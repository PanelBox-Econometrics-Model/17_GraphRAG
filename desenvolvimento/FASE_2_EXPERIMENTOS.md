# FASE 2: Experimentos e Ablation Study

**Duracao**: 3 meses
**Objetivo**: Ablation study completo, analise de custo, estudos de caso
**Pre-requisitos**: FASE 1 completa (dataset, metricas, baselines)

---

## Tarefa 2.1: Ablation Study

**Duracao**: 4-6 semanas
**Entrega**: `simulacoes/ablation_results/`

### Experimentos de Ablacao:

**A1: Sem ontologia restrita**
- Remover validacao de tipos em `_parse_response()`
- Aceitar todos os entity types e relation types retornados pelo LLM
- Medir: precision de triplas, relevancia dos resultados, ruido no grafo

**A2: Sem pesos adaptativos**
- Substituir `RETRIEVAL_WEIGHT_PRESETS` por pesos iguais (0.33/0.33/0.34)
- Remover entity boosting em `_compute_retrieval_weights()`
- Medir: nDCG@5, MRR por tipo de intencao

**A3: Sem entity resolution**
- Desativar `EntityResolver` no pipeline
- Manter entidades como extraidas (com duplicatas)
- Medir: numero de nos no grafo, cobertura de travessia, fragmentacao

**A4: Line-based chunking (sem AST)**
- Substituir `PythonParser` por chunking por linhas (500 tokens por chunk)
- Manter MarkdownParser e NotebookParser
- Medir: Recall@5 para queries CODE_EXAMPLE, coerencia dos chunks

**A5: Sem community summaries**
- Remover `CommunityRetriever` do pipeline
- Pesos: redistribuir peso de community entre graph e vector
- Medir: qualidade em queries GENERAL e EXPLANATION

**A6: Individual API calls (sem Batch)**
- Forcar `_fallback_individual()` em vez de `_process_batch()`
- Medir: custo total em USD, tempo total de extracao

**A7: Full reprocessing (sem incremental)**
- Ignorar manifesto, reprocessar todos os arquivos
- Medir: tempo total, custo total, comparar com incremental

**A8: Vector-only baseline**
- Remover GraphRetriever e CommunityRetriever
- graph=0.0, vector=1.0, community=0.0
- Medir: nDCG@5, MRR, Hit Rate@3 (RAG puro como baseline)

### Formato de Resultados:

```json
{
  "experiment": "A1_no_ontology",
  "dataset_size": 50,
  "metrics": {
    "ndcg_5": 0.XX,
    "ndcg_10": 0.XX,
    "mrr": 0.XX,
    "hit_rate_3": 0.XX,
    "precision_5": 0.XX,
    "recall_5": 0.XX
  },
  "by_intent": {
    "VALIDATION": {"ndcg_5": 0.XX, "mrr": 0.XX},
    "COMPARISON": {"ndcg_5": 0.XX, "mrr": 0.XX},
    ...
  },
  "cost_usd": 0.XX,
  "latency_ms": 0.XX
}
```

---

## Tarefa 2.2: Analise de Custo Detalhada

**Duracao**: 2 semanas
**Entrega**: `simulacoes/cost_analysis/`

### Metricas:
- [ ] Custo de indexacao por stage (discovery, chunking, extraction, resolution, loading)
- [ ] Comparacao: Batch API vs individual calls
- [ ] Cache hit rates por tipo de chunk
- [ ] Reducao incremental: % de chunks pulados em re-runs
- [ ] Custo total para processar PanelBox completo (first run vs re-run)
- [ ] Custo por query (retrieval + generation)
- [ ] Projecao: custo para codebases de 10x, 100x tamanho

### Tabela Alvo:

| Stage | Tokens | Custo (USD) | % do Total |
|-------|--------|-------------|------------|
| Triple Extraction (Batch) | X | $X.XX | X% |
| Triple Extraction (Individual, se batch falhar) | X | $X.XX | X% |
| Community Summarization | X | $X.XX | X% |
| Embedding | X | $X.XX | X% |
| Query (retrieval + generation) | X | $X.XX | X% |
| **Total First Run** | **X** | **$X.XX** | **100%** |
| **Total Re-Run (incremental, 10% changed)** | **X** | **$X.XX** | **X%** |

---

## Tarefa 2.3: Estudos de Caso Qualitativos

**Duracao**: 2 semanas
**Entrega**: `aplicacoes/case_studies/`

### Caso 1: Query de Validacao
- Pergunta: "Quais testes devo rodar antes de usar System GMM em um painel com T=7 e N=100?"
- Mostrar: intent classification, retrieval weights, resultados de cada estrategia, fusao, resposta final
- Comparar: resposta do sistema completo vs vector-only vs static weights

### Caso 2: Query de Comparacao
- Pergunta: "Qual a diferenca entre Fixed Effects e Random Effects? Quando usar cada um?"
- Mostrar: entidades reconhecidas, graph traversal (ALTERNATIVE_TO edges), vector results, fusao
- Comparar: com e sem entity resolution (FE -> FixedEffects)

### Caso 3: Query de Codigo
- Pergunta: "Me mostre como estimar um painel dinamico com dados desbalanceados usando PanelBox"
- Mostrar: intent=CODE_EXAMPLE, vector weight=0.6, chunks de codigo AST recuperados
- Comparar: AST chunks vs line-based chunks

### Caso 4: Query Geral
- Pergunta: "O que o PanelBox pode fazer?"
- Mostrar: intent=GENERAL, community weight=0.4, community summaries usados
- Comparar: com e sem community summaries

---

## Tarefa 2.4: Analise Estatistica

**Duracao**: 1-2 semanas
**Entrega**: `simulacoes/statistical_tests/`

### Testes:
- [ ] Teste de significancia (paired t-test ou Wilcoxon) para nDCG entre sistema completo e cada baseline
- [ ] Intervalo de confianca para cada metrica
- [ ] Effect size (Cohen's d) para as diferencas
- [ ] Analise por tipo de intencao: qual componente mais impacta cada tipo?

---

## Criterios de Conclusao

FASE 2 esta completa quando:
- [ ] 8 experimentos de ablacao executados com resultados
- [ ] Analise de custo completa com tabelas
- [ ] 4 estudos de caso qualitativos documentados
- [ ] Testes estatisticos de significancia executados
- [ ] Todas as figuras e tabelas geradas

---

*Status: Pendente*
*Inicio previsto: Maio 2026*
