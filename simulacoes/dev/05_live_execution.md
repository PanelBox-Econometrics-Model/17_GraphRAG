# TEST 05 — Execucao Live (Modo Real)

## Objetivo

Executar todos os experimentos do paper em modo real (live), substituindo os
resultados de simulacao por medicoes empiricas reais contra o knowledge graph
no Neo4j e geracao via Claude API.

## Contexto

Atualmente todos os resultados sao gerados em modo `--simulate`:
- `run_summary.json` → `"mode": "simulation"`, `"total_runtime_seconds": 0.03`
- O `SimulationEngine` usa valores hardcoded + ruido Gaussiano com seed 42
- As funcoes live (`_evaluate_hallucination_live()`, etc.) sao placeholders

O paper apresenta os resultados como empiricos:

> "Empirical evaluation across 200 regulatory questions and a 50-question
> financial benchmark..."

## Pre-requisitos

| # | Pre-requisito | Depende de | Status |
|---|--------------|------------|--------|
| 1 | Neo4j rodando com KG populado | TEST 02 | Pendente |
| 2 | 150 docs ingeridos | TEST 02 | Pendente |
| 3 | Embeddings e communities gerados | TEST 02 | Pendente |
| 4 | Ablation baselines implementadas | TEST 01 | Pendente |
| 5 | LLM judge implementado | TEST 03 | Pendente |
| 6 | API key Anthropic configurada | Infra | Disponivel |
| 7 | PostgreSQL rodando | Infra | Disponivel |

## Arquitetura da execucao live

```
                    ┌─────────────────────────────┐
                    │     run_experiments.py       │
                    │     (--live --judge llm)     │
                    └──────────┬──────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
     ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
     │ Exp 1     │      │ Exp 2     │      │ Exp 3     │
     │ Halluc.   │      │ Tokens    │      │ Speed     │
     └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
           │                   │                   │
     ┌─────▼─────────────────▼───────────────────▼─────┐
     │              retrieval engine                     │
     │  (graph + vector + community retrievers)          │
     │  + 4 baselines (VectorRAG, MS, Hybrid, NoRetr)    │
     └─────────┬──────────────┬──────────────┬──────────┘
               │              │              │
         ┌─────▼────┐  ┌─────▼────┐  ┌──────▼─────┐
         │  Neo4j   │  │  Claude  │  │  LLM Judge │
         │  KG+Vec  │  │  API     │  │  (Haiku)   │
         └──────────┘  └──────────┘  └────────────┘
```

## Arquivos a criar/modificar

### 1. Modificar: `simulacoes/scripts/run_experiments.py`

Implementar as funcoes live atualmente placeholder:

#### `_evaluate_hallucination_live()`

```python
def _evaluate_hallucination_live(
    self,
    questions: list[dict],
    systems: dict,      # {name: baseline_instance}
    judge: LLMJudge,
) -> dict:
    """Run Experiment 1 against real systems.

    For each question x each system:
      1. Execute retrieval pipeline (real Neo4j queries)
      2. Generate response (real Claude API call)
      3. Evaluate with LLM judge (real Claude API call)
      4. Record metrics (faithfulness, accuracy, grounding)
      5. Record tokens (input, output, context)
      6. Record latency (per stage)
    """
    results = {}

    for system_name, system in systems.items():
        system_results = []

        for q in questions:
            # Step 1: Retrieve
            start = time.time()
            retrieval_result = system.retrieve(q["question"])
            retrieval_ms = (time.time() - start) * 1000

            # Step 2: Generate
            start = time.time()
            generation_result = system.generate(
                q["question"],
                retrieval_result.formatted_context,
            )
            generation_ms = (time.time() - start) * 1000

            # Step 3: Judge
            judge_result = judge.evaluate_full(
                question_id=str(q["id"]),
                system_name=system_name,
                query=q["question"],
                context=retrieval_result.formatted_context,
                response=generation_result.text,
                ground_truth=q["ground_truth"],
                source_articles=q.get("source_articles", []),
            )

            system_results.append({
                "question_id": q["id"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "faithfulness": judge_result.faithfulness_score,
                "factual_accuracy": judge_result.factual_accuracy_score,
                "grounding": judge_result.grounding_score,
                "context_tokens": retrieval_result.token_count,
                "output_tokens": generation_result.output_tokens,
                "retrieval_latency_ms": retrieval_ms,
                "generation_latency_ms": generation_ms,
                "total_latency_ms": retrieval_ms + generation_ms,
            })

        results[system_name] = system_results

    return results
```

