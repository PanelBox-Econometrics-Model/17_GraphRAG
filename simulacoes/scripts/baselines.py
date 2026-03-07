"""Baseline retrieval systems for comparison against multi-strategy GraphRAG.

Implements four baselines to isolate and measure the contribution of each
component in the full retrieval pipeline:

    1. VectorRAGBaseline     - Vector-only retrieval (standard RAG)
    2. MSGraphRAGBaseline    - Graph + Community retrieval (Microsoft GraphRAG)
    3. HybridRAGBaseline     - Graph + Vector retrieval (Sarmah et al. 2024)
    4. NoRetrievalBaseline   - Direct LLM generation without retrieval

Each baseline shares the same interface as RetrievalEngine (retrieve, generate,
get_stats) and returns results in the same RetrievalContext format so that
downstream evaluation code works identically across all systems.

Usage:
    from baselines import (
        VectorRAGBaseline, MSGraphRAGBaseline,
        HybridRAGBaseline, NoRetrievalBaseline,
        BaselineRunner,
    )

    vector_rag = VectorRAGBaseline(driver, embedder, anthropic_client)
    results = vector_rag.retrieve("What is the Hausman test?")
    answer  = vector_rag.generate("What is the Hausman test?", results.formatted_context)

    runner = BaselineRunner(
        baselines={"vector": vector_rag, "msgraph": ms_graph_rag, ...},
        dataset=[{"id": "q1", "question": "What is ...?"}, ...],
    )
    comparison = runner.run()
"""

import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# Allow imports from the graphrag source tree
sys.path.insert(0, "/home/guhaase/projetos/panelbox/graphrag")

from src.retrieval.context_ranker import ContextRanker, RetrievalResult
from src.retrieval.engine import RetrievalContext
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.community_retriever import CommunityRetriever
from src.retrieval.intent_parser import IntentParser
from src.retrieval.models import IntentType, ParsedIntent, RetrievalType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
MAX_GENERATION_TOKENS = 2048

