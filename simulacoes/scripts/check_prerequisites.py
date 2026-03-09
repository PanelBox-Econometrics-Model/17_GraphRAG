#!/usr/bin/env python3
"""Check prerequisites for live experiment execution.

Verifies 8 conditions required to run experiments in live mode:
    1. Neo4j connection
    2. Knowledge graph populated (>= 500 entities)
    3. Vector index available
    4. Communities detected
    5. Anthropic API key configured
    6. Datasets available (200 questions + 50 benchmark)
    7. Baselines importable
    8. LLM judge importable

Usage:
    # Check all prerequisites
    python check_prerequisites.py

    # Check with custom Neo4j connection
    python check_prerequisites.py --neo4j-uri bolt://localhost:7687

    # Check and output JSON report
    python check_prerequisites.py --json
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Allow imports from the GraphRAG source tree
sys.path.insert(0, "/home/guhaase/projetos/panelbox/graphrag")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_neo4j_connection(uri: str, auth: tuple) -> dict:
    """Check if Neo4j is reachable.

    Args:
        uri: Neo4j bolt URI.
        auth: Tuple of (username, password).

    Returns:
        Status dict with success, message, and details.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run("RETURN 1 AS n")
            record = result.single()
            driver.close()
            return {
                "check": "neo4j_connection",
                "status": "PASS",
                "message": f"Connected to Neo4j at {uri}",
                "details": {"uri": uri},
            }
    except Exception as exc:
        return {
            "check": "neo4j_connection",
            "status": "FAIL",
            "message": f"Cannot connect to Neo4j: {exc}",
            "details": {"uri": uri, "error": str(exc)},
        }


def check_kg_populated(uri: str, auth: tuple, min_entities: int = 500) -> dict:
    """Check if the knowledge graph has sufficient entities.

    Args:
        uri: Neo4j bolt URI.
        auth: Tuple of (username, password).
        min_entities: Minimum number of entities required.

    Returns:
        Status dict.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total = result.single()["total"]

            result = session.run(
                "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS cnt "
                "ORDER BY cnt DESC LIMIT 10"
            )
            label_counts = {r["label"]: r["cnt"] for r in result}

            driver.close()

            if total >= min_entities:
                return {
                    "check": "kg_populated",
                    "status": "PASS",
                    "message": f"KG has {total} entities (>= {min_entities})",
                    "details": {"total_entities": total, "by_label": label_counts},
                }
            else:
                return {
                    "check": "kg_populated",
                    "status": "FAIL",
                    "message": f"KG has only {total} entities (need >= {min_entities})",
                    "details": {"total_entities": total, "by_label": label_counts},
                }
    except Exception as exc:
        return {
            "check": "kg_populated",
            "status": "FAIL",
            "message": f"Cannot query KG: {exc}",
            "details": {"error": str(exc)},
        }


def check_vector_index(uri: str, auth: tuple) -> dict:
    """Check if vector search index exists.

    Args:
        uri: Neo4j bolt URI.
        auth: Tuple of (username, password).

    Returns:
        Status dict.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run("SHOW INDEXES YIELD name, type WHERE type = 'VECTOR'")
            indexes = [r["name"] for r in result]
            driver.close()

            if indexes:
                return {
                    "check": "vector_index",
                    "status": "PASS",
                    "message": f"Found {len(indexes)} vector index(es): {indexes}",
                    "details": {"indexes": indexes},
                }
            else:
                return {
                    "check": "vector_index",
                    "status": "FAIL",
                    "message": "No vector indexes found",
                    "details": {"indexes": []},
                }
    except Exception as exc:
        return {
            "check": "vector_index",
            "status": "FAIL",
            "message": f"Cannot check vector indexes: {exc}",
            "details": {"error": str(exc)},
        }


def check_communities(uri: str, auth: tuple) -> dict:
    """Check if community detection has been run.

    Args:
        uri: Neo4j bolt URI.
        auth: Tuple of (username, password).

    Returns:
        Status dict.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n.community_id IS NOT NULL "
                "RETURN count(n) AS nodes_with_community, "
                "count(DISTINCT n.community_id) AS n_communities"
            )
            record = result.single()
            n_nodes = record["nodes_with_community"]
            n_communities = record["n_communities"]
            driver.close()

            if n_communities > 0:
                return {
                    "check": "communities",
                    "status": "PASS",
                    "message": f"Found {n_communities} communities ({n_nodes} assigned nodes)",
                    "details": {"n_communities": n_communities, "n_nodes": n_nodes},
                }
            else:
                return {
                    "check": "communities",
                    "status": "FAIL",
                    "message": "No community assignments found. Run community detection first.",
                    "details": {"n_communities": 0, "n_nodes": 0},
                }
    except Exception as exc:
        return {
            "check": "communities",
            "status": "FAIL",
            "message": f"Cannot check communities: {exc}",
            "details": {"error": str(exc)},
        }


def check_api_key() -> dict:
    """Check if Anthropic API key is configured.

    Returns:
        Status dict.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:]
        return {
            "check": "api_key",
            "status": "PASS",
            "message": f"ANTHROPIC_API_KEY is set ({masked})",
            "details": {"key_length": len(api_key)},
        }
    else:
        return {
            "check": "api_key",
            "status": "FAIL",
            "message": "ANTHROPIC_API_KEY is not set",
            "details": {},
        }


