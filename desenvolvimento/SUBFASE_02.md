# Subfase 02 - Experimentos e Benchmarks

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: SUBFASE_01
**Bloqueia**: SUBFASE_03, SUBFASE_04

## Objetivo

Projetar e executar 5 experimentos comparando GraphRAG multi-estrategia contra baselines (VectorRAG, MS GraphRAG, HybridRAG, No-retrieval) em tarefas financeiras. Coletar metricas quantitativas de alucinacao, economia de tokens, velocidade e benchmark completo.

## Descricao Tecnica

**Sistema GraphRAG**: Implementacao em `/home/guhaase/projetos/panelbox/graphrag/`
- Intent Parser: `src/retrieval/intent_parser.py` (6 intent types)
- Graph Retriever: `src/retrieval/graph_retriever.py` (N-hop Cypher)
- Vector Retriever: `src/retrieval/vector_retriever.py` (cosine similarity)
- Community Retriever: `src/retrieval/community_retriever.py` (Leiden summaries)
- Context Ranker: `src/retrieval/context_ranker.py` (weighted fusion)
- Engine: `src/retrieval/engine.py` (orchestrator)

**Baselines a implementar**:
1. VectorRAG: Embedding-only retrieval (same LLM, no graph)
2. MS GraphRAG: Leiden communities + global summarization (sem multi-strategy)
3. HybridRAG: Graph + Vector sem Community (Sarmah et al., 2024)
4. No-retrieval: Claude sem contexto externo

**Metricas**:
- Alucinacao: Faithfulness, Grounding rate, Factual accuracy
- Tokens: tokens_per_query, cost_per_1000_queries, indexing_cost_per_doc
- Velocidade: latency_p50, latency_p95, cache_hit_rate
- Benchmark: entity_coverage, concept_coverage, source_attribution, response_quality

**Arquivos a criar**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/datasets/regulatory_questions_200.json`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/datasets/benchmark_50.json`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/scripts/run_experiments.py`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/scripts/baselines.py`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/results/*.json`

## INSTRUCAO CRITICA

**ANTES de executar qualquer experimento**, verifique que o KG financeiro esta funcional:
```bash
# Verificar Neo4j esta rodando
curl -s http://localhost:7474 || echo "Neo4j nao esta rodando"

# Contar triplas no grafo
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'panelbox_graphrag'))
with driver.session() as s:
    r = s.run('MATCH (n) RETURN count(n) as nodes')
    print(f'Nodes: {r.single()[\"nodes\"]}')
    r = s.run('MATCH ()-[r]->() RETURN count(r) as rels')
    print(f'Relationships: {r.single()[\"rels\"]}')
"
```

### Etapa 1: Criar dataset de 200 perguntas regulatorias

Criar JSON com 200 perguntas sobre Basel III e LGPD com ground truth:
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Quais sao os requisitos minimos de capital sob Basel III Pilar 1?",
      "category": "compliance",
      "difficulty": "simple",
      "ground_truth": "Basel III Pilar 1 requer...",
      "source_articles": ["Basel III, Pilar 1, Secao 2"],
      "requires_multi_hop": false
    }
  ]
}
```

Distribuicao: 40% compliance, 25% analise financeira, 20% multi-hop, 10% comparacao, 5% auditoria.

### Etapa 2: Criar benchmark de 50 perguntas financeiras

Subset focado em 5 categorias com scoring system:
- Compliance regulatorio (15 perguntas, peso 30%)
- Analise financeira (12 perguntas, peso 25%)
- Raciocinio multi-hop (10 perguntas, peso 20%)
- Comparacao (8 perguntas, peso 15%)
- Auditoria (5 perguntas, peso 10%)

### Etapa 3: Implementar baselines

Implementar 3 baselines em Python:
1. **VectorRAG**: Usar apenas vector_retriever com full weight (1.0)
2. **MS GraphRAG**: Usar graph + community sem vector (weights: graph=0.6, community=0.4)
3. **HybridRAG**: Usar graph + vector sem community (weights: graph=0.5, vector=0.5)

### Etapa 4: Executar Experimento 1 (Alucinacao)

- Rodar 200 perguntas regulatorias em cada sistema
- Medir: Faithfulness, Grounding rate, Factual accuracy
- Anotar cada resposta (automatico via LLM-as-judge + sample manual)
- Tabular resultados comparativos

### Etapa 5: Executar Experimento 2 (Economia de Tokens)

- Medir tokens consumidos em cada etapa do pipeline
- Comparar: full-document vs structured retrieval
- Comparar: individual API vs Batch API para indexacao
- Calcular custo por 1000 queries

### Etapa 6: Executar Experimento 3 (Velocidade)

- Benchmark de latencia end-to-end (p50, p95)
- Comparar: serial vs paralelo retrieval
- Medir cache hit rate
- Comparar throughput de indexacao

### Etapa 7: Executar Experimento 5 (Benchmark Completo)

- Rodar 50 perguntas financeiras em todos os sistemas
- Scoring: entity_coverage (40%) + concept_coverage (30%) + source_attribution (20%) + response_quality (10%)
- Tabular resultados por categoria e sistema

## Criterios de Aceite

- [x] Dataset de 200 perguntas regulatorias criado com ground truth
- [x] Benchmark de 50 perguntas financeiras criado com scoring system
- [x] Baseline VectorRAG implementado e funcional
- [x] Baseline MS GraphRAG implementado e funcional
- [x] Baseline HybridRAG implementado e funcional
- [x] Experimento 1 (alucinacao) executado com resultados tabulados
- [x] Experimento 2 (tokens) executado com resultados tabulados
- [x] Experimento 3 (velocidade) executado com resultados tabulados
- [x] Experimento 5 (benchmark) executado com resultados tabulados
- [x] Tabelas comparativas geradas para cada experimento
- [x] Resultados salvos em JSON em simulacoes/results/

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Resultados GraphRAG vs VectorRAG sem diferenca significativa | Media | Alto | Focar em queries multi-hop onde diferenca e maior |
| LLM-as-judge inconsistente | Media | Medio | Calibrar com amostra manual de 50 perguntas |
| Custos de API altos para 200 perguntas x 4 sistemas | Alta | Medio | Usar Claude Haiku para baselines, Batch API |
| Neo4j lento para queries complexas | Baixa | Medio | Indexar propriamente, otimizar Cypher |

**End of Specification**