SYSTEM_PROMPT = (
    "You are a helpful technical assistant specializing in econometrics "
    "and panel data analysis. Answer based on the provided context when "
    "available. If no context is provided, answer from your general "
    "knowledge and state that clearly."
)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class BaseRetrieval(ABC):
    """Abstract base class for all baseline retrieval systems.

    Defines the common interface (retrieve, generate, get_stats) and
    shared helper methods for timing, token estimation, and LLM generation.

    Subclasses must implement _do_retrieve() to define their specific
    retrieval strategy.

    Args:
        driver: Neo4j driver instance for graph and vector queries.
        embedder: ChunkEmbedder instance for generating query embeddings.
        anthropic_client: Optional Anthropic client for LLM generation.
        max_context_tokens: Maximum tokens for the ranked context window.
    """

    baseline_name: str = "base"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        self._driver = driver
        self._embedder = embedder
        self._anthropic_client = anthropic_client
        self._max_context_tokens = max_context_tokens
        self._ranker = ContextRanker(max_context_tokens=max_context_tokens)
        self._intent_parser = self._create_intent_parser()

        # Accumulated statistics across calls
        self._call_count: int = 0
        self._total_latency_ms: float = 0.0
        self._total_retrieval_results: int = 0
        self._total_generation_tokens: int = 0
        self._last_stats: dict = {}

    def _create_intent_parser(self) -> IntentParser | None:
        """Create an IntentParser for entity extraction.

        Returns:
            IntentParser instance, or None if unavailable.
        """
        try:
            return IntentParser()
        except Exception as exc:
            logger.warning("IntentParser unavailable: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 10) -> RetrievalContext:
        """Execute the retrieval pipeline and return ranked context.

        Parses intent (for entity extraction), delegates to the subclass-
        specific _do_retrieve(), ranks the results, and records stats.

        Args:
            query: User query string.
            top_k: Maximum number of results per retriever.

        Returns:
            RetrievalContext with ranked results, formatted context, and stats.
        """
        pipeline_start = time.time()
        stage_timings: dict[str, float] = {}

        # Stage 1: Parse intent (shared across baselines for entity extraction)
        stage_start = time.time()
        parsed_intent = self._parse_intent(query)
        stage_timings["intent_parsing_ms"] = round(
            (time.time() - stage_start) * 1000, 2
        )

        # Stage 2: Subclass-specific retrieval
        stage_start = time.time()
        strategy_results = self._do_retrieve(parsed_intent, top_k)
        stage_timings["retrieval_ms"] = round(
            (time.time() - stage_start) * 1000, 2
        )

        # Stage 3: Rank and fuse using subclass-defined weights
        stage_start = time.time()
        weights = self._get_retrieval_weights()
        ranked_results = self._ranker.rank(
            graph_results=strategy_results.get("graph", []),
            vector_results=strategy_results.get("vector", []),
            community_results=strategy_results.get("community", []),
            weights=weights,
        )
        stage_timings["ranking_ms"] = round(
            (time.time() - stage_start) * 1000, 2
        )

        # Stage 4: Format context
        stage_start = time.time()
        formatted_context = self._ranker.format_context(ranked_results)
        stage_timings["formatting_ms"] = round(
            (time.time() - stage_start) * 1000, 2
        )

        total_ms = round((time.time() - pipeline_start) * 1000, 2)

        # Record stats for this call
        self._call_count += 1
        self._total_latency_ms += total_ms
        self._total_retrieval_results += len(ranked_results)

        graph_count = len(strategy_results.get("graph", []))
        vector_count = len(strategy_results.get("vector", []))
        community_count = len(strategy_results.get("community", []))

        self._last_stats = {
            "baseline": self.baseline_name,
            "total_latency_ms": total_ms,
            "stage_timings": stage_timings,
            "weights_used": weights,
            "intent_type": self._get_intent_type_str(parsed_intent),
            "graph_results_count": graph_count,
            "vector_results_count": vector_count,
            "community_results_count": community_count,
            "final_results_count": len(ranked_results),
            "ranker_stats": self._ranker.get_stats(),
            "context_token_estimate": sum(
                r.token_estimate for r in ranked_results
            ),
        }

        logger.info(
            "[%s] Pipeline completed in %.1fms: results=%d "
            "(g:%d v:%d c:%d -> %d final)",
            self.baseline_name,
            total_ms,
            graph_count + vector_count + community_count,
            graph_count,
            vector_count,
            community_count,
            len(ranked_results),
        )

        return RetrievalContext(
            results=ranked_results,
            formatted_context=formatted_context,
            parsed_intent=parsed_intent,
            stats=self._last_stats,
        )

    def generate(self, query: str, context: str) -> dict[str, Any]:
        """Generate an LLM response for the query using the provided context.

        Uses the Anthropic API (Claude) to produce an answer, recording
        latency and token usage metrics.

        Args:
            query: User query string.
            context: Formatted retrieval context (may be empty for NoRetrieval).

        Returns:
            Dictionary with keys:
                - answer (str): The generated response text.
                - model (str): Model identifier used.
                - latency_ms (float): Generation latency in milliseconds.
                - input_tokens (int): Tokens in the prompt.
                - output_tokens (int): Tokens in the completion.
                - baseline (str): Name of this baseline.
        """
        if self._anthropic_client is None:
            return {
                "answer": "[No Anthropic client configured]",
                "model": "none",
                "latency_ms": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "baseline": self.baseline_name,
            }

        # Build the user message
        if context and context.strip():
            user_message = (
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Answer the question based on the context above."
            )
        else:
            user_message = (
                f"Question: {query}\n\n"
                f"Answer the question from your general knowledge."
            )

        start_time = time.time()
        try:
            response = self._anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_GENERATION_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            latency_ms = round((time.time() - start_time) * 1000, 2)

            answer_text = response.content[0].text if response.content else ""
            input_tokens = getattr(response.usage, "input_tokens", 0)
            output_tokens = getattr(response.usage, "output_tokens", 0)

            self._total_generation_tokens += input_tokens + output_tokens

            return {
                "answer": answer_text,
                "model": ANTHROPIC_MODEL,
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "baseline": self.baseline_name,
            }

        except Exception as exc:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "[%s] Generation failed after %.1fms: %s",
                self.baseline_name, latency_ms, exc,
            )
            return {
                "answer": f"[Generation error: {exc}]",
                "model": ANTHROPIC_MODEL,
                "latency_ms": latency_ms,
                "input_tokens": 0,
                "output_tokens": 0,
                "baseline": self.baseline_name,
            }

    def get_stats(self) -> dict:
        """Return statistics from the last retrieval call and cumulative totals.

        Returns:
            Dictionary with last-call stats and aggregate metrics.
        """
        return {
            **self._last_stats,
            "cumulative": {
                "call_count": self._call_count,
                "total_latency_ms": round(self._total_latency_ms, 2),
                "avg_latency_ms": round(
                    self._total_latency_ms / max(self._call_count, 1), 2
                ),
                "total_retrieval_results": self._total_retrieval_results,
                "total_generation_tokens": self._total_generation_tokens,
            },
        }

    def reset_stats(self) -> None:
        """Reset all cumulative statistics to zero."""
        self._call_count = 0
        self._total_latency_ms = 0.0
        self._total_retrieval_results = 0
        self._total_generation_tokens = 0
        self._last_stats = {}

    # ------------------------------------------------------------------
    # Abstract method for subclasses
    # ------------------------------------------------------------------

    @abstractmethod
    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Perform subclass-specific retrieval.

        Must return a dictionary with keys 'graph', 'vector', 'community',
        each mapping to a (possibly empty) list of RetrievalResult.

        Args:
            parsed_intent: ParsedIntent from the intent parser (may be None).
            top_k: Maximum results per retriever.

        Returns:
            Dict mapping strategy name to list of RetrievalResult.
        """
        ...

    @abstractmethod
    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return the fixed retrieval weights for this baseline.

        Returns:
            Dict with keys 'graph', 'vector', 'community' summing to ~1.0.
        """
        ...

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _parse_intent(self, query: str) -> ParsedIntent | None:
        """Parse the user query to extract entities and intent type.

        This is used by all baselines (except NoRetrieval) for entity
        extraction, even when the weights are not intent-adaptive.

        Args:
            query: User query string.

        Returns:
            ParsedIntent, or None if the parser is unavailable.
        """
        if self._intent_parser is None:
            return ParsedIntent(
                query=query,
                entities=[],
                intent_type=IntentType.GENERAL,
                retrieval_weights={},
                cypher_hints=[],
                confidence=0.0,
            )
        try:
            return self._intent_parser.parse(query)
        except Exception as exc:
            logger.warning("Intent parsing failed: %s", exc)
            return ParsedIntent(
                query=query,
                entities=[],
                intent_type=IntentType.GENERAL,
                retrieval_weights={},
                cypher_hints=[],
                confidence=0.0,
            )

    def _get_intent_type_str(self, parsed_intent: ParsedIntent | None) -> str:
        """Extract intent type string from a ParsedIntent.

        Args:
            parsed_intent: ParsedIntent or None.

        Returns:
            Intent type string (e.g. 'validation', 'general').
        """
        if parsed_intent is None:
            return "general"
        intent_type = parsed_intent.intent_type
        if hasattr(intent_type, "value"):
            return str(intent_type.value)
        return str(intent_type)

    def _convert_results(
        self, raw_results: list, source_strategy: str
    ) -> list[RetrievalResult]:
        """Convert raw retriever output to ContextRanker RetrievalResult objects.

        Handles the different return formats from GraphRetriever (which uses
        its own RetrievalResult with node_id, node_type, properties, etc.),
        VectorRetriever (which returns src.retrieval.models.RetrievalResult
        with content, source, retrieval_type), and CommunityRetriever.

        Args:
            raw_results: List of result objects from a retriever.
            source_strategy: Strategy name ('graph', 'vector', 'community').

        Returns:
            List of context_ranker.RetrievalResult objects.
        """
        converted: list[RetrievalResult] = []

        for item in raw_results:
            # Already a ContextRanker RetrievalResult
            if isinstance(item, RetrievalResult):
                item.source_strategy = source_strategy
                converted.append(item)

            # Dict format
            elif isinstance(item, dict):
                converted.append(RetrievalResult(
                    chunk_id=item.get("chunk_id", item.get("id", "")),
                    content=item.get("content", item.get("text", "")),
                    score=float(item.get("score", item.get("similarity", 0.0))),
                    source_strategy=source_strategy,
                    metadata={
                        k: v for k, v in item.items()
                        if k not in (
                            "chunk_id", "id", "content", "text",
                            "score", "similarity",
                        )
                    },
                ))

            # Object with a score attribute (GraphRetriever.RetrievalResult, etc.)
            elif hasattr(item, "score"):
                metadata: dict[str, Any] = {}
                raw_metadata = getattr(item, "metadata", {})
                if isinstance(raw_metadata, dict):
                    metadata.update(raw_metadata)

                # Preserve source info
                source = getattr(item, "source", "")
                if source:
                    metadata["source_file"] = source

                # Preserve graph-specific fields
                for attr in ("name", "node_type", "node_id"):
                    val = getattr(item, attr, None)
                    if val:
                        if attr == "node_type":
                            metadata["entity_type"] = val
                        else:
                            metadata[attr] = val

                # Preserve relationships
                relationships = getattr(item, "relationships", None)
                if relationships:
                    rel_strs = []
                    for rel in relationships:
                        if isinstance(rel, dict):
                            rel_strs.append(
                                f"{rel.get('type', '?')} -> {rel.get('target', '?')}"
                            )
                        else:
                            rel_strs.append(str(rel))
                    metadata["relationships"] = rel_strs

                # Build content
                content = getattr(item, "content", "")
                if not content:
                    props = getattr(item, "properties", {}) or {}
                    name = getattr(item, "name", "")
                    node_type = getattr(item, "node_type", "")
                    parts = []
                    if name:
                        parts.append(
                            f"{node_type}: {name}" if node_type else name
                        )
                    if props.get("description"):
                        parts.append(props["description"])
                    if props.get("content"):
                        parts.append(props["content"])
                    for key in ("assumptions", "implementation_notes", "formula"):
                        if props.get(key):
                            parts.append(f"{key}: {props[key]}")
                    content = "\n".join(parts) if parts else str(props)

                converted.append(RetrievalResult(
                    chunk_id=getattr(
                        item, "chunk_id", getattr(item, "node_id", source)
                    ),
                    content=content,
                    score=float(getattr(item, "score", 0.0)),
                    source_strategy=source_strategy,
                    metadata=metadata,
                ))

        return converted


