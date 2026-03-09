# TEST 03 — LLM-as-Judge Evaluation Framework

## Objetivo

Substituir as heuristicas atuais de avaliacao (token overlap, regex, F1) por um
framework LLM-as-judge que usa Claude para avaliar faithfulness, factual accuracy
e grounding rate das respostas geradas, conforme descrito na Section 4.4 do paper.

## Contexto

O paper afirma:

> "Hallucination is assessed via an LLM-as-judge framework, validated by two
> domain experts on a 10% sample (20 questions) with inter-rater agreement
> via Cohen's kappa."

Atualmente, `run_experiments.py` usa metodos heuristicos:

- `_compute_faithfulness()`: token overlap entre response e context
- `_compute_factual_accuracy()`: F1 score com ground truth tokens
- `_compute_grounding_rate()`: regex para referencias regulatorias

Esses metodos nao correspondem ao que o paper descreve. Precisamos de um judge
baseado em LLM.

## Arquivos a criar

### 1. `simulacoes/scripts/llm_judge.py`

Modulo principal do framework LLM-as-judge.

```python
"""
LLM-as-Judge Evaluation Framework for GraphRAG.

Evaluates three dimensions of response quality using Claude as judge:
  1. Faithfulness: Are claims in the response grounded in the retrieved context?
  2. Factual Accuracy: Are claims factually correct per the ground truth?
  3. Grounding Rate: Does the response provide explicit source attribution?

References:
  - Zheng et al. (2023) "Judging LLM-as-a-Judge" (arXiv:2306.05685)
  - RAGAS evaluation framework
  - G-Eval (Liu et al., 2023)
"""

import json
import logging
from dataclasses import dataclass
from anthropic import Anthropic

logger = logging.getLogger(__name__)


@dataclass
class JudgeResult:
    """Result from a single LLM judge evaluation."""
    question_id: str
    system_name: str
    faithfulness_score: float       # 0.0 - 1.0
    factual_accuracy_score: float   # 0.0 - 1.0
    grounding_score: float          # 0.0 or 1.0 (binary)
    faithfulness_reasoning: str
    accuracy_reasoning: str
    grounding_reasoning: str
    judge_model: str
    judge_tokens_used: int


class LLMJudge:
    """Evaluates GraphRAG responses using Claude as judge."""

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        self.client = Anthropic()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_tokens_used = 0

    def evaluate_faithfulness(
        self,
        query: str,
        context: str,
        response: str,
    ) -> dict:
        """Evaluate whether claims in the response are grounded in context.

        Scoring:
          1.0 = All claims are fully supported by the retrieved context
          0.75 = Most claims supported, minor unsupported details
          0.5 = Mixed: some claims supported, some not
          0.25 = Most claims are not supported by context
          0.0 = Response contradicts or ignores the context entirely
        """
        prompt = f"""You are an expert evaluator assessing the faithfulness of a
response to its retrieved context. Faithfulness measures whether the claims
in the response are grounded in (supported by) the retrieved context.

## Query
{query}

## Retrieved Context
{context}

## Response to Evaluate
{response}

## Task
1. List each factual claim made in the response (numbered).
2. For each claim, determine if it is:
   - SUPPORTED: directly stated or logically implied by the context
   - PARTIALLY SUPPORTED: related information exists but details differ
   - NOT SUPPORTED: no basis in the context (potential hallucination)
3. Calculate the faithfulness score as:
   score = (SUPPORTED + 0.5 * PARTIALLY_SUPPORTED) / total_claims

## Output Format (JSON only)
{{
  "claims": [
    {{"claim": "...", "verdict": "SUPPORTED|PARTIALLY_SUPPORTED|NOT_SUPPORTED", "evidence": "..."}}
  ],
  "supported_count": <int>,
  "partial_count": <int>,
  "unsupported_count": <int>,
  "total_claims": <int>,
  "faithfulness_score": <float 0.0-1.0>,
  "reasoning": "<1-2 sentence summary>"
}}"""

        return self._call_judge(prompt)

    def evaluate_factual_accuracy(
        self,
        query: str,
        response: str,
        ground_truth: str,
        source_articles: list[str],
    ) -> dict:
        """Evaluate factual accuracy against expert-annotated ground truth.

        Scoring:
          1.0 = All key facts match the ground truth
          0.75 = Most facts correct, minor omissions
          0.5 = Partially correct, significant omissions or minor errors
          0.25 = Major factual errors present
          0.0 = Completely incorrect or irrelevant
        """
        articles_str = ", ".join(source_articles) if source_articles else "N/A"

        prompt = f"""You are an expert evaluator assessing the factual accuracy
of a response about financial regulation. Compare the response against the
expert-annotated ground truth.

## Query
{query}

## Ground Truth (Expert-Annotated)
{ground_truth}

## Relevant Source Articles
{articles_str}

## Response to Evaluate
{response}

## Task
1. Identify the key facts in the ground truth.
2. Check each fact against the response:
   - CORRECT: fact matches the ground truth
   - PARTIALLY CORRECT: related but imprecise or incomplete
   - INCORRECT: contradicts the ground truth
   - MISSING: fact not mentioned in the response
3. Calculate accuracy score.

## Output Format (JSON only)
{{
  "key_facts": [
    {{"fact": "...", "verdict": "CORRECT|PARTIALLY_CORRECT|INCORRECT|MISSING", "detail": "..."}}
  ],
  "correct_count": <int>,
  "partial_count": <int>,
  "incorrect_count": <int>,
  "missing_count": <int>,
  "total_facts": <int>,
  "factual_accuracy_score": <float 0.0-1.0>,
  "reasoning": "<1-2 sentence summary>"
}}"""

        return self._call_judge(prompt)

    def evaluate_grounding(
        self,
        response: str,
        expected_sources: list[str],
    ) -> dict:
        """Evaluate whether the response provides explicit source attribution.

        Binary scoring:
          1.0 = Response explicitly cites at least one regulatory source
                (article number, section, regulation name with specific reference)
          0.0 = No explicit source attribution found
        """
        sources_str = ", ".join(expected_sources) if expected_sources else "N/A"

        prompt = f"""You are an expert evaluator checking whether a response
about financial regulation provides explicit source attribution.

## Response to Evaluate
{response}

## Expected Source References
{sources_str}

## Task
Check if the response explicitly cites regulatory sources. Look for:
- Specific article numbers (e.g., "Art. 18", "Article 25", "Section 404")
- Regulation names with specifics (e.g., "Basel III Pillar 1", "LGPD Chapter VII")
- Resolution numbers (e.g., "Resolution 4.893", "Resolucao BCB 4893")
- Standard references (e.g., "BCBS 239", "CET1 requirement of 4.5%")

A vague mention like "according to regulations" does NOT count.
A specific citation like "under Basel III, the minimum CET1 ratio is 4.5%
(Pillar 1, paragraph 50)" DOES count.

## Output Format (JSON only)
{{
  "citations_found": [
    {{"citation": "...", "type": "article|section|regulation|standard", "specificity": "high|medium|low"}}
  ],
  "has_explicit_attribution": <bool>,
  "grounding_score": <float: 1.0 or 0.0>,
  "expected_sources_cited": <int out of total expected>,
  "reasoning": "<1-2 sentence summary>"
}}"""

        return self._call_judge(prompt)

    def evaluate_full(
        self,
        question_id: str,
        system_name: str,
        query: str,
        context: str,
        response: str,
        ground_truth: str,
        source_articles: list[str],
    ) -> JudgeResult:
        """Run all three evaluations for a single response."""

        faith = self.evaluate_faithfulness(query, context, response)
        accuracy = self.evaluate_factual_accuracy(
            query, response, ground_truth, source_articles
        )
        grounding = self.evaluate_grounding(response, source_articles)

        return JudgeResult(
            question_id=question_id,
            system_name=system_name,
            faithfulness_score=faith.get("faithfulness_score", 0.0),
            factual_accuracy_score=accuracy.get("factual_accuracy_score", 0.0),
            grounding_score=grounding.get("grounding_score", 0.0),
            faithfulness_reasoning=faith.get("reasoning", ""),
            accuracy_reasoning=accuracy.get("reasoning", ""),
            grounding_reasoning=grounding.get("reasoning", ""),
            judge_model=self.model,
            judge_tokens_used=self.total_tokens_used,
        )

    def _call_judge(self, prompt: str) -> dict:
        """Call Claude API and parse JSON response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        self.total_tokens_used += (
            response.usage.input_tokens + response.usage.output_tokens
        )

        text = response.content[0].text
        # Extract JSON from response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block in response
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"error": "Failed to parse judge response", "raw": text}
```

