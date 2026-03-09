"""LLM-as-Judge Evaluation Framework for GraphRAG.

Evaluates three dimensions of response quality using Claude as judge:
    1. Faithfulness: Are claims in the response grounded in the retrieved context?
    2. Factual Accuracy: Are claims factually correct per the ground truth?
    3. Grounding Rate: Does the response provide explicit source attribution?

References:
    - Zheng et al. (2023) "Judging LLM-as-a-Judge" (arXiv:2306.05685)
    - RAGAS evaluation framework
    - G-Eval (Liu et al., 2023)

Usage:
    # Live mode (requires Anthropic API key)
    judge = LLMJudge(model="claude-haiku-4-5-20251001")
    result = judge.evaluate_full(
        question_id="q001",
        system_name="MultiStrategy_GraphRAG",
        query="What is the minimum CET1 ratio under Basel III?",
        context="Basel III requires a minimum CET1 ratio of 4.5%...",
        response="The minimum CET1 ratio is 4.5% as per Basel III Pillar 1...",
        ground_truth="4.5% CET1 minimum under Basel III Pillar 1",
        source_articles=["Basel III Pillar 1, Art. 50"],
    )

    # Simulation mode (no API calls)
    sim_judge = SimulatedJudge(seed=42)
    result = sim_judge.evaluate_full(...)
"""

import json
import logging
import re
from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

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

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


class LLMJudge:
    """Evaluates GraphRAG responses using Claude as judge.

    Makes three separate API calls per evaluation (faithfulness, accuracy,
    grounding), each returning structured JSON with scores and reasoning.

    Args:
        model: Claude model to use for judging.
        temperature: Sampling temperature (0.0 for deterministic).
        max_tokens: Maximum response tokens per judge call.
    """

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        from anthropic import Anthropic
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
        """Run all three evaluations for a single response.

        Args:
            question_id: Unique question identifier.
            system_name: Name of the system being evaluated.
            query: User query text.
            context: Retrieved context text.
            response: Generated response text.
            ground_truth: Expected answer text.
            source_articles: List of expected source references.

        Returns:
            JudgeResult with all scores and reasoning.
        """
        tokens_before = self.total_tokens_used

        faith = self.evaluate_faithfulness(query, context, response)
        accuracy = self.evaluate_factual_accuracy(
            query, response, ground_truth, source_articles
        )
        grounding = self.evaluate_grounding(response, source_articles)

        tokens_used = self.total_tokens_used - tokens_before

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
            judge_tokens_used=tokens_used,
        )

    def _call_judge(self, prompt: str) -> dict:
        """Call Claude API and parse JSON response.

        Args:
            prompt: Full evaluation prompt.

        Returns:
            Parsed JSON dictionary from judge response.
        """
        try:
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

            # Try direct JSON parse
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Try to find JSON block in response
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
                logger.warning("Failed to parse judge response as JSON")
                return {"error": "Failed to parse judge response", "raw": text}

        except Exception as exc:
            logger.error("Judge API call failed: %s", exc)
            return {"error": str(exc)}

    def get_stats(self) -> dict:
        """Return judge usage statistics.

        Returns:
            Dictionary with model, total tokens, and estimated cost.
        """
        # Estimate cost based on Haiku pricing
        cost_per_m_input = 0.80
        cost_per_m_output = 4.00
        # Rough split: ~70% input, ~30% output
        estimated_input = self.total_tokens_used * 0.7
        estimated_output = self.total_tokens_used * 0.3
        estimated_cost = (
            estimated_input * cost_per_m_input / 1_000_000
            + estimated_output * cost_per_m_output / 1_000_000
        )

        return {
            "model": self.model,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": round(estimated_cost, 4),
        }