# ---------------------------------------------------------------------------
# Baseline 1: Vector-only RAG
# ---------------------------------------------------------------------------

class VectorRAGBaseline(BaseRetrieval):
    """Vector-only retrieval baseline (standard RAG).

    Uses ONLY the VectorRetriever with weight=1.0 for all intent types.
    No graph traversal, no community detection. This isolates the
    contribution of semantic search alone.

    Reference: Lewis et al. (2020) "Retrieval-Augmented Generation for
    Knowledge-Intensive NLP Tasks"
    """

    baseline_name = "vector_rag"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        super().__init__(driver, embedder, anthropic_client, max_context_tokens)
        self._vector_retriever = VectorRetriever(
            driver=driver, embedder=embedder,
        )

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using only the vector retriever.

        Args:
            parsed_intent: ParsedIntent for query text extraction.
            top_k: Maximum number of vector results.

        Returns:
            Dict with only 'vector' populated; 'graph' and 'community' empty.
        """
        vector_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            try:
                raw = self._vector_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                vector_results = self._convert_results(raw, "vector")
            except Exception as exc:
                logger.warning("[vector_rag] Vector retrieval failed: %s", exc)

        return {
            "graph": [],
            "vector": vector_results,
            "community": [],
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return vector-only weights (1.0 for vector, 0.0 for others).

        Returns:
            Fixed weight dict.
        """
        return {"graph": 0.0, "vector": 1.0, "community": 0.0}