#### `_measure_tokens_live()`

```python
def _measure_tokens_live(
    self,
    questions: list[dict],
    systems: dict,
) -> dict:
    """Measure real token consumption per system.

    Token counts come from the Claude API response.usage:
      - input_tokens (includes context + system prompt)
      - output_tokens
      - cache_creation_input_tokens
      - cache_read_input_tokens
    """
    # Reuse data from hallucination experiment if available
    # Otherwise, run retrieval + generation for each question x system
    pass
```

#### `_measure_latency_live()`

```python
def _measure_latency_live(
    self,
    questions: list[dict],
    systems: dict,
    n_runs: int = 3,
) -> dict:
    """Measure real latency with median of 3 runs.

    Stage breakdown:
      - Intent parsing (ms)
      - Retrieval execution (ms)
        - Graph retriever (ms)
        - Vector retriever (ms)
        - Community retriever (ms)
      - Ranking/fusion (ms)
      - Context formatting (ms)
      - LLM generation (ms)
      - Total end-to-end (ms)
    """
    # Run each question n_runs times
    # Take median of each timing
    pass
```

### 2. Modificar: `simulacoes/scripts/baselines.py`

Conectar as baselines ao Neo4j real:

```python
class BaseRetrieval:
    def __init__(
        self,
        neo4j_driver,          # Real Neo4j connection
        anthropic_client,      # Real Claude API client
        vector_index_name: str = "chunk_embeddings",
    ):
        self.driver = neo4j_driver
        self.client = anthropic_client
        # Initialize retrievers with real connections
        self.graph_retriever = GraphRetriever(neo4j_driver)
        self.vector_retriever = VectorRetriever(neo4j_driver, vector_index_name)
        self.community_retriever = CommunityRetriever(neo4j_driver)
```

### 3. Script de orquestracao: `simulacoes/scripts/run_live.sh`

```bash
#!/bin/bash
# Full live experiment execution

set -e

echo "=== GraphRAG Live Experiment Execution ==="
echo "Started: $(date)"

# Check prerequisites
echo "[1/8] Checking prerequisites..."
python scripts/check_prerequisites.py

# Ensure Neo4j is running
echo "[2/8] Checking Neo4j connection..."
python -c "from neo4j import GraphDatabase; d = GraphDatabase.driver('bolt://localhost:7687'); d.verify_connectivity(); d.close()"

# Run experiments sequentially
echo "[3/8] Running Experiment 1: Hallucination (200 questions x 5 systems)..."
python scripts/run_experiments.py --experiment 1 --live --judge-mode llm \
    --output results/live/experiment_1_hallucination.json

echo "[4/8] Running Experiment 2: Token Economy (200 questions x 6 systems)..."
python scripts/run_experiments.py --experiment 2 --live \
    --output results/live/experiment_2_tokens.json

echo "[5/8] Running Experiment 3: Speed Benchmark (200 questions, 3 runs)..."
python scripts/run_experiments.py --experiment 3 --live --n-runs 3 \
    --output results/live/experiment_3_speed.json

echo "[6/8] Running Experiment 5: Full Benchmark (50 questions x 5 systems)..."
python scripts/run_experiments.py --experiment 5 --live --judge-mode llm \
    --output results/live/experiment_5_benchmark.json

echo "[7/8] Running Experiment 6: Ablation Study (50 questions x 7 configs)..."
python scripts/run_experiments.py --experiment 6 --live --judge-mode llm \
    --output results/live/experiment_6_ablation.json

echo "[8/8] Generating summary..."
python scripts/run_experiments.py --summarize --input-dir results/live/ \
    --output results/live/run_summary.json

echo "=== Completed: $(date) ==="
echo "Results in: simulacoes/results/live/"
```

