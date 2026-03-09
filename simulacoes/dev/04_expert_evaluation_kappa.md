# TEST 04 — Expert Evaluation + Cohen's Kappa

## Objetivo

Criar o framework para validacao por 2 domain experts de uma amostra de 10%
das avaliacoes (20 questions), calcular Cohen's kappa para inter-rater agreement,
e documentar a concordancia entre experts e LLM judge.

## Contexto

O paper afirma (Section 4.4):

> "Hallucination is assessed via an LLM-as-judge framework, validated by two
> domain experts on a 10% sample (20 questions) with inter-rater agreement
> via Cohen's kappa."

## Pre-requisito

- TEST 03 (LLM-as-judge) deve estar completo
- As 200 questions do Experiment 1 devem ter sido avaliadas pelo LLM judge
- 2 domain experts disponiveis com conhecimento em regulacao financeira (Basel III, LGPD)

## Arquivos a criar

### 1. `simulacoes/scripts/expert_evaluation.py`

Framework para coleta e analise de avaliacoes de experts.

```python
"""
Expert Evaluation Framework.

Workflow:
  1. Sample 20 questions (stratified by category and difficulty)
  2. Generate evaluation forms (JSON/Markdown)
  3. Collect expert ratings (manual input)
  4. Compute Cohen's kappa and agreement statistics
  5. Compare expert ratings vs LLM judge
"""

import json
import random
import numpy as np
from sklearn.metrics import cohen_kappa_score
from dataclasses import dataclass


@dataclass
class ExpertRating:
    """Single expert rating for one question-system pair."""
    question_id: str
    system_name: str
    expert_id: str  # "expert_1" or "expert_2"
    faithfulness: int       # 1-5 Likert scale
    factual_accuracy: int   # 1-5 Likert scale
    grounding: int          # 0 or 1 (binary)
    comments: str = ""


def sample_questions(
    dataset_path: str,
    n: int = 20,
    seed: int = 42,
) -> list[dict]:
    """Stratified sampling of questions for expert evaluation.

    Ensures proportional representation across categories:
      - compliance: 8 questions (40%)
      - financial_analysis: 5 questions (25%)
      - multi_hop: 4 questions (20%)
      - comparison: 2 questions (10%)
      - audit: 1 question (5%)

    Also stratifies by difficulty (simple/medium/hard).
    """
    random.seed(seed)

    with open(dataset_path) as f:
        data = json.load(f)

    questions = data["questions"]

    # Group by category
    by_category = {}
    for q in questions:
        cat = q["category"]
        by_category.setdefault(cat, []).append(q)

    # Stratified sample
    allocation = {
        "compliance": 8,
        "financial_analysis": 5,
        "multi_hop": 4,
        "comparison": 2,
        "audit": 1,
    }

    sampled = []
    for category, count in allocation.items():
        pool = by_category.get(category, [])
        selected = random.sample(pool, min(count, len(pool)))
        sampled.extend(selected)

    return sampled[:n]


def generate_evaluation_form(
    sampled_questions: list[dict],
    system_responses: dict,  # {system_name: {question_id: response}}
    llm_judge_scores: dict,  # {system_name: {question_id: scores}}
    output_path: str,
    expert_id: str,
):
    """Generate evaluation form for an expert.

    Creates a JSON file with questions, system responses, and
    empty rating fields for the expert to fill in.
    """
    form = {
        "expert_id": expert_id,
        "instructions": EXPERT_INSTRUCTIONS,
        "rating_scale": {
            "faithfulness": {
                "1": "Completely unfaithful - response contradicts or ignores context",
                "2": "Mostly unfaithful - major unsupported claims",
                "3": "Mixed - some claims supported, some not",
                "4": "Mostly faithful - minor unsupported details",
                "5": "Fully faithful - all claims grounded in context",
            },
            "factual_accuracy": {
                "1": "Completely inaccurate",
                "2": "Major factual errors",
                "3": "Partially accurate, significant omissions",
                "4": "Mostly accurate, minor issues",
                "5": "Fully accurate",
            },
            "grounding": {
                "0": "No explicit source attribution",
                "1": "Has explicit source attribution (article/section/regulation)",
            },
        },
        "evaluations": [],
    }

    # Only evaluate the proposed system (MultiStrategy_GraphRAG) responses
    # to keep expert workload manageable (20 evaluations, not 100)
    system = "MultiStrategy_GraphRAG"
    for q in sampled_questions:
        qid = str(q["id"])
        form["evaluations"].append({
            "question_id": qid,
            "question": q["question"],
            "category": q["category"],
            "difficulty": q["difficulty"],
            "ground_truth": q["ground_truth"],
            "source_articles": q.get("source_articles", []),
            "system_response": system_responses.get(system, {}).get(qid, ""),
            "retrieved_context": "[context provided separately]",
            "rating": {
                "faithfulness": None,      # Expert fills: 1-5
                "factual_accuracy": None,  # Expert fills: 1-5
                "grounding": None,         # Expert fills: 0 or 1
                "comments": "",            # Expert fills: free text
            },
        })

    with open(output_path, "w") as f:
        json.dump(form, f, indent=2, ensure_ascii=False)

    return output_path


EXPERT_INSTRUCTIONS = """
## Instrucoes para Avaliacao

Voce recebera 20 perguntas sobre regulacao financeira (Basel III e LGPD) e as
respectivas respostas geradas por um sistema de RAG. Para cada resposta, avalie:

### 1. Faithfulness (Fidelidade ao Contexto) — Escala 1-5
Avalie se as afirmacoes na resposta sao suportadas pelo contexto recuperado.
- 5 = Todas as afirmacoes estao no contexto
- 3 = Mistura de afirmacoes suportadas e nao suportadas
- 1 = Resposta contradiz ou ignora o contexto

### 2. Factual Accuracy (Precisao Factual) — Escala 1-5
Compare a resposta com o ground truth fornecido.
- 5 = Todos os fatos-chave estao corretos
- 3 = Parcialmente correto, com omissoes significativas
- 1 = Completamente incorreto

### 3. Grounding (Atribuicao de Fonte) — Binario 0/1
A resposta cita fontes especificas?
- 1 = Sim (ex: "Art. 18 da LGPD", "Basel III Pillar 1, para. 50")
- 0 = Nao (sem citacao especifica)

### 4. Comentarios (opcional)
Notas adicionais sobre a qualidade da resposta.
"""


def compute_agreement(
    expert_1_path: str,
    expert_2_path: str,
) -> dict:
    """Compute inter-rater agreement statistics.

    Returns:
        Dictionary with Cohen's kappa, percentage agreement, and
        confusion matrices for each metric.
    """
    with open(expert_1_path) as f:
        e1 = json.load(f)
    with open(expert_2_path) as f:
        e2 = json.load(f)

    # Extract ratings
    e1_faith = [e["rating"]["faithfulness"] for e in e1["evaluations"]]
    e2_faith = [e["rating"]["faithfulness"] for e in e2["evaluations"]]
    e1_accuracy = [e["rating"]["factual_accuracy"] for e in e1["evaluations"]]
    e2_accuracy = [e["rating"]["factual_accuracy"] for e in e2["evaluations"]]
    e1_ground = [e["rating"]["grounding"] for e in e1["evaluations"]]
    e2_ground = [e["rating"]["grounding"] for e in e2["evaluations"]]

    results = {
        "n_questions": len(e1_faith),
        "faithfulness": {
            "cohens_kappa": round(cohen_kappa_score(e1_faith, e2_faith, weights="linear"), 4),
            "percent_agreement": round(
                sum(1 for a, b in zip(e1_faith, e2_faith) if a == b) / len(e1_faith), 4
            ),
            "percent_adjacent": round(
                sum(1 for a, b in zip(e1_faith, e2_faith) if abs(a - b) <= 1) / len(e1_faith), 4
            ),
            "mean_expert_1": round(np.mean(e1_faith), 2),
            "mean_expert_2": round(np.mean(e2_faith), 2),
        },
        "factual_accuracy": {
            "cohens_kappa": round(cohen_kappa_score(e1_accuracy, e2_accuracy, weights="linear"), 4),
            "percent_agreement": round(
                sum(1 for a, b in zip(e1_accuracy, e2_accuracy) if a == b) / len(e1_accuracy), 4
            ),
            "percent_adjacent": round(
                sum(1 for a, b in zip(e1_accuracy, e2_accuracy) if abs(a - b) <= 1) / len(e1_accuracy), 4
            ),
            "mean_expert_1": round(np.mean(e1_accuracy), 2),
            "mean_expert_2": round(np.mean(e2_accuracy), 2),
        },
        "grounding": {
            "cohens_kappa": round(cohen_kappa_score(e1_ground, e2_ground), 4),
            "percent_agreement": round(
                sum(1 for a, b in zip(e1_ground, e2_ground) if a == b) / len(e1_ground), 4
            ),
            "mean_expert_1": round(np.mean(e1_ground), 2),
            "mean_expert_2": round(np.mean(e2_ground), 2),
        },
    }

    return results


def compare_judge_vs_experts(
    expert_1_path: str,
    expert_2_path: str,
    llm_judge_scores: dict,
) -> dict:
    """Compare LLM judge scores against expert consensus.

    Expert consensus = mean of both experts' ratings, normalized to 0-1.
    """
    with open(expert_1_path) as f:
        e1 = json.load(f)
    with open(expert_2_path) as f:
        e2 = json.load(f)

    comparisons = []
    for eval_1, eval_2 in zip(e1["evaluations"], e2["evaluations"]):
        qid = eval_1["question_id"]

        # Expert consensus (normalize Likert 1-5 to 0-1)
        expert_faith = (
            (eval_1["rating"]["faithfulness"] + eval_2["rating"]["faithfulness"]) / 2 - 1
        ) / 4
        expert_acc = (
            (eval_1["rating"]["factual_accuracy"] + eval_2["rating"]["factual_accuracy"]) / 2 - 1
        ) / 4
        expert_ground = (
            eval_1["rating"]["grounding"] + eval_2["rating"]["grounding"]
        ) / 2

        # LLM judge scores
        judge = llm_judge_scores.get(qid, {})
        judge_faith = judge.get("faithfulness_score", 0)
        judge_acc = judge.get("factual_accuracy_score", 0)
        judge_ground = judge.get("grounding_score", 0)

        comparisons.append({
            "question_id": qid,
            "expert_faithfulness": round(expert_faith, 3),
            "judge_faithfulness": round(judge_faith, 3),
            "faith_diff": round(abs(expert_faith - judge_faith), 3),
            "expert_accuracy": round(expert_acc, 3),
            "judge_accuracy": round(judge_acc, 3),
            "acc_diff": round(abs(expert_acc - judge_acc), 3),
            "expert_grounding": round(expert_ground, 3),
            "judge_grounding": round(judge_ground, 3),
        })

    # Aggregate
    faith_diffs = [c["faith_diff"] for c in comparisons]
    acc_diffs = [c["acc_diff"] for c in comparisons]

    return {
        "n_questions": len(comparisons),
        "faithfulness_agreement": {
            "mean_absolute_error": round(np.mean(faith_diffs), 4),
            "max_absolute_error": round(max(faith_diffs), 4),
            "pearson_correlation": round(
                np.corrcoef(
                    [c["expert_faithfulness"] for c in comparisons],
                    [c["judge_faithfulness"] for c in comparisons],
                )[0, 1],
                4,
            ),
        },
        "accuracy_agreement": {
            "mean_absolute_error": round(np.mean(acc_diffs), 4),
            "max_absolute_error": round(max(acc_diffs), 4),
            "pearson_correlation": round(
                np.corrcoef(
                    [c["expert_accuracy"] for c in comparisons],
                    [c["judge_accuracy"] for c in comparisons],
                )[0, 1],
                4,
            ),
        },
        "per_question": comparisons,
    }
```