# ---------------------------------------------------------------------------
# Baseline 2: Microsoft GraphRAG (Graph + Community, no Vector)
# ---------------------------------------------------------------------------

class MSGraphRAGBaseline(BaseRetrieval):
    """Microsoft GraphRAG baseline: Graph + Community retrieval.

    Uses GraphRetriever and CommunityRetriever with fixed weights
    (graph=0.6, community=0.4) for ALL intent types. No VectorRetriever,
    no intent-aware weight adaptation.

    This simulates the core approach from:
    Edge et al. (2024) "From Local to Global: A Graph RAG Approach to
    Query-Focused Summarization"
    """

    baseline_name = "ms_graphrag"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        super().__init__(driver, embedder, anthropic_client, max_context_tokens)
        self._graph_retriever = GraphRetriever(driver=driver)
        self._community_retriever = CommunityRetriever(
            driver=driver, embedder=embedder,
        )

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using graph and community retrievers only.

        Args:
            parsed_intent: ParsedIntent for entity-based graph traversal.
            top_k: Maximum number of results per retriever.

        Returns:
            Dict with 'graph' and 'community' populated; 'vector' empty.
        """
        graph_results: list[RetrievalResult] = []
        community_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            # Graph retriever
            try:
                raw = self._graph_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                graph_results = self._convert_results(raw, "graph")
            except Exception as exc:
                logger.warning("[ms_graphrag] Graph retrieval failed: %s", exc)

            # Community retriever
            try:
                raw = self._community_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                community_results = self._convert_results(raw, "community")
            except Exception as exc:
                logger.warning(
                    "[ms_graphrag] Community retrieval failed: %s", exc,
                )

        return {
            "graph": graph_results,
            "vector": [],
            "community": community_results,
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return fixed MS GraphRAG weights: graph=0.6, community=0.4.

        Returns:
            Fixed weight dict (no intent adaptation).
        """
        return {"graph": 0.6, "vector": 0.0, "community": 0.4}


