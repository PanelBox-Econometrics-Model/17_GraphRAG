#!/usr/bin/env python3
"""Expert Evaluation Framework + Cohen's Kappa.

Workflow:
    1. Sample 20 questions (stratified by category and difficulty)
    2. Generate evaluation forms (JSON) for 2 domain experts
    3. Collect expert ratings (manual input or simulated)
    4. Compute Cohen's kappa and agreement statistics
    5. Compare expert ratings vs LLM judge

Usage:
    # Generate evaluation forms
    python expert_evaluation.py --generate-forms

    # Generate simulated expert ratings (for testing pipeline)
    python expert_evaluation.py --simulate-experts

    # Compute agreement from completed forms
    python expert_evaluation.py --compute-agreement

    # Compare LLM judge vs experts
    python expert_evaluation.py --compare-judge

    # Full pipeline (simulate + compute)
    python expert_evaluation.py --simulate-experts --compute-agreement --compare-judge
"""

import argparse
import json
import logging
import os
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import cohen_kappa_score

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPERT_INSTRUCTIONS = """## Instrucoes para Avaliacao

Voce recebera 20 perguntas sobre regulacao financeira (Basel III e LGPD) e as
respectivas respostas geradas por um sistema de RAG. Para cada resposta, avalie:

### 1. Faithfulness (Fidelidade ao Contexto) — Escala 1-5
Avalie se as afirmacoes na resposta sao suportadas pelo contexto recuperado.
- 5 = Todas as afirmacoes estao no contexto
- 4 = Maioria suportada, detalhes menores nao suportados
- 3 = Mistura de afirmacoes suportadas e nao suportadas
- 2 = Maioria nao suportada
- 1 = Resposta contradiz ou ignora o contexto

### 2. Factual Accuracy (Precisao Factual) — Escala 1-5
Compare a resposta com o ground truth fornecido.
- 5 = Todos os fatos-chave estao corretos
- 4 = Maioria correta, omissoes menores
- 3 = Parcialmente correto, com omissoes significativas
- 2 = Erros factuais relevantes
- 1 = Completamente incorreto

### 3. Grounding (Atribuicao de Fonte) — Binario 0/1
A resposta cita fontes especificas?
- 1 = Sim (ex: "Art. 18 da LGPD", "Basel III Pillar 1, para. 50")
- 0 = Nao (sem citacao especifica)

### 4. Comentarios (opcional)
Notas adicionais sobre a qualidade da resposta.
"""

STRATIFIED_ALLOCATION = {
    "compliance": 8,
    "financial_analysis": 5,
    "multi_hop": 4,
    "comparison": 2,
    "audit": 1,
}

KAPPA_INTERPRETATION = {
    "0.00-0.20": "slight agreement",
    "0.21-0.40": "fair agreement",
    "0.41-0.60": "moderate agreement",
    "0.61-0.80": "substantial agreement",
    "0.81-1.00": "almost perfect agreement",
}


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_questions(
    dataset_path: str,
    n: int = 20,
    seed: int = 42,
) -> list[dict]:
    """Stratified sampling of questions for expert evaluation.

    Ensures proportional representation across categories:
        compliance: 8 (40%), financial_analysis: 5 (25%),
        multi_hop: 4 (20%), comparison: 2 (10%), audit: 1 (5%)

    Args:
        dataset_path: Path to the questions JSON file.
        n: Total number of questions to sample.
        seed: Random seed for reproducibility.

    Returns:
        List of sampled question dictionaries.
    """
    random.seed(seed)

    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", data if isinstance(data, list) else [])

    # Group by category
    by_category: dict[str, list[dict]] = {}
    for q in questions:
        cat = q.get("category", "unknown")
        by_category.setdefault(cat, []).append(q)

    sampled = []
    for category, count in STRATIFIED_ALLOCATION.items():
        pool = by_category.get(category, [])
        if pool:
            selected = random.sample(pool, min(count, len(pool)))
            sampled.extend(selected)

    # Trim to exactly n
    return sampled[:n]


# ---------------------------------------------------------------------------
# Form generation
# ---------------------------------------------------------------------------