### 4. Script de verificacao de pre-requisitos

```python
# simulacoes/scripts/check_prerequisites.py

def check_all():
    checks = {
        "neo4j_connection": check_neo4j(),
        "neo4j_kg_populated": check_kg_stats(),  # >= 500 entities
        "neo4j_vector_index": check_vector_index(),
        "neo4j_communities": check_communities(),
        "anthropic_api_key": check_api_key(),
        "datasets_exist": check_datasets(),
        "baselines_importable": check_baselines(),
        "judge_importable": check_judge(),
    }

    all_ok = all(checks.values())
    for name, ok in checks.items():
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")

    if not all_ok:
        print("\nSome prerequisites are not met. Fix before running live.")
        sys.exit(1)
```

## Estrutura de resultados live

```
simulacoes/results/
├── run_summary.json                  # Simulacao (existente)
├── experiment_1_hallucination.json   # Simulacao (existente)
├── experiment_2_tokens.json          # Simulacao (existente)
├── experiment_3_speed.json           # Simulacao (existente)
├── experiment_4_security.json        # Simulacao (existente)
├── experiment_5_benchmark.json       # Simulacao (existente)
└── live/                             # NOVO: resultados reais
    ├── run_summary.json
    ├── experiment_1_hallucination.json
    ├── experiment_2_tokens.json
    ├── experiment_3_speed.json
    ├── experiment_5_benchmark.json
    ├── experiment_6_ablation.json
    └── metadata.json                 # Hardware, versions, timing
```

### `metadata.json`

```json
{
  "execution": {
    "mode": "live",
    "seed": 42,
    "start_time": "2026-03-10T10:00:00Z",
    "end_time": "2026-03-10T14:30:00Z",
    "total_runtime_seconds": 16200
  },
  "environment": {
    "cpu": "8 cores",
    "ram_gb": 32,
    "os": "Linux (WSL2)",
    "python_version": "3.11",
    "neo4j_version": "5.x",
    "postgresql_version": "16"
  },
  "models": {
    "generation": "claude-sonnet-4-20250514",
    "extraction": "claude-haiku-4-5-20251001",
    "judge": "claude-haiku-4-5-20251001",
    "embeddings": "all-MiniLM-L6-v2"
  },
  "knowledge_graph": {
    "total_entities": 727,
    "total_triples": 1500,
    "entity_types": 10,
    "relationship_types": 14,
    "communities": 45
  },
  "datasets": {
    "regulatory_questions": 200,
    "benchmark_questions": 50,
    "document_corpus": 150
  },
  "api_costs": {
    "generation_usd": 15.20,
    "judge_usd": 2.50,
    "total_usd": 17.70
  }
}
```

## Estimativa de custos e tempo

### Custos API

| Componente | Chamadas | Tokens estimados | Custo |
|-----------|---------|-----------------|-------|
| **Generation** (200 Q x 5 systems) | 1,000 | ~5M input, ~500K output | |
| — com Haiku | | | $6.00 |
| — com Sonnet | | | $22.50 |
| **Generation** (50 Q x 7 ablation) | 350 | ~1.8M input, ~175K output | |
| — com Haiku | | | $2.10 |
| — com Sonnet | | | $7.90 |
| **Latency** (200 Q x 5 sys x 3 runs) | 3,000 | ~15M input, ~1.5M output | |
| — com Haiku | | | $18.00 |
| — com Sonnet | | | $67.50 |
| **LLM Judge** (3,000 avaliacoes) | 3,000 | ~2.4M input, ~1.2M output | $2.50 |
| **Total com Haiku** | | | **~$28.60** |
| **Total com Sonnet** | | | **~$100.40** |

**Recomendacao**: Usar Haiku para geracao e judge. O paper nao especifica o modelo
de geracao, apenas diz "the same LLM for generation". Haiku e suficiente e economico.

### Tempo de execucao

