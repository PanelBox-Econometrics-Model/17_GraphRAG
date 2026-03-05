# Paper 17: GraphRAG para Bibliotecas Econometricas

## Visao Geral

Sistema GraphRAG especializado em dominio que combina extracao de triplas com ontologia restrita, chunking baseado em AST, retrieval multi-estrategia com pesos adaptativos por intencao, e otimizacao de custos em producao. Aplicado ao PanelBox, biblioteca de econometria de painel.

**Status**: Em desenvolvimento - Sistema funcional implementado
**Periodico-alvo**: ACM Computing Surveys (Q1, IF ~23.8), ACM TOIS (Q1, IF ~5.4), Information Fusion (Q1, IF ~14.7)
**Alternativas**: EMNLP (Systems Track), NAACL (Industry Track), KDD (Applied Data Science)
**Tempo estimado**: 8-12 meses

## Por Que E Interessante?

- **Lacuna real**: Nenhum paper aplica GraphRAG a bibliotecas de econometria/financas quantitativas
- **8 contribuicoes novas**: Cada componente do sistema preenche uma lacuna especifica na literatura
- **Dominio de alta relevancia**: Instituicoes financeiras usam intensivamente econometria de painel
- **Sistema funcional**: Nao e teoria — temos implementacao completa rodando em producao
- **Ponte entre areas**: Conecta NLP, Knowledge Graphs, Software Engineering, e Econometria

## Contribuicoes Principais

### 1. Ontologia Restrita para Econometria (GAP 1)
10 entity types + 14 relation types especificos para panel data econometrics.
Nenhum GraphRAG existente opera neste dominio.

### 2. Retrieval Multi-Estrategia com Pesos Adaptativos (GAP 2)
6 tipos de intencao (VALIDATION, COMPARISON, RECOMMENDATION, EXPLANATION, CODE_EXAMPLE, GENERAL)
mapeados para distribuicoes de peso distintas entre 3 estrategias (graph, vector, community).
Boost dinamico baseado em entidades reconhecidas.

### 3. Otimizacao de Custos em 3 Camadas (GAP 3)
Batch API (50% desconto) + cache por chunk em disco + processamento incremental por SHA-256.
Nenhum paper trata otimizacao de custo na fase de indexacao/extracao.

### 4. Resolucao de Entidades com Alias de Dominio (GAP 4)
Pipeline de 4 estagios (exact, case-insensitive, fuzzy SequenceMatcher, type validation)
com dicionario curado de aliases por tipo de entidade.

### 5. Chunking AST + Construcao de Knowledge Graph (GAP 5)
Parser Python (ast stdlib) + Parser Markdown (regex) + Parser Notebook (json)
alimentando extracao com ontologia restrita. Combina compreensao de codigo com construcao de KG.

### 6. Retrieval Unificado 3-Estrategias com Fusao (GAP 6)
Graph + Vector + Community executados em paralelo, fundidos pelo ContextRanker com
normalizacao, ponderacao, deduplicacao e telemetria por estagio.

### 7. Resumos de Comunidade Especializados por Dominio (GAP 7)
Prompts de sumarizacao com expertise em econometria + cache + nos Community no Neo4j.

### 8. Ingestao Incremental com Hash de Conteudo (GAP 8)
SHA-256 por arquivo + manifesto JSON + metadados de pipeline no Neo4j para codebases em evolucao.

## Estrutura de Pastas

### `/literatura`
- Surveys de GraphRAG (2024-2025)
- HybridRAG e aplicacoes financeiras
- Ontology-constrained extraction
- AST-based code chunking
- Entity resolution em dominios tecnicos
- Cost optimization em LLM pipelines

### `/teoria`
- Formalizacao da ontologia e suas restricoes
- Framework de classificacao de intencao e calibracao de pesos
- Analise de complexidade do pipeline de resolucao de entidades
- Modelo de custo: Batch API vs individual vs cache hit rates

### `/simulacoes`
- Ablation study: impacto de cada componente no retrieval quality
- Comparacao de pesos: estaticos vs dinamicos por intencao
- Analise de custo: Batch vs individual vs incremental savings
- Entity resolution: precision/recall por estagio

### `/implementacao`
- Codigo-fonte completo do sistema (ja existente em `/graphrag/src/`)
- Metricas de performance e telemetria
- Configuracao e deployment

### `/aplicacoes`
- PanelBox: biblioteca de econometria de painel (caso de uso primario)
- Analise qualitativa de respostas geradas
- Comparacao com RAG tradicional (vector-only)

### `/paper`
- Manuscrito LaTeX
- Figuras e tabelas
- Supplementary materials

### `/desenvolvimento`
- Fases de desenvolvimento e cronograma
- Checklists de tarefas por fase

## Journals Alvo

**Primeira escolha**: ACM Transactions on Information Systems (TOIS)
- Publicou o survey "Graph Retrieval-Augmented Generation" (2025)
- Escopo perfeito: information retrieval + systems
- IF ~5.4

**Segunda escolha**: Information Fusion (Elsevier)
- Foco em fusao multi-modal/multi-estrategia
- Alta relevancia para o componente de retrieval fusion
- IF ~14.7

**Alternativas**:
- EMNLP Systems Track (conferencia, mais rapido)
- KDD Applied Data Science Track (foco pratico)
- Expert Systems with Applications (aplicacao pratica)

## Cronograma

```
Mes 1-2:   FASE 1 (Literatura e baseline)
Mes 3-5:   FASE 2 (Experimentos e ablation)
Mes 6-8:   FASE 3 (Escrita do manuscrito)
Mes 9-10:  FASE 4 (Revisao e submissao)
Mes 11-12: FASE 5 (Revisoes do journal)
```

## Metricas de Sucesso

- [ ] Ablation study completo (8 componentes)
- [ ] Comparacao com RAG baseline (vector-only)
- [ ] Comparacao com Microsoft GraphRAG vanilla
- [ ] Analise de custo quantificada (USD por 1000 chunks)
- [ ] Paper submetido a journal/conferencia
- [ ] Replication package publico

---

**Criado em**: Marco 2026
**Prioridade**: ALTA (sistema ja implementado, paper documenta contribuicoes)
