# Paper 17: Ontology-Constrained GraphRAG with Intent-Adaptive Multi-Strategy Retrieval for Domain-Specific Technical Libraries

**Data**: Marco 2026
**Status**: Sistema implementado, paper em construcao
**Prioridade**: Alta
**Periodico-alvo**: ACM TOIS, Information Fusion, EMNLP Systems Track

---

## Executive Summary

Este paper apresenta um sistema GraphRAG end-to-end especializado em dominio, aplicado a uma biblioteca de econometria de painel (PanelBox). O sistema combina **8 contribuicoes tecnicas** que preenchem lacunas identificadas na literatura atual de GraphRAG:

1. **Ontologia restrita** para econometria de painel (10 entity types, 14 relation types)
2. **Retrieval multi-estrategia com pesos adaptativos** por tipo de intencao (6 tipos)
3. **Otimizacao de custos em 3 camadas** (Batch API + cache + incremental)
4. **Resolucao de entidades** com dicionario de aliases de dominio
5. **Chunking AST** combinado com construcao de knowledge graph
6. **Engine de retrieval unificado** com fusao de 3 estrategias
7. **Resumos de comunidade** especializados por dominio
8. **Ingestao incremental** com deteccao de mudancas por hash de conteudo

**Diferencial central**: Especializacao de dominio em cada estagio do pipeline, nao apenas no prompt final de geracao. Enquanto sistemas existentes (Microsoft GraphRAG, LightRAG, HybridRAG) sao domain-agnostic, nosso sistema incorpora conhecimento de dominio na ontologia, nos aliases, nos prompts de extracao, nos resumos de comunidade, e nos pesos de retrieval.

---

## 1. Motivacao

### 1.1 O Problema

Instituicoes financeiras (bancos, asset managers, bancos centrais, fintechs) usam intensivamente econometria de painel: Fixed Effects, Random Effects, GMM de Arellano-Bond, System GMM de Blundell-Bond, testes de raiz unitaria, cointegration, e dezenas de testes diagnosticos.

Os analistas quantitativos enfrentam perguntas como:
- "Qual teste devo rodar antes de usar System GMM?"
- "Qual a diferenca entre robust e clustered standard errors?"
- "Me mostre codigo para estimar um painel dinamico com dados desbalanceados"
- "O que significa rejeitar o teste de Hansen?"

**RAG tradicional (vector-only)** falha nestas perguntas porque:
- Relacoes estruturadas (VALIDATES, PRECONDITION, ALTERNATIVE_TO) se perdem na similaridade vetorial
- A mesma entidade aparece com nomes diferentes (FE, Fixed Effects, Within Estimator, FixedEffects)
- Perguntas de comparacao exigem recuperar ambos os lados, nao apenas o mais similar
- Perguntas conceituais de alto nivel precisam de resumos, nao de trechos de codigo

### 1.2 Por que GraphRAG?

GraphRAG combina knowledge graphs (relacoes explicitas) com RAG (recuperacao + geracao). A arquitetura de referencia (Edge et al., 2024) demonstrou superioridade em perguntas que exigem sensemaking global.

**Porem**, os sistemas GraphRAG existentes sao domain-agnostic:
- Microsoft GraphRAG extrai entidades genericas sem restricao ontologica
- LightRAG otimiza custo mas perde profundidade relacional
- HybridRAG combina graph + vector mas com pesos estaticos
- Nenhum sistema adapta pesos de retrieval baseado no tipo de pergunta

### 1.3 Nossa Tese

**Especializacao de dominio em cada estagio do pipeline GraphRAG — nao apenas no prompt de geracao — melhora significativamente a qualidade das respostas para bibliotecas tecnicas especializadas, ao mesmo tempo que reduz custos operacionais.**

---

## 2. Estado da Arte e Lacunas

### 2.1 Papers Fundamentais