| Experimento | Chamadas API | Tempo estimado |
|------------|-------------|----------------|
| Exp 1 (Hallucination) | 1,000 gen + 3,000 judge | ~60 min |
| Exp 2 (Tokens) | Reusar dados do Exp 1 | ~5 min (processamento) |
| Exp 3 (Speed, 3 runs) | 3,000 gen | ~120 min |
| Exp 5 (Benchmark) | 250 gen + 750 judge | ~20 min |
| Exp 6 (Ablation) | 350 gen + 1,050 judge | ~25 min |
| **Total** | | **~4 horas** |

Com Batch API (50% desconto, execucao async em ate 24h):
- Custo: ~$14.30 (metade)
- Tempo: resultados em 1-24h (async)

## Configuracoes de execucao

### Modo economico (recomendado para primeira execucao)

```bash
python run_experiments.py --live \
    --model claude-haiku-4-5-20251001 \
    --judge-model claude-haiku-4-5-20251001 \
    --max-questions 50 \
    --n-runs 1 \
    --seed 42
```

Custo estimado: ~$5-8

### Modo completo (para resultados finais)

```bash
python run_experiments.py --live \
    --model claude-haiku-4-5-20251001 \
    --judge-model claude-haiku-4-5-20251001 \
    --judge-mode llm \
    --n-runs 3 \
    --seed 42 \
    --batch-api \
    --output-dir results/live/
```

Custo estimado: ~$14-28

### Modo paper (para replicar exatamente o paper)

```bash
python run_experiments.py --live \
    --experiment all \
    --judge-mode llm \
    --n-runs 3 \
    --seed 42 \
    --output-dir results/live/
```

## Validacao dos resultados live vs simulados

Apos a execucao live, comparar com os resultados simulados:

```python
def compare_live_vs_simulated(live_dir, sim_dir):
    """Compare live vs simulated results.

    Expected:
      - Trends should match (same ranking of systems)
      - Absolute values may differ by 5-15%
      - If live results diverge significantly, investigate root causes
    """
    # Load both result sets
    # Compare system rankings (should be identical)
    # Compare absolute values (acceptable range)
    # Flag any anomalies
```

| Metrica | Sim valor | Live range aceitavel |
|---------|----------|---------------------|
| Faithfulness (ours) | 87.35% | 75-95% |
| Faithfulness (VectorRAG) | 72.88% | 60-85% |
| Token reduction vs full doc | 69.85% | 55-80% |
| Parallel p50 latency | 1,785ms | 1,000-3,000ms |
| Benchmark weighted score | 87.95% | 75-95% |

O mais importante e que os **rankings** (ours > HybridRAG > MS GraphRAG > VectorRAG > NoRetrieval)
se mantenham, mesmo que os valores absolutos variem.

## Criterios de aceite

1. Todos os experimentos executam sem erro em modo live
2. Resultados salvos em `results/live/` com metadata completa
3. Rankings de sistemas consistentes com simulacao
4. Faithfulness do MultiStrategy >= 75% (resultado real)
5. Token reduction vs FullDocument >= 50%
6. Parallel latency <= 3,000ms (p50)
7. Benchmark weighted score >= 75%
8. Custo total da execucao <= $30
9. metadata.json com informacoes de hardware, versoes, e custos

## Dependencias

- TEST 01 (ablation baselines)
- TEST 02 (corpus de 150 docs + KG populado)
- TEST 03 (LLM judge)
- Neo4j rodando com dados
- PostgreSQL rodando
- API key Anthropic
- `graphrag/src/retrieval/` (engine completa)
- `graphrag/src/ingestion/` (pipeline completa)

## Riscos e mitigacoes

| Risco | Probabilidade | Mitigacao |
|-------|--------------|-----------|
| Rate limiting da API | Media | Usar Batch API; adicionar retries com backoff |
| Custo excedendo $30 | Baixa | Monitorar custo em tempo real; modo economico primeiro |
| Neo4j timeout em queries complexas | Baixa | Indices criados; timeout configuravel |
| Resultados divergem muito do simulado | Media | Ajustar parametros do SimulationEngine para proxima iteracao |
| KG com poucos dados (< 500 entities) | Depende TEST 02 | Garantir que TEST 02 passa primeiro |