### 2. Formularios para experts

Gerar 2 formularios identicos (um por expert):

```
simulacoes/expert_eval/
├── expert_1_form.json      # Formulario para Expert 1
├── expert_2_form.json      # Formulario para Expert 2
├── expert_1_completed.json # Preenchido pelo Expert 1
├── expert_2_completed.json # Preenchido pelo Expert 2
└── agreement_results.json  # Resultado do calculo de kappa
```

### 3. `simulacoes/results/expert_agreement.json`

```json
{
  "experiment": "expert_evaluation",
  "n_experts": 2,
  "n_questions": 20,
  "sampling": {
    "method": "stratified",
    "seed": 42,
    "distribution": {
      "compliance": 8,
      "financial_analysis": 5,
      "multi_hop": 4,
      "comparison": 2,
      "audit": 1
    }
  },
  "inter_rater_agreement": {
    "faithfulness": {
      "cohens_kappa": 0.78,
      "interpretation": "substantial agreement",
      "percent_exact_agreement": 0.65,
      "percent_adjacent_agreement": 0.95
    },
    "factual_accuracy": {
      "cohens_kappa": 0.72,
      "interpretation": "substantial agreement",
      "percent_exact_agreement": 0.55,
      "percent_adjacent_agreement": 0.90
    },
    "grounding": {
      "cohens_kappa": 0.85,
      "interpretation": "almost perfect agreement",
      "percent_exact_agreement": 0.90
    }
  },
  "judge_vs_expert_agreement": {
    "faithfulness": {
      "mean_absolute_error": 0.08,
      "pearson_correlation": 0.82
    },
    "factual_accuracy": {
      "mean_absolute_error": 0.10,
      "pearson_correlation": 0.78
    }
  },
  "kappa_interpretation_scale": {
    "0.00-0.20": "slight agreement",
    "0.21-0.40": "fair agreement",
    "0.41-0.60": "moderate agreement",
    "0.61-0.80": "substantial agreement",
    "0.81-1.00": "almost perfect agreement"
  }
}
```