| Paper | Ano | Contribuicao | Limitacao |
|-------|-----|--------------|-----------|
| Edge et al. "From Local to Global" (Microsoft) | 2024 | Arquitetura GraphRAG de referencia | Domain-agnostic, custo alto, sem pesos adaptativos |
| Peng et al. "Graph RAG Survey" (ACM TOIS) | 2025 | Taxonomia G-Indexing/G-Retrieval/G-Generation | Survey, nao sistema; identifica gaps |
| Singh et al. "HybridRAG" (ACM ICAIF) | 2024 | Graph + Vector para documentos financeiros | Pesos estaticos, dominio superficial (earnings calls) |
| Liu et al. "FinDKG" (ACM ICAIF) | 2024 | KG temporal para mercados financeiros | Foco em trend detection, nao RAG |
| Chen et al. "cAST" (EMNLP Findings) | 2025 | Chunking AST para code retrieval | Nao constroi KG; retrieval vector-only |
| "Ontology-Grounded Triple Extraction" (CEUR-WS) | 2024 | Ontologia melhora extracao em 44% | Nao integra com RAG; dominio generico |
| Conte et al. "iText2KG" | 2024 | Construcao incremental de KG | Nao usa hash de conteudo; dominio generico |
| LightRAG | 2024 | 10x reducao de tokens vs GraphRAG | Sem ontologia; pesos estaticos; sem AST |

### 2.2 Lacunas Identificadas

**GAP 1: Nenhum GraphRAG para econometria/financas quantitativas**
- FinDKG: noticias financeiras, nao bibliotecas de codigo
- HybridRAG: earnings calls, pesos estaticos
- Zero papers com ontologia de Estimator, DiagnosticTest, StatisticalConcept

**GAP 2: Nenhum sistema com pesos de retrieval adaptativos por intencao**
- HybridRAG: graph=0.5, vector=0.5 (fixo)
- Adaptive-RAG: adapta complexidade, nao pesos entre estrategias
- Zero papers com 6+ intent types mapeados para 3 estrategias com boosting por entidade

**GAP 3: Nenhum paper trata otimizacao de custo na fase de indexacao**
- LightRAG: otimiza query-time
- FalkorDB: reducao de custo generico
- Zero papers com Batch API + cache + incremental como pipeline integrado

**GAP 4: Entity resolution para vocabularios tecnicos especializados**
- ER financeiro: nomes de pessoas/empresas (AML)
- Zero papers com alias dictionaries para terminologia econometrica

**GAP 5: Chunking AST combinado com construcao de KG**
- cAST: AST para retrieval vector-only
- Zero papers onde chunks AST alimentam extracao de triplas com ontologia

**GAP 6: Retrieval unificado com fusao de 3 estrategias**
- HybridRAG: 2 estrategias (graph + vector)
- Microsoft GraphRAG: 2 modos (local + global), nao fusao ponderada
- Zero papers com graph + vector + community em fusao com ContextRanker

**GAP 7: Community summaries especializados por dominio**
- Microsoft GraphRAG: resumos genericos
- Zero papers com summarizer que instrui LLM como "econometrics expert"

**GAP 8: Ingestao incremental com hash de conteudo para codebases**
- iText2KG: incremental mas sem hash
- IncRML: hash mas sem LLM extraction
- Zero papers com SHA-256 + manifesto + metadados de pipeline no Neo4j

---

## 3. Arquitetura do Sistema

### 3.1 Visao Geral do Pipeline

```
Source Files (.py, .md, .ipynb)
    |
    v
[1] Discovery (SHA-256 hash, manifest comparison)
    |
    v
[2] Chunking (AST parser for Python, regex for Markdown, JSON for Notebooks)
    |
    v
[3] Triple Extraction (Claude API + ontology-constrained prompts + Batch API)
    |
    v
[4] Entity Resolution (alias lookup + fuzzy matching + type validation)
    |
    v
[5] Graph Loading (Neo4j MERGE with schema + constraints)
    |
    v
[6] Community Detection (Leiden algorithm via GDS)
    |
    v
[7] Community Summarization (Claude API + domain-expert prompts)
    |
    v
[8] Embedding (all-MiniLM-L6-v2 + pgvector)
```

### 3.2 Pipeline de Retrieval

```
User Query
    |
    v
[A] Intent Parser (regex-based, 6 intent types, entity extraction)
    |
    v
[B] Parallel Retrieval:
    B1: Graph Retriever (Neo4j Cypher, multi-hop traversal)
    B2: Vector Retriever (pgvector cosine similarity)
    B3: Community Retriever (summary matching)
    |
    v
[C] Context Ranker (normalize, weight, deduplicate, truncate)
    |
    v
[D] Generation (Claude API with extended thinking)
```

### 3.3 Ontologia