### 2. Modificar: `simulacoes/scripts/run_experiments.py`

Substituir os metodos heuristicos no Experiment 1:

```python
# ANTES (heuristico):
faithfulness = self._compute_faithfulness(response, context)

# DEPOIS (LLM judge):
from llm_judge import LLMJudge

judge = LLMJudge(model="claude-haiku-4-5-20251001")
result = judge.evaluate_faithfulness(query, context, response)
faithfulness = result["faithfulness_score"]
```

Adicionar flag `--judge-mode` ao CLI:

```bash
# Heuristico (rapido, gratis)
python run_experiments.py --experiment 1 --simulate

# LLM judge (mais preciso, custo API)
python run_experiments.py --experiment 1 --judge-mode llm

# LLM judge com modo live
python run_experiments.py --experiment 1 --judge-mode llm --live
```

### 3. `simulacoes/results/experiment_1_hallucination_judge.json`

Resultado com metadados do judge:

```json
{
  "experiment": "hallucination_evaluation",
  "judge_mode": "llm",
  "judge_model": "claude-haiku-4-5-20251001",
  "judge_temperature": 0.0,
  "total_judge_calls": 3000,
  "total_judge_tokens": 1500000,
  "total_judge_cost_usd": 1.35,
  "per_system": {
    "MultiStrategy_GraphRAG": {
      "faithfulness": {"mean": 0.8735, "std": 0.041, "median": 0.876},
      "factual_accuracy": {"mean": 0.8398, "std": 0.048},
      "grounding_rate": {"mean": 0.9638, "std": 0.019},
      "sample_judgments": [
        {
          "question_id": "q001",
          "faithfulness_score": 0.92,
          "claims_analyzed": 5,
          "supported": 4,
          "partial": 1,
          "unsupported": 0,
          "reasoning": "All capital requirement claims are directly supported..."
        }
      ]
    }
  }
}
```