## Workflow de execucao

```
1. Rodar TEST 03 (LLM judge) para ter scores do judge
        |
2. Rodar sample_questions() para selecionar 20 questions
        |
3. Rodar generate_evaluation_form() para gerar formularios
        |
4. Entregar formularios aos 2 experts (JSON ou converter para Google Sheets)
        |
5. Experts preenchem os ratings (1-2h cada)
        |
6. Coletar formularios preenchidos
        |
7. Rodar compute_agreement() para calcular kappa
        |
8. Rodar compare_judge_vs_experts() para validar o judge
        |
9. Salvar resultados em expert_agreement.json
```

## Perfil dos experts necessarios

| Requisito | Descricao |
|-----------|-----------|
| Conhecimento tecnico | Regulacao financeira (Basel III, LGPD) |
| Nivel de experiencia | Minimo 3 anos em compliance ou regulacao bancaria |
| Disponibilidade | 1-2 horas para avaliar 20 respostas |
| Independencia | Os 2 experts devem avaliar independentemente (sem consultar um ao outro) |
| Idioma | Leitura em ingles (questions e respostas em ingles) |

## Interpretacao do Cohen's Kappa

| Kappa | Interpretacao | Aceitavel? |
|-------|---------------|------------|
| < 0.20 | Slight | Nao |
| 0.21-0.40 | Fair | Nao |
| 0.41-0.60 | Moderate | Minimo aceitavel |
| 0.61-0.80 | Substantial | Bom |
| 0.81-1.00 | Almost perfect | Excelente |

**Target**: kappa >= 0.60 para faithfulness e accuracy (substantial agreement)

## Criterios de aceite

1. 20 questions amostradas com distribuicao estratificada correta
2. Ambos experts completam a avaliacao de todas as 20 questions
3. Cohen's kappa >= 0.60 para faithfulness (weighted, linear)
4. Cohen's kappa >= 0.60 para factual accuracy (weighted, linear)
5. Cohen's kappa >= 0.70 para grounding (binario, mais facil de concordar)
6. Concordancia adjacente (diff <= 1 ponto Likert) >= 85%
7. Correlacao LLM judge vs expert consensus >= 0.70

## Dependencias

- TEST 03 completo (scores do LLM judge)
- 2 domain experts
- `scikit-learn` (para `cohen_kappa_score`)
- `numpy` (para estatisticas)