def check_datasets() -> dict:
    """Check if required datasets exist.

    Returns:
        Status dict.
    """
    base = Path(__file__).resolve().parent.parent / "datasets"

    required = {
        "regulatory_questions_200.json": 200,
        "benchmark_50.json": 50,
    }

    found = {}
    missing = []

    for filename, expected_count in required.items():
        filepath = base / filename
        if filepath.exists():
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                questions = data.get("questions", data if isinstance(data, list) else [])
                found[filename] = len(questions)
            except Exception:
                found[filename] = -1
        else:
            missing.append(filename)

    if not missing and all(v > 0 for v in found.values()):
        return {
            "check": "datasets",
            "status": "PASS",
            "message": f"All datasets found: {found}",
            "details": {"found": found, "directory": str(base)},
        }
    else:
        return {
            "check": "datasets",
            "status": "FAIL",
            "message": f"Missing datasets: {missing}",
            "details": {"found": found, "missing": missing, "directory": str(base)},
        }


def check_baselines_importable() -> dict:
    """Check if baseline modules can be imported.

    Returns:
        Status dict.
    """
    try:
        from baselines import (
            VectorRAGBaseline, MSGraphRAGBaseline,
            HybridRAGBaseline, NoRetrievalBaseline,
        )
        from ablation_baselines import (
            WithoutGraphBaseline, WithoutVectorBaseline,
            GraphOnlyBaseline, CommunityOnlyBaseline,
        )
        return {
            "check": "baselines_importable",
            "status": "PASS",
            "message": "All 8 baseline classes importable",
            "details": {"classes": 8},
        }
    except Exception as exc:
        return {
            "check": "baselines_importable",
            "status": "FAIL",
            "message": f"Import failed: {exc}",
            "details": {"error": str(exc)},
        }


def check_judge_importable() -> dict:
    """Check if LLM judge module can be imported.

    Returns:
        Status dict.
    """
    try:
        from llm_judge import LLMJudge, SimulatedJudge, JudgeResult
        return {
            "check": "judge_importable",
            "status": "PASS",
            "message": "LLMJudge, SimulatedJudge, JudgeResult importable",
            "details": {"classes": 3},
        }
    except Exception as exc:
        return {
            "check": "judge_importable",
            "status": "FAIL",
            "message": f"Import failed: {exc}",
            "details": {"error": str(exc)},
        }


def run_all_checks(
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_auth: tuple = ("neo4j", "panelbox_graphrag"),
) -> list[dict]:
    """Run all 8 prerequisite checks.

    Args:
        neo4j_uri: Neo4j connection URI.
        neo4j_auth: Neo4j authentication tuple.

    Returns:
        List of check result dictionaries.
    """
    results = []

    # Infrastructure checks
    results.append(check_neo4j_connection(neo4j_uri, neo4j_auth))
    results.append(check_kg_populated(neo4j_uri, neo4j_auth))
    results.append(check_vector_index(neo4j_uri, neo4j_auth))
    results.append(check_communities(neo4j_uri, neo4j_auth))

    # Configuration checks
    results.append(check_api_key())
    results.append(check_datasets())

    # Code checks
    results.append(check_baselines_importable())
    results.append(check_judge_importable())

    return results


def print_results(results: list[dict]) -> None:
    """Print check results in a formatted table.

    Args:
        results: List of check result dictionaries.
    """
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    print(f"\n{'='*70}")
    print(f"  Prerequisite Check Results ({passed}/{total} passed)")
    print(f"{'='*70}")

    for r in results:
        icon = "[PASS]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {icon} {r['check']:25s} {r['message']}")

    print(f"\n  {'All prerequisites met!' if passed == total else f'{total - passed} check(s) failed.'}")

    if passed < total:
        print("\n  Failed checks need to be resolved before running live experiments.")
        print("  You can still run experiments in simulation mode: --simulate")

    print()


def main():
    """Entry point for prerequisite checks."""
    parser = argparse.ArgumentParser(
        description="Check prerequisites for live experiment execution",
    )
    parser.add_argument(
        "--neo4j-uri",
        type=str,
        default="bolt://localhost:7687",
        help="Neo4j connection URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--neo4j-user",
        type=str,
        default="neo4j",
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--neo4j-pass",
        type=str,
        default="panelbox_graphrag",
        help="Neo4j password",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    results = run_all_checks(
        neo4j_uri=args.neo4j_uri,
        neo4j_auth=(args.neo4j_user, args.neo4j_pass),
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)

    # Exit with error code if any check failed
    passed = sum(1 for r in results if r["status"] == "PASS")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