**10 Entity Types:**
| Type | Descricao | Exemplo |
|------|-----------|---------|
| Estimator | Modelo econometrico | SystemGMM, FixedEffects |
| DiagnosticTest | Teste de especificacao | HausmanTest, SarganTest |
| Parameter | Parametro de modelo | n_instruments, max_lags |
| StatisticalConcept | Conceito teorico | heteroskedasticity, endogeneity |
| Literature | Referencia academica | arellano_bond_1991 |
| ModelFamily | Familia de modelos | GMM, StaticPanel |
| StandardError | Tipo de erro padrao | robust_se, clustered_se |
| Dataset | Conjunto de dados | panel_data, employment_data |
| CodePattern | Padrao de uso de codigo | fit_predict_pattern |
| ResultMetric | Metrica de resultado | r_squared, j_statistic |

**14 Relation Types:**
BELONGS_TO, INHERITS_FROM, VALIDATES, REQUIRES, PRODUCES, ADDRESSES, TESTS_FOR, BASED_ON, ALTERNATIVE_TO, PRECONDITION, SUPPORTS_SE, DEMONSTRATED_IN, IMPLEMENTED_BY, SUCCEEDS

### 3.4 Pesos Adaptativos por Intencao

| Intent Type | Graph | Vector | Community | Logica |
|-------------|:-----:|:------:|:---------:|--------|
| VALIDATION | 0.70 | 0.20 | 0.10 | Validacao exige relacoes estruturadas (VALIDATES, PRECONDITION) |
| COMPARISON | 0.50 | 0.30 | 0.20 | Comparacao precisa de relacoes entre entidades |
| RECOMMENDATION | 0.30 | 0.40 | 0.30 | Recomendacao combina similaridade e contexto |
| EXPLANATION | 0.40 | 0.40 | 0.20 | Explicacao precisa de conceitos e codigo |
| CODE_EXAMPLE | 0.30 | 0.60 | 0.10 | Codigo e melhor recuperado por similaridade vetorial |
| GENERAL | 0.30 | 0.30 | 0.40 | Perguntas gerais se beneficiam de resumos |

**Entity boost**: Se entidades sao reconhecidas na query, graph weight recebe boost de ate +0.10, normalizado para soma=1.0.

---

## 4. Experimentos Propostos

### 4.1 Ablation Study (Contribuicao Principal)

Remover cada componente individualmente e medir impacto no retrieval quality:

| Experimento | Componente Removido | Metrica |
|-------------|---------------------|---------|
| A1 | Ontologia restrita -> extracao generica | Precision de triplas, relevancia |
| A2 | Pesos adaptativos -> pesos estaticos (0.33/0.33/0.34) | nDCG@5, MRR |
| A3 | Entity resolution -> sem resolucao | Cobertura do grafo, duplicacoes |
| A4 | AST chunking -> line-based chunking | Recall@5 para queries de codigo |
| A5 | Community summaries -> sem comunidades | Qualidade em queries GENERAL |
| A6 | Batch API -> individual calls | Custo por chunk (USD) |
| A7 | Incremental -> full reprocessing | Tempo e custo de re-ingestao |
| A8 | 3 estrategias -> vector-only (RAG baseline) | nDCG@5, MRR, cobertura |

### 4.2 Benchmark de Qualidade

**Dataset de avaliacao**: 50 perguntas reais sobre econometria de painel, classificadas por tipo:
- 10 VALIDATION ("Qual teste usar antes de GMM?")
- 8 COMPARISON ("Diferenca entre FE e RE?")
- 7 RECOMMENDATION ("Melhor estimador para painel curto?")
- 10 EXPLANATION ("O que e heterocedasticidade?")
- 8 CODE_EXAMPLE ("Codigo para System GMM?")
- 7 GENERAL ("O que o PanelBox faz?")

**Metricas**:
- nDCG@5, nDCG@10 (ranking quality)
- MRR (Mean Reciprocal Rank)
- Hit Rate@3
- Resposta humana: relevancia (1-5), completude (1-5), corretude (1-5)

**Baselines**:
1. Vector-only RAG (sem grafo)
2. Microsoft GraphRAG vanilla (sem ontologia)
3. HybridRAG (graph + vector, pesos estaticos)
4. Nosso sistema completo

### 4.3 Analise de Custo

Quantificar custo em USD por pipeline stage:

| Metrica | Formula |
|---------|---------|
| Custo de indexacao | (tokens enviados x preco) - desconto Batch API |
| Cache hit rate | chunks cacheados / total chunks |
| Reducao incremental | chunks pulados / total chunks |
| Custo total por 1000 chunks | soma de todos os estagios |
| Comparacao | vs individual calls, vs full reprocessing |

