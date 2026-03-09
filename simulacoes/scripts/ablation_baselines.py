"""Ablation study baselines for GraphRAG multi-strategy system.

Implements 4 ablation configurations to measure the contribution of each
retrieval component by systematically removing or isolating them:

    1. WithoutGraphBaseline     - Vector + Community (graph removed)
    2. WithoutVectorBaseline    - Graph + Community (vector removed)
    3. GraphOnlyBaseline        - Graph only (vector + community removed)
    4. CommunityOnlyBaseline    - Community only (graph + vector removed)

Together with the existing baselines (Full system, VectorRAG, HybridRAG),
these produce the 7-row ablation study in Table 7 of the paper.

Usage:
    from ablation_baselines import (
        WithoutGraphBaseline,
        WithoutVectorBaseline,
        GraphOnlyBaseline,
        CommunityOnlyBaseline,
    )

    without_graph = WithoutGraphBaseline(driver, embedder, anthropic_client)
    results = without_graph.retrieve("What is the minimum CET1 ratio?")
"""

import logging
import sys
from typing import Any

# Allow imports from the graphrag source tree
sys.path.insert(0, "/home/guhaase/projetos/panelbox/graphrag")

from src.retrieval.context_ranker import ContextRanker, RetrievalResult
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.community_retriever import CommunityRetriever
from src.retrieval.models import ParsedIntent

from baselines import BaseRetrieval

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Ablation 1: Without Graph (Vector + Community)
# ---------------------------------------------------------------------------

class WithoutGraphBaseline(BaseRetrieval):
    """Full system minus graph retriever.

    Uses VectorRetriever and CommunityRetriever with weights redistributed
    from the full system (graph zeroed, remaining normalized):
        vector=0.67, community=0.33

    Measures the contribution of graph traversal to overall performance.
    """

    baseline_name = "without_graph"

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
        self._community_retriever = CommunityRetriever(
            driver=driver, embedder=embedder,
        )

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using vector and community retrievers only.

        Args:
            parsed_intent: ParsedIntent for query text extraction.
            top_k: Maximum number of results per retriever.

        Returns:
            Dict with 'vector' and 'community' populated; 'graph' empty.
        """
        vector_results: list[RetrievalResult] = []
        community_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            try:
                raw = self._vector_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                vector_results = self._convert_results(raw, "vector")
            except Exception as exc:
                logger.warning("[without_graph] Vector retrieval failed: %s", exc)

            try:
                raw = self._community_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                community_results = self._convert_results(raw, "community")
            except Exception as exc:
                logger.warning("[without_graph] Community retrieval failed: %s", exc)

        return {
            "graph": [],
            "vector": vector_results,
            "community": community_results,
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return weights with graph zeroed and remainder redistributed.

        Returns:
            Fixed weight dict: vector=0.67, community=0.33.
        """
        return {"graph": 0.0, "vector": 0.67, "community": 0.33}


# ---------------------------------------------------------------------------
# Ablation 2: Without Vector (Graph + Community)
# ---------------------------------------------------------------------------

class WithoutVectorBaseline(BaseRetrieval):
    """Full system minus vector retriever.

    Uses GraphRetriever and CommunityRetriever with weights redistributed
    from the full system (vector zeroed, remaining normalized):
        graph=0.7, community=0.3

    Measures the contribution of semantic vector search.
    """

    baseline_name = "without_vector"

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
            try:
                raw = self._graph_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                graph_results = self._convert_results(raw, "graph")
            except Exception as exc:
                logger.warning("[without_vector] Graph retrieval failed: %s", exc)

            try:
                raw = self._community_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                community_results = self._convert_results(raw, "community")
            except Exception as exc:
                logger.warning("[without_vector] Community retrieval failed: %s", exc)

        return {
            "graph": graph_results,
            "vector": [],
            "community": community_results,
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return weights with vector zeroed and remainder redistributed.

        Returns:
            Fixed weight dict: graph=0.7, community=0.3.
        """
        return {"graph": 0.7, "vector": 0.0, "community": 0.3}


# ---------------------------------------------------------------------------
# Ablation 3: Graph Only
# ---------------------------------------------------------------------------

class GraphOnlyBaseline(BaseRetrieval):
    """Graph-only retriever: isolates graph traversal contribution.

    Uses only GraphRetriever with weight=1.0. No vector or community
    retrieval. Demonstrates graph traversal performance in isolation.
    """

    baseline_name = "graph_only"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        super().__init__(driver, embedder, anthropic_client, max_context_tokens)
        self._graph_retriever = GraphRetriever(driver=driver)

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using only the graph retriever.

        Args:
            parsed_intent: ParsedIntent for entity-based graph traversal.
            top_k: Maximum number of graph results.

        Returns:
            Dict with only 'graph' populated; 'vector' and 'community' empty.
        """
        graph_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            try:
                raw = self._graph_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                graph_results = self._convert_results(raw, "graph")
            except Exception as exc:
                logger.warning("[graph_only] Graph retrieval failed: %s", exc)

        return {
            "graph": graph_results,
            "vector": [],
            "community": [],
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return graph-only weights.

        Returns:
            Fixed weight dict: graph=1.0, others=0.0.
        """
        return {"graph": 1.0, "vector": 0.0, "community": 0.0}


# ---------------------------------------------------------------------------
# Ablation 4: Community Only
# ---------------------------------------------------------------------------

class CommunityOnlyBaseline(BaseRetrieval):
    """Community-only retriever: isolates community summarization contribution.

    Uses only CommunityRetriever with weight=1.0. No graph traversal or
    vector search. Demonstrates community detection performance in isolation.
    """

    baseline_name = "community_only"

    def __init__(
        self,
        driver: Any,
        embedder: Any,
        anthropic_client: Any = None,
        max_context_tokens: int = 4000,
    ) -> None:
        super().__init__(driver, embedder, anthropic_client, max_context_tokens)
        self._community_retriever = CommunityRetriever(
            driver=driver, embedder=embedder,
        )

    def _do_retrieve(
        self, parsed_intent: ParsedIntent | None, top_k: int
    ) -> dict[str, list[RetrievalResult]]:
        """Retrieve using only the community retriever.

        Args:
            parsed_intent: ParsedIntent for community matching.
            top_k: Maximum number of community results.

        Returns:
            Dict with only 'community' populated; 'graph' and 'vector' empty.
        """
        community_results: list[RetrievalResult] = []

        if parsed_intent is not None:
            try:
                raw = self._community_retriever.retrieve(
                    parsed_intent=parsed_intent, top_k=top_k,
                )
                community_results = self._convert_results(raw, "community")
            except Exception as exc:
                logger.warning("[community_only] Community retrieval failed: %s", exc)

        return {
            "graph": [],
            "vector": [],
            "community": community_results,
        }

    def _get_retrieval_weights(self) -> dict[str, float]:
        """Return community-only weights.

        Returns:
            Fixed weight dict: community=1.0, others=0.0.
        """
        return {"graph": 0.0, "vector": 0.0, "community": 1.0}
