# FASE 3: Escrita do Manuscrito

**Duracao**: 3 meses
**Objetivo**: Draft completo do paper com todas as secoes, figuras e tabelas
**Pre-requisitos**: FASE 2 completa (resultados experimentais)

---

## Tarefa 3.1: Secao 1 - Introduction (2-3 paginas)

**Duracao**: 1 semana

### Conteudo:
- [ ] Motivacao: por que instituicoes financeiras precisam de GraphRAG especializado
- [ ] Problema: RAG generico falha em perguntas que exigem relacoes estruturadas
- [ ] Contribuicoes: lista numerada das 8 contribuicoes
- [ ] Resultados preview: "+X% nDCG vs vector-only, -Y% custo vs full reprocessing"
- [ ] Estrutura do paper

---

## Tarefa 3.2: Secao 2 - Related Work (3-4 paginas)

**Duracao**: 2 semanas

### Subsecoes:
- [ ] 2.1 Retrieval-Augmented Generation
- [ ] 2.2 Knowledge Graphs for Information Retrieval
- [ ] 2.3 GraphRAG: From Local to Global
- [ ] 2.4 Domain-Specific Knowledge Graph Construction
- [ ] 2.5 Cost Optimization in LLM Pipelines
- [ ] Tabela comparativa: nosso sistema vs existentes

---

## Tarefa 3.3: Secao 3 - System Architecture (5-6 paginas)

**Duracao**: 3 semanas

### Subsecoes:
- [ ] 3.1 Overview (pipeline diagram - Figura 1)
- [ ] 3.2 Ingestion Pipeline
  - 3.2.1 Source Discovery and Change Detection
  - 3.2.2 Multi-Format Chunking (AST, Markdown, Notebook)
  - 3.2.3 Ontology-Constrained Triple Extraction
  - 3.2.4 Entity Resolution
  - 3.2.5 Graph Loading and Schema Management
- [ ] 3.3 Retrieval Pipeline
  - 3.3.1 Intent Classification
  - 3.3.2 Multi-Strategy Retrieval (Graph, Vector, Community)
  - 3.3.3 Context Ranking and Fusion
- [ ] 3.4 Generation Pipeline

---

## Tarefa 3.4: Secao 4 - Domain Specialization (4-5 paginas)

**Duracao**: 2 semanas

### Subsecoes:
- [ ] 4.1 Domain Ontology Design (Tabela: 10 types + 14 relations)
- [ ] 4.2 Ontology-Constrained Extraction with Few-Shot Learning
- [ ] 4.3 Entity Resolution with Domain Alias Dictionaries
- [ ] 4.4 Domain-Expert Community Summarization
- [ ] 4.5 Discussion: Generalizability to Other Domains

---

## Tarefa 3.5: Secao 5 - Intent-Adaptive Retrieval (3-4 paginas)

**Duracao**: 2 semanas

### Subsecoes:
- [ ] 5.1 Intent Classification Framework (6 types, regex-based, zero-cost)
- [ ] 5.2 Weight Preset Calibration (Tabela: 6x3 weight matrix)
- [ ] 5.3 Entity-Aware Weight Boosting
- [ ] 5.4 Context Ranking Algorithm (normalize, weight, deduplicate)
- [ ] Figura: Intent weight heatmap

---

## Tarefa 3.6: Secao 6 - Cost Optimization (2-3 paginas)

**Duracao**: 1 semana

### Subsecoes:
- [ ] 6.1 Batch API Integration (50% cost reduction)
- [ ] 6.2 Per-Chunk Result Caching
- [ ] 6.3 Incremental Processing with Content Hashing
- [ ] 6.4 Cost Tracking and Projection
- [ ] Tabela: custo por stage, first run vs re-run

---

## Tarefa 3.7: Secao 7 - Experimental Evaluation (6-8 paginas)

**Duracao**: 3 semanas

### Subsecoes:
- [ ] 7.1 Experimental Setup (dataset, metricas, baselines)
- [ ] 7.2 Ablation Study Results (Tabela principal)
- [ ] 7.3 Impact by Intent Type (nDCG por tipo)
- [ ] 7.4 Cost Analysis (Tabela de custos)
- [ ] 7.5 Qualitative Case Studies (4 exemplos end-to-end)
- [ ] 7.6 Statistical Significance

---

## Tarefa 3.8: Secoes 8-9 - Discussion and Conclusion (3-5 paginas)

**Duracao**: 1 semana

### Discussion:
- [ ] Limitacoes (dominio especifico, tamanho do dataset, avaliacao)
- [ ] Generalizacao para outros dominios (medicina, direito, engenharia)
- [ ] Comparacao com abordagens emergentes (AgenticRAG, etc.)
- [ ] Implicacoes para instituicoes financeiras

### Conclusion:
- [ ] Resumo das contribuicoes
- [ ] Principais resultados quantitativos
- [ ] Trabalho futuro (avaliacao com usuarios, outros dominios, auto-tuning de pesos)

---

## Tarefa 3.9: Figuras e Tabelas

**Duracao**: 2 semanas (paralelo com escrita)

### Figuras:
- [ ] Fig 1: Pipeline overview (ingestion + retrieval)
- [ ] Fig 2: Ontology schema (grafo visual)
- [ ] Fig 3: AST chunking example
- [ ] Fig 4: Triple extraction flow
- [ ] Fig 5: Entity resolution pipeline
- [ ] Fig 6: Intent weight heatmap (6x3)
- [ ] Fig 7: Ablation results (bar chart)
- [ ] Fig 8: Cost comparison (bar chart)
- [ ] Fig 9: Knowledge graph visualization (subgrafo real)
- [ ] Fig 10: Query walkthrough example

### Tabelas:
- [ ] Tab 1: Feature comparison with existing systems
- [ ] Tab 2: Ontology definition
- [ ] Tab 3: Retrieval weight presets
- [ ] Tab 4: Ablation study results
- [ ] Tab 5: Benchmark results (nDCG, MRR, Hit Rate)
- [ ] Tab 6: Cost analysis by stage
- [ ] Tab 7: Entity resolution precision/recall
- [ ] Tab 8: Qualitative response examples

---

## Criterios de Conclusao

FASE 3 esta completa quando:
- [ ] Todas as 9 secoes escritas
- [ ] 10 figuras produzidas
- [ ] 8 tabelas produzidas
- [ ] Referencias completas (BibTeX)
- [ ] Draft lido por ao menos 1 reviewer interno

---

*Status: Pendente*
*Inicio previsto: Agosto 2026*