### 4.4 Analise de Entity Resolution

- Precision: entidades corretamente unificadas / total unificadas
- Recall: entidades que deveriam ser unificadas / total que deveriam
- Impacto no grafo: reducao de nos duplicados
- Analise por estagio: contribuicao de exact vs fuzzy vs type validation

---

## 5. Estrutura do Paper

### Titulo Proposto
**"Domain-Specialized GraphRAG: Ontology-Constrained Knowledge Graph Construction and Intent-Adaptive Multi-Strategy Retrieval for Econometric Software Libraries"**

### Titulo Alternativo (mais curto)
**"OntologyRAG: Intent-Adaptive Graph Retrieval for Domain-Specific Technical Libraries"**

### Secoes

| # | Secao | Paginas | Conteudo |
|---|-------|---------|----------|
| 1 | Introduction | 2-3 | Problema, motivacao, contribuicoes |
| 2 | Related Work | 3-4 | GraphRAG landscape, lacunas, posicionamento |
| 3 | System Architecture | 5-6 | Pipeline completo (ingestion + retrieval + generation) |
| 4 | Domain-Specific Components | 4-5 | Ontologia, alias resolution, community summaries |
| 5 | Intent-Adaptive Retrieval | 3-4 | Intent classification, weight presets, entity boosting |
| 6 | Cost Optimization | 2-3 | Batch API, caching, incremental processing |
| 7 | Experimental Evaluation | 6-8 | Ablation, benchmarks, cost analysis, case studies |
| 8 | Discussion | 2-3 | Limitacoes, generalizacao para outros dominios |
| 9 | Conclusion | 1-2 | Contribuicoes, trabalho futuro |
| | References | 2-3 | ~40-50 referencias |
| | **Total** | **30-40** | |

### Figuras Planejadas

1. **Pipeline overview** (ingestion + retrieval) - diagrama de arquitetura
2. **Ontology schema** - grafo visual dos 10 entity types e 14 relation types
3. **AST chunking example** - arvore AST -> chunks semanticos
4. **Triple extraction flow** - prompt -> LLM -> validation -> graph
5. **Entity resolution pipeline** - alias -> fuzzy -> type validation
6. **Intent weight heatmap** - 6 intents x 3 strategies
7. **Ablation results** - bar chart com impacto de cada componente
8. **Cost comparison** - batch vs individual vs incremental
9. **Knowledge graph visualization** - subgrafo real do PanelBox
10. **Query example walkthrough** - end-to-end de uma query

### Tabelas Planejadas

1. Comparacao com sistemas existentes (feature matrix)
2. Ontology definition (entity types + relation types)
3. Retrieval weight presets por intent
4. Ablation study results
5. Benchmark results (nDCG, MRR, Hit Rate)
6. Cost analysis por pipeline stage
7. Entity resolution precision/recall por estagio
8. Qualitative examples de respostas geradas

---

## 6. Referencia Bibliografica Preliminar

### GraphRAG Foundational
1. Edge, D., et al. (2024). "From Local to Global: A Graph RAG Approach to Query-Focused Summarization." arXiv:2404.16130
2. Peng, B., et al. (2025). "Graph Retrieval-Augmented Generation: A Survey." ACM TOIS. arXiv:2408.08921
3. Hu, Z., et al. (2025). "A Survey of Graph Retrieval-Augmented Generation for Customized LLMs." arXiv:2501.13958
4. Gao, Y., et al. (2025). "Retrieval-Augmented Generation with Graphs (GraphRAG)." arXiv:2501.00309

### Financial Domain
5. Singh, B., et al. (2024). "HybridRAG: Integrating Knowledge Graphs and Vector Retrieval for Efficient Information Extraction from Financial Documents." ACM ICAIF. arXiv:2408.04948
6. Liu, X., et al. (2024). "FinDKG: Dynamic Knowledge Graphs with LLMs for Detecting Global Trends in Financial Markets." ACM ICAIF. arXiv:2407.10909
7. IEEE 2807.2-2024. "Guide for Application of Knowledge Graphs for Financial Services."

### Ontology-Constrained Extraction
8. "Ontology-Grounded Triple Extraction with LLMs." (2024). CEUR-WS Vol-4085
9. "A Two-Step Knowledge Extraction Pipeline with Ontology Alignment." (2024). ACL TextGraphs
10. "Ontology-Based Knowledge Graph Framework for Industrial Standards." (2024). arXiv:2512.08398
11. "Ontology Learning and Knowledge Graph Construction: Impact on RAG." (2025). arXiv:2511.05991

