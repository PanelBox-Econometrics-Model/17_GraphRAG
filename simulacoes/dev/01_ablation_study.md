# TEST 01 — Ablation Study (Table 7)

## Objetivo

Implementar as 3 configuracoes faltantes do ablation study e executar o benchmark
de 50 questions com todas as 7 configuracoes, gerando os resultados da Table 7 do paper.

## Contexto

O paper apresenta 7 configuracoes na Table 7:

| # | Configuracao                        | Status   |
|---|-------------------------------------|----------|
| 1 | Full system (Graph + Vector + Community) | JA EXISTE (MultiStrategy) |
| 2 | Without Graph retriever             | FALTANDO |
| 3 | Without Vector retriever            | FALTANDO |
| 4 | Without Community retriever         | JA EXISTE (~HybridRAG, mas pesos diferentes) |
| 5 | Graph only                          | FALTANDO |
| 6 | Vector only                         | JA EXISTE (VectorRAG) |
| 7 | Community only                      | FALTANDO |

A config 4 (Without Community) e a config 6 (Vector only) ja existem como baselines
em `baselines.py`, mas com pesos fixos que nao correspondem exatamente ao ablation.
No ablation, queremos medir o impacto de REMOVER um componente do sistema completo,
mantendo os demais com os mesmos pesos relativos.

## Valores esperados (Table 7 do paper)

| Configuracao                          | Weighted Score | Delta     |
|---------------------------------------|---------------|-----------|
| Full system (Graph + Vector + Community) | 87.95%     | ---       |
| Without Graph retriever               | 71.82%        | -16.13 pp |
| Without Vector retriever              | 78.44%        | -9.51 pp  |
| Without Community retriever           | 83.21%        | -4.74 pp  |
| Graph only                            | 74.58%        | -13.37 pp |
| Vector only                           | 59.49%        | -28.46 pp |
| Community only                        | 52.13%        | -35.82 pp |

## Arquivos a criar/modificar

### 1. Novo arquivo: `simulacoes/scripts/ablation_baselines.py`

Criar 4 novas classes que herdam de `BaseRetrieval` (de `baselines.py`):

```python
class WithoutGraphBaseline(BaseRetrieval):
    """Full system minus graph retriever."""
    # Pesos: graph=0.0, vector e community redistribuidos
    # Original full: graph=variavel por intent, vector=variavel, community=variavel
    # Ablation: zera graph, normaliza vector+community para somar 1.0
    WEIGHTS = {"graph": 0.0, "vector": 0.67, "community": 0.33}

class WithoutVectorBaseline(BaseRetrieval):
    """Full system minus vector retriever."""
    WEIGHTS = {"graph": 0.7, "vector": 0.0, "community": 0.3}

class GraphOnlyBaseline(BaseRetrieval):
    """Only graph retriever active."""
    WEIGHTS = {"graph": 1.0, "vector": 0.0, "community": 0.0}

class CommunityOnlyBaseline(BaseRetrieval):
    """Only community retriever active."""
    WEIGHTS = {"graph": 0.0, "vector": 0.0, "community": 1.0}
```

### 2. Modificar: `simulacoes/scripts/run_experiments.py`

Adicionar `experiment_6_ablation()` que:

1. Carrega as 50 questions do benchmark (`datasets/benchmark_50.json`)
2. Instancia todas as 7 configuracoes
3. Para cada configuracao:
   - Executa retrieval + generation para as 50 questions
   - Calcula os 4 sub-scores: entity coverage, concept coverage, source attribution, response quality
   - Calcula o weighted score: 0.4*entity + 0.3*concept + 0.2*source + 0.1*quality
4. Calcula o delta (diferenca em pp) de cada configuracao vs full system
5. Salva resultado em `results/experiment_6_ablation.json`

### 3. Novo resultado: `simulacoes/results/experiment_6_ablation.json`

Estrutura esperada:

```json
{
  "experiment": "ablation_study",
  "dataset": "benchmark_50.json",
  "num_questions": 50,
  "seed": 42,
  "configurations": {
    "full_system": {
      "components": ["graph", "vector", "community"],
      "weighted_score": 0.8795,
      "entity_coverage": 0.8805,
      "concept_coverage": 0.8513,
      "source_attribution": 0.9475,
      "response_quality": 0.8246,
      "delta_pp": 0.0
    },
    "without_graph": {
      "components": ["vector", "community"],
      "weighted_score": 0.7182,
      "delta_pp": -16.13
    },
    "without_vector": {
      "components": ["graph", "community"],
      "weighted_score": 0.7844,
      "delta_pp": -9.51
    },
    "without_community": {
      "components": ["graph", "vector"],
      "weighted_score": 0.8321,
      "delta_pp": -4.74
    },
    "graph_only": {
      "components": ["graph"],
      "weighted_score": 0.7458,
      "delta_pp": -13.37
    },
    "vector_only": {
      "components": ["vector"],
      "weighted_score": 0.5949,
      "delta_pp": -28.46
    },
    "community_only": {
      "components": ["community"],
      "weighted_score": 0.5213,
      "delta_pp": -35.82
    }
  },
  "analysis": {
    "most_impactful_component": "graph",
    "graph_contribution_pp": 16.13,
    "vector_contribution_pp": 9.51,
    "community_contribution_pp": 4.74,
    "complementarity": "full_system > best_single_component (87.95 > 74.58)"
  }
}
```

## Modo de execucao

### Simulacao (imediato)

Adicionar parametros ao `SimulationEngine` para as 4 novas configuracoes, seguindo
o mesmo padrao das demais: valores esperados + ruido Gaussiano com seed 42.

```bash
python run_experiments.py --experiment 6 --simulate
```

### Live (apos completar TEST 05)

Com o KG populado e API configurada:

```bash
python run_experiments.py --experiment 6
```

Para cada configuracao, o engine.py recebe os pesos customizados e executa o
pipeline real. O benchmark scorer calcula os 4 sub-scores e o weighted score.

## Metricas de scoring (mesmo do Experiment 5)

- **Entity Coverage (40%)**: fracao das expected_entities presentes na resposta
- **Concept Coverage (30%)**: fracao dos expected_concepts presentes na resposta
- **Source Attribution (20%)**: fracao das source_references citadas na resposta
- **Response Quality (10%)**: heuristica de comprimento + estrutura + vocabulario tecnico
- **Weighted Score**: 0.4*EC + 0.3*CC + 0.2*SA + 0.1*RQ

## Dependencias

- `baselines.py` (classes base)
- `datasets/benchmark_50.json` (50 questions com expected entities/concepts/references)
- `graphrag/src/retrieval/engine.py` (aceita pesos customizados)

## Criterios de aceite

1. As 7 configuracoes executam sem erro
2. Full system score >= 85%
3. Remover qualquer componente reduz o score (delta negativo para todos)
4. Full system > melhor componente individual (confirma complementaridade)
5. Graph e o componente mais impactful (maior delta quando removido)
6. Resultados consistentes entre execucoes com mesmo seed