# ---------------------------------------------------------------------------
# Baseline 3: HybridRAG (Graph + Vector, no Community)
# ---------------------------------------------------------------------------

class HybridRAGBaseline(BaseRetrieval):
    """Hybrid RAG baseline: Graph + Vector retrieval.

    Uses GraphRetriever and VectorRetriever with fixed equal weights
    (graph=0.5, vector=0.5) for ALL intent types. No CommunityRetriever,
    no intent-aware weight adaptation.

    This simulates the approach from:
    Sarmah et al. (2024) "HybridRAG: Integrating Knowledge Graphs and
    Vector Retrieval Augmented Generation for Efficient Information
    Extraction"
    """

    baseline_name = "hybrid_rag"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        super().__init__(driver, embedder, anthropic_client, max_context_tokens)
        self._graph_retriever = GraphRetriever(driver=driver)
        self._vector_retriever = VectorRetriever(
            driver=driver, embedder=embedder,
        )

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using graph and vector retrievers only.

        Args:
            parsed_intent: ParsedIntent for entity extraction and query text.
            top_k: Maximum number of results per retriever.

        Returns:
            Dict with 'graph' and 'vector' populated; 'community' empty.
        """
        graph_results: list[RetrievalResult] = []
        vector_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            # Graph retriever
            try:
                raw = self._graph_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                graph_results = self._convert_results(raw, "graph")
            except Exception as exc:
                logger.warning("[hybrid_rag] Graph retrieval failed: %s", exc)

            # Vector retriever
            try:
                raw = self._vector_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                vector_results = self._convert_results(raw, "vector")
            except Exception as exc:
                logger.warning("[hybrid_rag] Vector retrieval failed: %s", exc)

        return {
            "graph": graph_results,
            "vector": vector_results,
            "community": [],
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return fixed HybridRAG weights: graph=0.5, vector=0.5.

        Returns:
            Fixed weight dict (no intent adaptation).
        """
        return {"graph": 0.5, "vector": 0.5, "community": 0.0}


# ---------------------------------------------------------------------------
# Baseline 4: No Retrieval (direct LLM)
# ---------------------------------------------------------------------------