class SimulatedJudge:
    """Simulated judge for testing without API calls.

    Generates realistic scores with Gaussian noise around expected values,
    matching the simulation engine pattern used throughout the experiments.

    Args:
        seed: Random seed for reproducibility.
        hallucination_params: Optional override for per-system score parameters.
    """

    # Default per-system score parameters (aligned with SimulationEngine)
    DEFAULT_PARAMS: dict[str, dict[str, float]] = {
        "MultiStrategy_GraphRAG": {
            "faithfulness_mean": 0.87, "faithfulness_std": 0.04,
            "accuracy_mean": 0.84, "accuracy_std": 0.05,
            "grounding_mean": 0.96, "grounding_std": 0.02,
        },
        "VectorRAG": {
            "faithfulness_mean": 0.72, "faithfulness_std": 0.06,
            "accuracy_mean": 0.68, "accuracy_std": 0.07,
            "grounding_mean": 0.55, "grounding_std": 0.08,
        },
        "MS_GraphRAG": {
            "faithfulness_mean": 0.80, "faithfulness_std": 0.05,
            "accuracy_mean": 0.75, "accuracy_std": 0.06,
            "grounding_mean": 0.70, "grounding_std": 0.06,
        },
        "HybridRAG": {
            "faithfulness_mean": 0.82, "faithfulness_std": 0.05,
            "accuracy_mean": 0.78, "accuracy_std": 0.06,
            "grounding_mean": 0.72, "grounding_std": 0.06,
        },
        "NoRetrieval": {
            "faithfulness_mean": 0.45, "faithfulness_std": 0.10,
            "accuracy_mean": 0.40, "accuracy_std": 0.10,
            "grounding_mean": 0.00, "grounding_std": 0.00,
        },
    }

    def __init__(
        self,
        seed: int = 42,
        hallucination_params: dict[str, dict[str, float]] | None = None,
    ):
        self.rng = np.random.default_rng(seed)
        self.params = hallucination_params or self.DEFAULT_PARAMS
        self.total_tokens_used = 0
        self.total_calls = 0

    def evaluate_full(
        self,
        question_id: str,
        system_name: str,
        query: str = "",
        context: str = "",
        response: str = "",
        ground_truth: str = "",
        source_articles: list[str] | None = None,
        difficulty: str = "moderate",
    ) -> JudgeResult:
        """Generate simulated judge scores.

        Args:
            question_id: Unique question identifier.
            system_name: Name of the system being evaluated.
            query: User query (used for reasoning generation).
            context: Retrieved context (unused in simulation).
            response: Generated response (unused in simulation).
            ground_truth: Expected answer (unused in simulation).
            source_articles: Expected sources (unused in simulation).
            difficulty: Question difficulty for score adjustment.

        Returns:
            JudgeResult with simulated scores.
        """
        params = self.params.get(system_name, self.params.get("VectorRAG", {}))

        # Difficulty multipliers
        diff_mult = {
            "simple": 1.02,
            "moderate": 1.00,
            "complex": 0.95,
            "multi_hop": 0.90,
        }.get(difficulty, 1.0)

        faithfulness = float(np.clip(
            self.rng.normal(
                params.get("faithfulness_mean", 0.5) * diff_mult,
                params.get("faithfulness_std", 0.1),
            ),
            0.0, 1.0,
        ))

        accuracy = float(np.clip(
            self.rng.normal(
                params.get("accuracy_mean", 0.5) * diff_mult,
                params.get("accuracy_std", 0.1),
            ),
            0.0, 1.0,
        ))

        if system_name == "NoRetrieval":
            grounding = 0.0
        else:
            grounding_raw = float(np.clip(
                self.rng.normal(
                    params.get("grounding_mean", 0.5) * diff_mult,
                    params.get("grounding_std", 0.1),
                ),
                0.0, 1.0,
            ))
            # Binary threshold: >=0.5 means grounded
            grounding = 1.0 if grounding_raw >= 0.5 else 0.0

        # Simulate token usage (~1200 tokens per full evaluation)
        tokens = int(self.rng.normal(1200, 200))
        self.total_tokens_used += max(tokens, 100)
        self.total_calls += 3  # 3 calls per full evaluation

        return JudgeResult(
            question_id=question_id,
            system_name=system_name,
            faithfulness_score=round(faithfulness, 4),
            factual_accuracy_score=round(accuracy, 4),
            grounding_score=grounding,
            faithfulness_reasoning=f"[Simulated] Faithfulness={faithfulness:.2f} for {system_name}",
            accuracy_reasoning=f"[Simulated] Accuracy={accuracy:.2f} for {system_name}",
            grounding_reasoning=f"[Simulated] Grounding={'present' if grounding else 'absent'} for {system_name}",
            judge_model="simulated",
            judge_tokens_used=tokens,
        )

    def get_stats(self) -> dict:
        """Return simulated judge statistics."""
        return {
            "model": "simulated",
            "total_tokens_used": self.total_tokens_used,
            "total_calls": self.total_calls,
            "estimated_cost_usd": 0.0,
        }