### Code Understanding
12. Chen, X., et al. (2025). "cAST: Enhancing Code Retrieval-Augmented Generation with Structural Chunking via AST." EMNLP Findings. arXiv:2506.15655

### Incremental KG Construction
13. Conte, A., et al. (2024). "iText2KG: Incremental Knowledge Graphs Construction Using LLMs." arXiv:2409.03284
14. "IncRML: Incremental Knowledge Graph Construction from Heterogeneous Data Sources." Semantic Web Journal.

### Alternative GraphRAG Architectures
15. Guo, Z., et al. (2024). "LightRAG: Simple and Fast Retrieval-Augmented Generation." arXiv:2410.05779
16. "NanoGraphRAG: A Lightweight Alternative." (2024). GitHub.

### Knowledge Graph Fundamentals
17. Ji, S., et al. (2021). "A Survey on Knowledge Graphs: Representation, Acquisition, and Applications." IEEE TNNLS.
18. Hogan, A., et al. (2021). "Knowledge Graphs." ACM Computing Surveys.

### RAG Fundamentals
19. Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS.
20. Gao, Y., et al. (2024). "Retrieval-Augmented Generation for Large Language Models: A Survey." arXiv:2312.10997

### Entity Resolution
21. Christophides, V., et al. (2021). "An Overview of End-to-End Entity Resolution." ACM Computing Surveys.
22. Barlaug, N., & Gulla, J.A. (2021). "Neural Networks for Entity Matching: A Survey." ACM TIST.

### Community Detection
23. Traag, V., et al. (2019). "From Louvain to Leiden: Guaranteeing Well-Connected Communities." Scientific Reports.

---

## 7. Diferenciais vs Trabalhos Existentes

| Feature | Microsoft GraphRAG | LightRAG | HybridRAG | **Nosso Sistema** |
|---------|:-:|:-:|:-:|:-:|
| Ontologia restrita de dominio | - | - | - | **10 types + 14 rels** |
| Pesos adaptativos por intencao | - | - | - | **6 intents** |
| AST chunking + KG | - | - | - | **Python/MD/Notebook** |
| Entity resolution com aliases | - | - | - | **4-stage pipeline** |
| Batch API optimization | - | - | - | **50% desconto** |
| Incremental ingestion (hash) | - | Parcial | - | **SHA-256 + manifesto** |
| Community summaries | Generico | - | - | **Domain-expert** |
| Multi-strategy retrieval | Local/Global | Dual-level | Graph+Vector | **Graph+Vector+Community** |
| Intent classification | - | - | - | **6 types, zero-cost** |
| Cost tracking | - | - | - | **Per-interaction** |

---

## 8. Proximos Passos

### Imediatos
1. [ ] Compilar lista completa de referencias (BibTeX)
2. [ ] Definir dataset de avaliacao (50 perguntas)
3. [ ] Implementar metricas automaticas (nDCG, MRR)
4. [ ] Rodar pipeline completo no PanelBox para gerar grafo de referencia

### Curto Prazo (Mes 1-2)
5. [ ] Executar ablation study (8 experimentos)
6. [ ] Executar benchmark contra baselines
7. [ ] Analise de custo quantificada
8. [ ] Iniciar escrita da Secao 3 (Architecture)

### Medio Prazo (Mes 3-6)
9. [ ] Completar todas as secoes do paper
10. [ ] Gerar figuras e tabelas
11. [ ] Internal review
12. [ ] Submissao

---

## 9. Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|:---:|:---:|-----------|
| Dataset de avaliacao muito pequeno | Media | Alto | Aumentar para 100 perguntas, usar crowdsourcing |
| Ablation nao mostra diferenca significativa | Baixa | Alto | Cada componente ja e justificado pela literatura |
| Scooped por paper similar | Baixa | Medio | Dominio especifico (econometria) e unico |
| Reviewers pedem mais baselines | Media | Medio | Preparar comparacao com LightRAG e NanoGraphRAG |
| Custo de experimentos (API calls) | Media | Baixo | Usar cache agressivo, Batch API |

**Probabilidade de sucesso**: 85-90% (sistema ja funcional, contribuicoes claras)

---

**Criado em**: Marco 2026
**Autores**: Gustavo Haase, Paulo Dourado
**Repositorio**: graphrag/ dentro do projeto PanelBox