def generate_evaluation_form(
    sampled_questions: list[dict],
    output_path: str,
    expert_id: str,
) -> str:
    """Generate evaluation form for an expert.

    Creates a JSON file with questions, rating scale definitions,
    and empty rating fields for the expert to fill in.

    Args:
        sampled_questions: List of sampled question dictionaries.
        output_path: Path to save the form JSON.
        expert_id: Expert identifier ("expert_1" or "expert_2").

    Returns:
        Path to the saved form.
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

    for q in sampled_questions:
        qid = str(q["id"])
        form["evaluations"].append({
            "question_id": qid,
            "question": q.get("question", ""),
            "category": q.get("category", "unknown"),
            "difficulty": q.get("difficulty", "moderate"),
            "ground_truth": q.get("ground_truth", ""),
            "source_articles": q.get("source_articles", []),
            "system_response": "[response would be filled from experiment results]",
            "rating": {
                "faithfulness": None,
                "factual_accuracy": None,
                "grounding": None,
                "comments": "",
            },
        })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(form, f, indent=2, ensure_ascii=False)

    logger.info("Evaluation form saved to %s (%d questions)", output_path, len(form["evaluations"]))
    return output_path


# ---------------------------------------------------------------------------
# Simulated expert ratings
# ---------------------------------------------------------------------------

def generate_simulated_expert_ratings(
    form_path: str,
    output_path: str,
    expert_id: str,
    seed: int = 42,
    bias: float = 0.0,
) -> str:
    """Generate simulated expert ratings for testing the pipeline.

    Produces ratings with controlled inter-rater agreement (kappa ~0.75).
    Expert 2 gets a small bias to simulate realistic disagreement.

    Args:
        form_path: Path to the empty evaluation form JSON.
        output_path: Path to save the completed form.
        expert_id: Expert identifier.
        seed: Random seed.
        bias: Score bias for this expert (-0.3 to +0.3).

    Returns:
        Path to the saved completed form.
    """
    rng = np.random.default_rng(seed)

    with open(form_path, encoding="utf-8") as f:
        form = json.load(f)

    form["expert_id"] = expert_id

    # Use a FIXED seed (42) for latent quality so both experts share the same
    # underlying question quality. Expert-specific noise uses the expert's seed.
    latent_rng = np.random.default_rng(42)
    n_questions = len(form["evaluations"])

    # Latent quality per question (shared between experts)
    latent_faith = latent_rng.normal(3.8, 0.9, size=n_questions)
    latent_acc = latent_rng.normal(3.6, 1.0, size=n_questions)
    latent_ground = latent_rng.random(size=n_questions)  # for grounding

    for i, evaluation in enumerate(form["evaluations"]):
        category = evaluation.get("category", "compliance")
        difficulty = evaluation.get("difficulty", "moderate")

        # Adjust by difficulty
        diff_adjust = {
            "simple": 0.4,
            "moderate": 0.0,
            "complex": -0.5,
            "multi_hop": -0.8,
        }.get(difficulty, 0.0)

        # Expert-specific noise on top of shared latent quality
        # Small noise (std=0.4) produces kappa ~0.65-0.80
        faith_raw = latent_faith[i] + diff_adjust + bias + rng.normal(0, 0.4)
        faithfulness = int(np.clip(round(faith_raw), 1, 5))

        acc_raw = latent_acc[i] + diff_adjust + bias + rng.normal(0, 0.45)
        factual_accuracy = int(np.clip(round(acc_raw), 1, 5))

        # Grounding: shared latent determines base, expert adds small noise
        grounding_threshold = 0.15  # ~85% grounded
        ground_noise = rng.normal(0, 0.05)
        grounding = 1 if (latent_ground[i] + ground_noise) > grounding_threshold else 0

        evaluation["rating"] = {
            "faithfulness": faithfulness,
            "factual_accuracy": factual_accuracy,
            "grounding": grounding,
            "comments": f"[Simulated by {expert_id}]",
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(form, f, indent=2, ensure_ascii=False)

    logger.info("Simulated ratings saved to %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# Agreement computation
# ---------------------------------------------------------------------------

def compute_agreement(
    expert_1_path: str,
    expert_2_path: str,
) -> dict:
    """Compute inter-rater agreement statistics between two experts.

    Calculates:
        - Cohen's kappa (linear weighted for Likert, unweighted for binary)
        - Percentage exact agreement
        - Percentage adjacent agreement (within 1 point on Likert)
        - Mean ratings per expert

    Args:
        expert_1_path: Path to completed Expert 1 form JSON.
        expert_2_path: Path to completed Expert 2 form JSON.

    Returns:
        Dictionary with agreement statistics per metric.
    """
    with open(expert_1_path, encoding="utf-8") as f:
        e1 = json.load(f)
    with open(expert_2_path, encoding="utf-8") as f:
        e2 = json.load(f)

    # Extract ratings
    e1_faith = [e["rating"]["faithfulness"] for e in e1["evaluations"]]
    e2_faith = [e["rating"]["faithfulness"] for e in e2["evaluations"]]
    e1_accuracy = [e["rating"]["factual_accuracy"] for e in e1["evaluations"]]
    e2_accuracy = [e["rating"]["factual_accuracy"] for e in e2["evaluations"]]
    e1_ground = [e["rating"]["grounding"] for e in e1["evaluations"]]
    e2_ground = [e["rating"]["grounding"] for e in e2["evaluations"]]

    n = len(e1_faith)

    results = {
        "n_questions": n,
        "faithfulness": {
            "cohens_kappa": round(cohen_kappa_score(e1_faith, e2_faith, weights="linear"), 4),
            "percent_exact_agreement": round(
                sum(1 for a, b in zip(e1_faith, e2_faith) if a == b) / n, 4
            ),
            "percent_adjacent_agreement": round(
                sum(1 for a, b in zip(e1_faith, e2_faith) if abs(a - b) <= 1) / n, 4
            ),
            "mean_expert_1": round(float(np.mean(e1_faith)), 2),
            "mean_expert_2": round(float(np.mean(e2_faith)), 2),
        },
        "factual_accuracy": {
            "cohens_kappa": round(cohen_kappa_score(e1_accuracy, e2_accuracy, weights="linear"), 4),
            "percent_exact_agreement": round(
                sum(1 for a, b in zip(e1_accuracy, e2_accuracy) if a == b) / n, 4
            ),
            "percent_adjacent_agreement": round(
                sum(1 for a, b in zip(e1_accuracy, e2_accuracy) if abs(a - b) <= 1) / n, 4
            ),
            "mean_expert_1": round(float(np.mean(e1_accuracy)), 2),
            "mean_expert_2": round(float(np.mean(e2_accuracy)), 2),
        },
        "grounding": {
            "cohens_kappa": round(cohen_kappa_score(e1_ground, e2_ground), 4),
            "percent_exact_agreement": round(
                sum(1 for a, b in zip(e1_ground, e2_ground) if a == b) / n, 4
            ),
            "mean_expert_1": round(float(np.mean(e1_ground)), 2),
            "mean_expert_2": round(float(np.mean(e2_ground)), 2),
        },
    }

    # Add interpretation for each kappa
    for metric in ["faithfulness", "factual_accuracy", "grounding"]:
        kappa = results[metric]["cohens_kappa"]
        results[metric]["interpretation"] = _interpret_kappa(kappa)

    return results


def _interpret_kappa(kappa: float) -> str:
    """Interpret Cohen's kappa value.

    Args:
        kappa: Cohen's kappa score.

    Returns:
        Interpretation string.
    """
    if kappa < 0.0:
        return "less than chance agreement"
    elif kappa < 0.21:
        return "slight agreement"
    elif kappa < 0.41:
        return "fair agreement"
    elif kappa < 0.61:
        return "moderate agreement"
    elif kappa < 0.81:
        return "substantial agreement"
    else:
        return "almost perfect agreement"


# ---------------------------------------------------------------------------
# Judge vs Expert comparison
# ---------------------------------------------------------------------------

def compare_judge_vs_experts(
    expert_1_path: str,
    expert_2_path: str,
    judge_scores_path: str | None = None,
) -> dict:
    """Compare LLM judge scores against expert consensus.

    Expert consensus = mean of both experts' ratings, normalized to 0-1.

    Args:
        expert_1_path: Path to completed Expert 1 form.
        expert_2_path: Path to completed Expert 2 form.
        judge_scores_path: Path to LLM judge results JSON. If None, uses
            simulated judge scores.

    Returns:
        Dictionary with comparison statistics.
    """
    with open(expert_1_path, encoding="utf-8") as f:
        e1 = json.load(f)
    with open(expert_2_path, encoding="utf-8") as f:
        e2 = json.load(f)

    # Load or simulate judge scores
    judge_scores = {}
    if judge_scores_path and os.path.exists(judge_scores_path):
        with open(judge_scores_path, encoding="utf-8") as f:
            judge_data = json.load(f)
        # Extract per-question scores from judge results
        per_system = judge_data.get("results", {}).get("per_system", {})
        ms_graphrag = per_system.get("MultiStrategy_GraphRAG", {})
        # Use system-level means as proxy (per-question not always available)
        default_faith = ms_graphrag.get("faithfulness", {}).get("mean", 0.87)
        default_acc = ms_graphrag.get("factual_accuracy", {}).get("mean", 0.84)
        default_ground = ms_graphrag.get("grounding_rate", {}).get("mean", 0.96)
        for eval_item in e1["evaluations"]:
            qid = eval_item["question_id"]
            judge_scores[qid] = {
                "faithfulness_score": default_faith,
                "factual_accuracy_score": default_acc,
                "grounding_score": default_ground,
            }
    else:
        # Generate simulated judge scores
        rng = np.random.default_rng(42)
        for eval_item in e1["evaluations"]:
            qid = eval_item["question_id"]
            judge_scores[qid] = {
                "faithfulness_score": float(np.clip(rng.normal(0.87, 0.04), 0, 1)),
                "factual_accuracy_score": float(np.clip(rng.normal(0.84, 0.05), 0, 1)),
                "grounding_score": 1.0 if rng.random() < 0.96 else 0.0,
            }

    comparisons = []
    for eval_1, eval_2 in zip(e1["evaluations"], e2["evaluations"]):
        qid = eval_1["question_id"]

        # Expert consensus: normalize Likert 1-5 to 0-1
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
        judge = judge_scores.get(qid, {})
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

    expert_faith_vals = [c["expert_faithfulness"] for c in comparisons]
    judge_faith_vals = [c["judge_faithfulness"] for c in comparisons]
    expert_acc_vals = [c["expert_accuracy"] for c in comparisons]
    judge_acc_vals = [c["judge_accuracy"] for c in comparisons]

    # Pearson correlation (handle edge case of constant arrays)
    def _safe_pearson(a: list, b: list) -> float:
        if len(set(a)) <= 1 or len(set(b)) <= 1:
            return 1.0 if a == b else 0.0
        return float(np.corrcoef(a, b)[0, 1])

    return {
        "n_questions": len(comparisons),
        "faithfulness_agreement": {
            "mean_absolute_error": round(float(np.mean(faith_diffs)), 4),
            "max_absolute_error": round(float(max(faith_diffs)), 4),
            "pearson_correlation": round(_safe_pearson(expert_faith_vals, judge_faith_vals), 4),
        },
        "accuracy_agreement": {
            "mean_absolute_error": round(float(np.mean(acc_diffs)), 4),
            "max_absolute_error": round(float(max(acc_diffs)), 4),
            "pearson_correlation": round(_safe_pearson(expert_acc_vals, judge_acc_vals), 4),
        },
        "per_question": comparisons,
    }


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_full_pipeline(
    datasets_dir: str,
    expert_eval_dir: str,
    results_dir: str,
    seed: int = 42,
    generate_forms: bool = False,
    simulate_experts: bool = False,
    compute_kappa: bool = False,
    compare_with_judge: bool = False,
    judge_results_path: str | None = None,
) -> dict:
    """Run the full expert evaluation pipeline.

    Args:
        datasets_dir: Path to datasets directory.
        expert_eval_dir: Path to expert evaluation directory.
        results_dir: Path to results directory.
        seed: Random seed.
        generate_forms: Whether to generate evaluation forms.
        simulate_experts: Whether to generate simulated expert ratings.
        compute_kappa: Whether to compute Cohen's kappa.
        compare_with_judge: Whether to compare with LLM judge.
        judge_results_path: Path to LLM judge results.

    Returns:
        Dictionary with all pipeline results.
    """
    results = {}
    dataset_path = os.path.join(datasets_dir, "regulatory_questions_200.json")

    # Step 1: Sample questions
    sampled = sample_questions(dataset_path, n=20, seed=seed)
    logger.info("Sampled %d questions for expert evaluation", len(sampled))

    # Log distribution
    cat_counts = {}
    for q in sampled:
        cat = q.get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    logger.info("Category distribution: %s", cat_counts)

    results["sampling"] = {
        "method": "stratified",
        "seed": seed,
        "n_questions": len(sampled),
        "distribution": cat_counts,
    }

    # Step 2: Generate forms
    if generate_forms or simulate_experts:
        form_1_path = os.path.join(expert_eval_dir, "expert_1_form.json")
        form_2_path = os.path.join(expert_eval_dir, "expert_2_form.json")

        generate_evaluation_form(sampled, form_1_path, "expert_1")
        generate_evaluation_form(sampled, form_2_path, "expert_2")

        results["forms_generated"] = [form_1_path, form_2_path]

    # Step 3: Simulate expert ratings
    if simulate_experts:
        e1_completed = os.path.join(expert_eval_dir, "expert_1_completed.json")
        e2_completed = os.path.join(expert_eval_dir, "expert_2_completed.json")

        generate_simulated_expert_ratings(
            form_1_path, e1_completed, "expert_1", seed=seed, bias=0.0
        )
        generate_simulated_expert_ratings(
            form_2_path, e2_completed, "expert_2", seed=seed + 1, bias=-0.2
        )

        results["simulated_ratings"] = [e1_completed, e2_completed]

    # Step 4: Compute agreement
    if compute_kappa:
        e1_completed = os.path.join(expert_eval_dir, "expert_1_completed.json")
        e2_completed = os.path.join(expert_eval_dir, "expert_2_completed.json")

        if not os.path.exists(e1_completed) or not os.path.exists(e2_completed):
            logger.error("Completed forms not found. Run --simulate-experts first.")
            return results

        agreement = compute_agreement(e1_completed, e2_completed)
        results["inter_rater_agreement"] = agreement

        # Save agreement results
        agreement_path = os.path.join(expert_eval_dir, "agreement_results.json")
        with open(agreement_path, "w", encoding="utf-8") as f:
            json.dump(agreement, f, indent=2, ensure_ascii=False)
        logger.info("Agreement results saved to %s", agreement_path)

        # Print summary
        print("\n" + "=" * 60)
        print("  Inter-Rater Agreement (Cohen's Kappa)")
        print("=" * 60)
        for metric in ["faithfulness", "factual_accuracy", "grounding"]:
            m = agreement[metric]
            print(f"  {metric}:")
            print(f"    kappa = {m['cohens_kappa']:.4f} ({m['interpretation']})")
            print(f"    exact agreement = {m['percent_exact_agreement']:.0%}")
            if "percent_adjacent_agreement" in m:
                print(f"    adjacent agreement = {m['percent_adjacent_agreement']:.0%}")
            print(f"    Expert 1 mean = {m['mean_expert_1']:.2f}, Expert 2 mean = {m['mean_expert_2']:.2f}")
        print()

    # Step 5: Compare with judge
    if compare_with_judge:
        e1_completed = os.path.join(expert_eval_dir, "expert_1_completed.json")
        e2_completed = os.path.join(expert_eval_dir, "expert_2_completed.json")

        comparison = compare_judge_vs_experts(
            e1_completed, e2_completed, judge_results_path
        )
        results["judge_vs_expert_agreement"] = {
            "n_questions": comparison["n_questions"],
            "faithfulness": comparison["faithfulness_agreement"],
            "factual_accuracy": comparison["accuracy_agreement"],
        }

        # Print summary
        print("\n" + "=" * 60)
        print("  LLM Judge vs Expert Agreement")
        print("=" * 60)
        for metric, key in [("faithfulness", "faithfulness_agreement"), ("accuracy", "accuracy_agreement")]:
            m = comparison[key]
            print(f"  {metric}:")
            print(f"    MAE = {m['mean_absolute_error']:.4f}")
            print(f"    Pearson r = {m['pearson_correlation']:.4f}")
        print()

    # Save full results
    full_results = {
        "experiment": "expert_evaluation",
        "n_experts": 2,
        "n_questions": 20,
        **results,
        "kappa_interpretation_scale": KAPPA_INTERPRETATION,
    }

    results_path = os.path.join(results_dir, "expert_agreement.json")
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    logger.info("Full results saved to %s", results_path)

    return full_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """Entry point for expert evaluation pipeline."""
    parser = argparse.ArgumentParser(
        description="Expert Evaluation Framework + Cohen's Kappa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--generate-forms",
        action="store_true",
        help="Generate evaluation forms for experts",
    )
    parser.add_argument(
        "--simulate-experts",
        action="store_true",
        help="Generate simulated expert ratings (for testing)",
    )
    parser.add_argument(
        "--compute-agreement",
        action="store_true",
        help="Compute Cohen's kappa from completed forms",
    )
    parser.add_argument(
        "--compare-judge",
        action="store_true",
        help="Compare LLM judge scores vs expert consensus",
    )
    parser.add_argument(
        "--judge-results",
        type=str,
        default=None,
        help="Path to LLM judge results JSON (for --compare-judge)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    base_dir = Path(__file__).resolve().parent.parent
    datasets_dir = str(base_dir / "datasets")
    expert_eval_dir = str(base_dir / "expert_eval")
    results_dir = str(base_dir / "results")

    # Default: if no flags, run everything
    if not any([args.generate_forms, args.simulate_experts, args.compute_agreement, args.compare_judge]):
        args.generate_forms = True
        args.simulate_experts = True
        args.compute_agreement = True
        args.compare_judge = True

    run_full_pipeline(
        datasets_dir=datasets_dir,
        expert_eval_dir=expert_eval_dir,
        results_dir=results_dir,
        seed=args.seed,
        generate_forms=args.generate_forms,
        simulate_experts=args.simulate_experts,
        compute_kappa=args.compute_agreement,
        compare_with_judge=args.compare_judge,
        judge_results_path=args.judge_results,
    )


if __name__ == "__main__":
    main()