## Estimativa de custos

| Item | Quantidade | Tokens/chamada | Custo (Haiku) |
|------|-----------|----------------|---------------|
| Faithfulness eval | 200 Q x 5 systems = 1,000 | ~800 input + 400 output | $1.20 |
| Factual accuracy eval | 200 Q x 5 systems = 1,000 | ~600 input + 300 output | $0.80 |
| Grounding eval | 200 Q x 5 systems = 1,000 | ~400 input + 200 output | $0.50 |
| **Total** | **3,000 chamadas** | | **~$2.50** |

Usando Batch API (50% desconto): **~$1.25**

## Validacao do judge

Para garantir que o LLM judge e confiavel:

### Calibracao com exemplos conhecidos

Criar 20 pares (response, context) com scores conhecidos:
- 5 casos com faithfulness = 1.0 (tudo suportado)
- 5 casos com faithfulness = 0.5 (misto)
- 5 casos com faithfulness = 0.0 (tudo alucinado)
- 5 casos edge (parcialmente corretos)

Verificar que o judge atribui scores dentro de +/- 0.15 do esperado.

### Consistencia (test-retest)

Rodar o judge 3x nos mesmos 20 exemplos e verificar:
- Correlacao de Pearson >= 0.90 entre runs
- Desvio padrao entre runs <= 0.10

### Concordancia com heuristicas

Comparar scores do LLM judge vs heuristicas atuais nos 200 questions:
- Correlacao de Spearman >= 0.70 (concordancia geral)
- Verificar divergencias sistematicas

## Dependencias

- API key Anthropic
- `datasets/regulatory_questions_200.json` (questions com ground truth)
- Respostas geradas por cada sistema (do Experiment 1 live ou simulado)

## Criterios de aceite

1. Judge retorna scores validos (0.0-1.0) para todas as 3,000 avaliacoes
2. Zero erros de parsing JSON nas respostas do judge
3. Calibracao: erro medio <= 0.15 nos 20 exemplos conhecidos
4. Consistencia: correlacao >= 0.90 entre runs repetidos
5. Custo total do judge <= $3.00
6. Tempo de execucao <= 30 minutos (com paralelismo)
7. Cada avaliacao inclui reasoning explicavel