class NoRetrievalBaseline(BaseRetrieval):
    """No-retrieval baseline: sends queries directly to the LLM.

    No retrieval is performed. The query is sent to Claude without
    any retrieved context, establishing the absolute lower bound
    for domain-specific question answering.
    """

    baseline_name = "no_retrieval"

    def __init__(
        self,
        driver: Any = None,
        embedder: Any = None,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        # Pass None-safe driver/embedder to parent; they will not be used
        super().__init__(
            driver=driver,
            embedder=embedder,
            anthropic_client=anthropic_client,
            max_context_tokens=max_context_tokens,
        )

    def _create_intent_parser(self) -> IntentParser | None:
        """Override: no intent parsing needed for this baseline.

        Returns:
            None (no parser needed).
        """
        return None

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Return empty results for all strategies.

        Args:
            parsed_intent: Ignored.
            top_k: Ignored.

        Returns:
            Dict with all strategies empty.
        """
        return {
            "graph": [],
            "vector": [],
            "community": [],
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return zero weights (no retrieval).

        Returns:
            All-zero weight dict.
        """
        return {"graph": 0.0, "vector": 0.0, "community": 0.0}


# ---------------------------------------------------------------------------
# Baseline Runner
# ---------------------------------------------------------------------------

@dataclass
class QuestionResult:
    """Result of running a single question through a single baseline.

    Attributes:
        question_id: Unique identifier for the question.
        question: The question text.
        baseline_name: Name of the baseline used.
        retrieval_context: The full RetrievalContext from retrieval.
        generation_result: Dict with answer, latency, and token counts.
        retrieval_latency_ms: Retrieval phase latency.
        generation_latency_ms: Generation phase latency.
        total_latency_ms: End-to-end latency.
        retrieval_count: Number of retrieval results.
        context_tokens: Estimated tokens in the context.
        error: Error message if the run failed, else None.
    """
    question_id: str = ""
    question: str = ""
    baseline_name: str = ""
    retrieval_context: RetrievalContext | None = None
    generation_result: dict = field(default_factory=dict)
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    retrieval_count: int = 0
    context_tokens: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        """Serialize to a flat dictionary for tabular analysis.

        Returns:
            Dictionary with all scalar fields; retrieval_context is
            replaced by its formatted_context string for compactness.
        """
        return {
            "question_id": self.question_id,
            "question": self.question,
            "baseline": self.baseline_name,
            "answer": self.generation_result.get("answer", ""),
            "retrieval_latency_ms": self.retrieval_latency_ms,
            "generation_latency_ms": self.generation_latency_ms,
            "total_latency_ms": self.total_latency_ms,
            "retrieval_count": self.retrieval_count,
            "context_tokens": self.context_tokens,
            "input_tokens": self.generation_result.get("input_tokens", 0),
            "output_tokens": self.generation_result.get("output_tokens", 0),
            "formatted_context": (
                self.retrieval_context.formatted_context
                if self.retrieval_context else ""
            ),
            "error": self.error,
        }


@dataclass
class BaselineComparison:
    """Aggregated comparison results across all baselines and questions.

    Attributes:
        results: List of QuestionResult for every (baseline, question) pair.
        summary: Per-baseline aggregate statistics.
        metadata: Run metadata (timestamp, question count, baseline names).
    """
    results: list[QuestionResult] = field(default_factory=list)
    summary: dict[str, dict] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_records(self) -> list[dict]:
        """Convert all results to a list of flat dictionaries.

        Suitable for creating a pandas DataFrame:
            df = pd.DataFrame(comparison.to_records())

        Returns:
            List of dictionaries, one per (baseline, question) pair.
        """
        return [r.to_dict() for r in self.results]


class BaselineRunner:
    """Runs multiple baselines across a dataset and collects comparison metrics.

    Takes a dictionary of named baseline instances and a dataset (list of
    question dicts), runs each baseline on every question, and produces
    structured comparison results.

    Args:
        baselines: Dict mapping baseline name to BaseRetrieval instance.
        dataset: List of question dicts, each with at least 'question'
            and optionally 'id' and 'reference_answer' keys.
        run_generation: Whether to also run LLM generation (default True).
            Set to False for retrieval-only benchmarking.
    """

    def __init__(
        self,
        baselines: dict[str, BaseRetrieval],
        dataset: list[dict[str, str]],
        run_generation: bool = True,
    ) -> None:
        self._baselines = baselines
        self._dataset = dataset
        self._run_generation = run_generation

    def run(self, top_k: int = 10) -> BaselineComparison:
        """Execute all baselines on all questions and collect metrics.

        For each question, runs each baseline's retrieve() method and
        optionally generate() method, recording latency and result counts.

        Args:
            top_k: Maximum retrieval results per retriever per question.

        Returns:
            BaselineComparison with per-question results and summary.
        """
        all_results: list[QuestionResult] = []
        run_start = time.time()

        total_pairs = len(self._dataset) * len(self._baselines)
        logger.info(
            "Starting baseline comparison: %d baselines x %d questions = %d runs",
            len(self._baselines),
            len(self._dataset),
            total_pairs,
        )

        for q_idx, question_data in enumerate(self._dataset, start=1):
            question_text = question_data.get("question", question_data.get("q", ""))
            question_id = question_data.get("id", f"q{q_idx:03d}")

            if not question_text:
                logger.warning(
                    "Skipping question %s: empty text", question_id,
                )
                continue

            logger.info(
                "[%d/%d] Question: %s",
                q_idx, len(self._dataset), question_text[:80],
            )

            for baseline_name, baseline in self._baselines.items():
                result = self._run_single(
                    baseline=baseline,
                    baseline_name=baseline_name,
                    question_id=question_id,
                    question_text=question_text,
                    top_k=top_k,
                )
                all_results.append(result)

        # Compute summary
        summary = self._compute_summary(all_results)
        run_duration_s = round(time.time() - run_start, 2)

        metadata = {
            "total_questions": len(self._dataset),
            "total_baselines": len(self._baselines),
            "baseline_names": list(self._baselines.keys()),
            "run_generation": self._run_generation,
            "top_k": top_k,
            "total_runs": len(all_results),
            "run_duration_s": run_duration_s,
        }

        logger.info(
            "Baseline comparison completed in %.1fs: %d total runs",
            run_duration_s,
            len(all_results),
        )

        return BaselineComparison(
            results=all_results,
            summary=summary,
            metadata=metadata,
        )

    def _run_single(
        self,
        baseline: BaseRetrieval,
        baseline_name: str,
        question_id: str,
        question_text: str,
        top_k: int,
    ) -> QuestionResult:
        """Run a single baseline on a single question.

        Args:
            baseline: The baseline instance.
            baseline_name: Name of the baseline.
            question_id: Unique question identifier.
            question_text: The question text.
            top_k: Maximum retrieval results.

        Returns:
            QuestionResult with all metrics populated.
        """
        result = QuestionResult(
            question_id=question_id,
            question=question_text,
            baseline_name=baseline_name,
        )

        total_start = time.time()

        # Retrieval phase
        try:
            retrieval_start = time.time()
            retrieval_ctx = baseline.retrieve(question_text, top_k=top_k)
            result.retrieval_latency_ms = round(
                (time.time() - retrieval_start) * 1000, 2
            )
            result.retrieval_context = retrieval_ctx
            result.retrieval_count = len(retrieval_ctx.results)
            result.context_tokens = sum(
                r.token_estimate for r in retrieval_ctx.results
            )
        except Exception as exc:
            result.retrieval_latency_ms = round(
                (time.time() - total_start) * 1000, 2
            )
            result.error = f"Retrieval error: {exc}"
            logger.error(
                "[%s] Retrieval failed for %s: %s",
                baseline_name, question_id, exc,
            )
            result.total_latency_ms = result.retrieval_latency_ms
            return result

        # Generation phase
        if self._run_generation:
            try:
                gen_start = time.time()
                gen_result = baseline.generate(
                    question_text, retrieval_ctx.formatted_context,
                )
                result.generation_latency_ms = round(
                    (time.time() - gen_start) * 1000, 2
                )
                result.generation_result = gen_result
            except Exception as exc:
                result.generation_latency_ms = round(
                    (time.time() - total_start) * 1000
                    - result.retrieval_latency_ms, 2,
                )
                result.error = f"Generation error: {exc}"
                logger.error(
                    "[%s] Generation failed for %s: %s",
                    baseline_name, question_id, exc,
                )

        result.total_latency_ms = round(
            (time.time() - total_start) * 1000, 2
        )
        return result

    def _compute_summary(
        self, results: list[QuestionResult]
    ) -> dict[str, dict]:
        """Compute per-baseline aggregate statistics.

        For each baseline, computes mean/median/max for latency and
        retrieval counts, and total token usage.

        Args:
            results: All QuestionResult objects from the run.

        Returns:
            Dict mapping baseline name to statistics dict.
        """
        from collections import defaultdict

        grouped: dict[str, list[QuestionResult]] = defaultdict(list)
        for r in results:
            grouped[r.baseline_name].append(r)

        summary: dict[str, dict] = {}

        for name, group in grouped.items():
            retrieval_latencies = [r.retrieval_latency_ms for r in group]
            generation_latencies = [
                r.generation_latency_ms for r in group if r.generation_latency_ms > 0
            ]
            total_latencies = [r.total_latency_ms for r in group]
            retrieval_counts = [r.retrieval_count for r in group]
            context_token_counts = [r.context_tokens for r in group]
            error_count = sum(1 for r in group if r.error is not None)

            total_input_tokens = sum(
                r.generation_result.get("input_tokens", 0) for r in group
            )
            total_output_tokens = sum(
                r.generation_result.get("output_tokens", 0) for r in group
            )

            summary[name] = {
                "question_count": len(group),
                "error_count": error_count,
                "retrieval_latency_ms": {
                    "mean": round(
                        sum(retrieval_latencies)
                        / max(len(retrieval_latencies), 1), 2,
                    ),
                    "median": round(
                        sorted(retrieval_latencies)[len(retrieval_latencies) // 2]
                        if retrieval_latencies else 0.0, 2,
                    ),
                    "max": round(
                        max(retrieval_latencies) if retrieval_latencies else 0.0,
                        2,
                    ),
                },
                "generation_latency_ms": {
                    "mean": round(
                        sum(generation_latencies)
                        / max(len(generation_latencies), 1), 2,
                    ),
                    "median": round(
                        sorted(generation_latencies)[
                            len(generation_latencies) // 2
                        ]
                        if generation_latencies else 0.0, 2,
                    ),
                    "max": round(
                        max(generation_latencies)
                        if generation_latencies else 0.0, 2,
                    ),
                },
                "total_latency_ms": {
                    "mean": round(
                        sum(total_latencies) / max(len(total_latencies), 1), 2,
                    ),
                    "median": round(
                        sorted(total_latencies)[len(total_latencies) // 2]
                        if total_latencies else 0.0, 2,
                    ),
                    "max": round(
                        max(total_latencies) if total_latencies else 0.0, 2,
                    ),
                },
                "retrieval_count": {
                    "mean": round(
                        sum(retrieval_counts)
                        / max(len(retrieval_counts), 1), 2,
                    ),
                    "median": round(
                        sorted(retrieval_counts)[len(retrieval_counts) // 2]
                        if retrieval_counts else 0, 2,
                    ),
                    "max": max(retrieval_counts) if retrieval_counts else 0,
                },
                "context_tokens": {
                    "mean": round(
                        sum(context_token_counts)
                        / max(len(context_token_counts), 1), 2,
                    ),
                    "total": sum(context_token_counts),
                },
                "generation_tokens": {
                    "total_input": total_input_tokens,
                    "total_output": total_output_tokens,
                    "total": total_input_tokens + total_output_tokens,
                },
            }

        return summary


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def create_all_baselines(
    driver: Any,
    embedder: Any,
    anthropic_client: Any = None,
    max_context_tokens: int = 4000,
) -> dict[str, BaseRetrieval]:
    """Create all four baseline instances in a named dictionary.

    Convenience factory for use with BaselineRunner.

    Args:
        driver: Neo4j driver instance.
        embedder: ChunkEmbedder instance.
        anthropic_client: Optional Anthropic client for LLM generation.
        max_context_tokens: Maximum tokens for the context window.

    Returns:
        Dict mapping baseline name to baseline instance:
            - "vector_rag": VectorRAGBaseline
            - "ms_graphrag": MSGraphRAGBaseline
            - "hybrid_rag": HybridRAGBaseline
            - "no_retrieval": NoRetrievalBaseline
    """
    return {
        "vector_rag": VectorRAGBaseline(
            driver=driver,
            embedder=embedder,
            anthropic_client=anthropic_client,
            max_context_tokens=max_context_tokens,
        ),
        "ms_graphrag": MSGraphRAGBaseline(
            driver=driver,
            embedder=embedder,
            anthropic_client=anthropic_client,
            max_context_tokens=max_context_tokens,
        ),
        "hybrid_rag": HybridRAGBaseline(
            driver=driver,
            embedder=embedder,
            anthropic_client=anthropic_client,
            max_context_tokens=max_context_tokens,
        ),
        "no_retrieval": NoRetrievalBaseline(
            anthropic_client=anthropic_client,
            max_context_tokens=max_context_tokens,
        ),
    }
