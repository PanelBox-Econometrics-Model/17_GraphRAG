# Survey da Literatura e Lacunas Identificadas

**Data**: Marco 2026
**Objetivo**: Mapear o estado da arte em GraphRAG e identificar lacunas que nosso sistema preenche

---

## 1. Papers Fundamentais de GraphRAG

### 1.1 Microsoft GraphRAG (Edge et al., 2024)
- **Paper**: "From Local to Global: A Graph RAG Approach to Query-Focused Summarization"
- **Link**: https://arxiv.org/abs/2404.16130
- **Contribuicao**: Arquitetura de referencia — extracao de KG, comunidades Leiden, resumos hierarquicos
- **Limitacao**: Domain-agnostic, custo alto (~$X por 1M tokens), sem pesos adaptativos
- **Relacao com nosso trabalho**: Inspiracao arquitetural; nos especializamos cada estagio

### 1.2 GraphRAG Survey (Peng et al., ACM TOIS 2025)
- **Paper**: "Graph Retrieval-Augmented Generation: A Survey"
- **Link**: https://arxiv.org/abs/2408.08921
- **Contribuicao**: Taxonomia G-Indexing/G-Retrieval/G-Generation; classifica Knowledge-based vs Index-based vs Hybrid
- **Limitacao**: Survey, nao sistema; identifica desafios mas nao propoe solucoes
- **Relacao**: Nosso sistema se classifica como Knowledge-based GraphRAG com extensoes

### 1.3 Survey para LLMs Customizados (Hu et al., 2025)
- **Paper**: "A Survey of Graph Retrieval-Augmented Generation for Customized LLMs"
- **Link**: https://arxiv.org/abs/2501.13958
- **Contribuicao**: Categorizacao de tecnicas de retrieval e generation augmentation
- **Limitacao**: Foco generico, nao aborda especializacao de dominio
- **Relacao**: Nosso intent-adaptive retrieval nao aparece em nenhuma categoria existente

### 1.4 GraphRAG Overview (Gao et al., 2025)
- **Paper**: "Retrieval-Augmented Generation with Graphs (GraphRAG)"
- **Link**: https://arxiv.org/abs/2501.00309
- **Contribuicao**: Sintese consolidada do campo
- **Relacao**: Confirma que a area e nascente com muitas lacunas

---

## 2. Dominio Financeiro

### 2.1 HybridRAG (Singh et al., ACM ICAIF 2024)
- **Paper**: "HybridRAG: Integrating Knowledge Graphs and Vector Retrieval for Efficient Information Extraction from Financial Documents"
- **Link**: https://arxiv.org/abs/2408.04948
- **Contribuicao**: Combina Graph + Vector RAG para 50 earnings calls (Nifty 50)
- **Limitacao**: Pesos ESTATICOS, sem ontologia de dominio, dominio superficial (earnings calls generico)
- **Relacao**: Nosso sistema vai alem com 3 estrategias, pesos adaptativos, e ontologia especializada
- **COMPETIDOR MAIS PROXIMO**

### 2.2 FinDKG (Liu et al., ACM ICAIF 2024)
- **Paper**: "FinDKG: Dynamic Knowledge Graphs with LLMs for Detecting Global Trends in Financial Markets"
- **Link**: https://arxiv.org/abs/2407.10909
- **Contribuicao**: KG temporal de noticias financeiras (1999-2023), 15 relations, 12 entity types
- **Limitacao**: Foco em trend detection, nao RAG; dominio e noticias, nao bibliotecas de codigo
- **Relacao**: Ontologia similar em escopo mas para dominio diferente

### 2.3 IEEE 2807.2-2024
- **Documento**: "Guide for Application of Knowledge Graphs for Financial Services"
- **Contribuicao**: Guia de arquitetura para KGs em financas
- **Limitacao**: Guia, nao implementacao; nao aborda RAG
- **Relacao**: Contexto institucional para relevancia do trabalho

---

## 3. Ontologia e Extracao Restrita

### 3.1 Ontology-Grounded Triple Extraction (CEUR-WS 2024)
- **Link**: https://ceur-ws.org/Vol-4085/paper13.pdf
- **Resultado**: Ontologia melhora precision em +44.2%, reduz alucinacoes em -22.5%
- **Limitacao**: Nao integra com RAG; avaliacao isolada da extracao
- **Relacao**: Valida nosso approach de ontologia restrita

### 3.2 Two-Step Pipeline with Ontology (ACL TextGraphs 2024)
- **Link**: https://aclanthology.org/2024.textgraphs-1.5.pdf
- **Contribuicao**: Pipeline em 2 passos com alinhamento ontologico
- **Limitacao**: Generico, nao dominio-especifico
- **Relacao**: Nosso pipeline tambem valida contra ontologia, mas no dominio de econometria

### 3.3 Ontology for Industrial Standards (arXiv 2024)
- **Link**: https://arxiv.org/abs/2512.08398
- **Contribuicao**: KG baseado em ontologia para documentos industriais
- **Relacao**: Paralelo interessante — dominio industrial vs nosso dominio econometrico

### 3.4 Ontology Impact on RAG (arXiv 2025)
- **Link**: https://arxiv.org/html/2511.05991v1
- **Contribuicao**: Compara diretamente ontologias e impacto na qualidade do RAG
- **Relacao**: Evidencia que suporta nossa tese de que ontologia melhora RAG

---

## 4. Chunking de Codigo

### 4.1 cAST (Chen et al., EMNLP Findings 2025)
- **Paper**: "cAST: Enhancing Code Retrieval-Augmented Generation with Structural Chunking via AST"
- **Link**: https://arxiv.org/abs/2506.15655
- **Resultado**: AST chunking melhora Recall@5 em +4.3 pts, Pass@1 em +2.67 pts
- **Limitacao**: Usa AST apenas para retrieval vetorial; NAO constroi knowledge graph
- **Relacao**: Nos combinamos AST chunking com construcao de KG — lacuna exata que preenchemos

---

## 5. Construcao Incremental de KG

### 5.1 iText2KG (Conte et al., 2024)
- **Link**: https://arxiv.org/abs/2409.03284
- **Contribuicao**: KG incremental com LLM, sem pos-processamento
- **Limitacao**: Nao usa hash de conteudo para deteccao de mudancas
- **Relacao**: Nos usamos SHA-256 + manifesto para ingestao verdadeiramente incremental

### 5.2 IncRML (Semantic Web Journal)
- **Contribuicao**: 11-57x mais rapido que reconstrucao completa
- **Limitacao**: Usa RML mappings, nao LLM extraction
- **Relacao**: Complementar — nos provemos incrementalidade para LLM-based extraction

---

## 6. Alternativas Cost-Efficient

### 6.1 LightRAG (Guo et al., 2024)
- **Link**: https://arxiv.org/abs/2410.05779
- **Resultado**: 10x reducao de tokens, 65-80% economia vs GraphRAG
- **Limitacao**: Sem ontologia restrita, sem AST, pesos estaticos, sem community summaries
- **Relacao**: Baseline de comparacao para custo; nos otimizamos diferentemente (Batch API + cache + incremental)

### 6.2 NanoGraphRAG
- **Contribuicao**: Implementacao leve e hackable do GraphRAG
- **Limitacao**: Funcionalidade reduzida, sem especializacao de dominio
- **Relacao**: Baseline potencial

---

## 7. Tabela Resumo de Lacunas

| # | Lacuna | Evidencia na Literatura | Nosso Preenchimento |
|---|--------|------------------------|---------------------|
| 1 | GraphRAG para econometria | Zero papers neste dominio | Ontologia 10+14 types |
| 2 | Pesos adaptativos por intencao | HybridRAG=estatico, Adaptive-RAG=complexidade | 6 intents x 3 estrategias |
| 3 | Custo de indexacao/extracao | Papers focam query-time | Batch+cache+incremental |
| 4 | ER para vocabularios tecnicos | ER financeiro=nomes | 4-stage com aliases |
| 5 | AST + KG construction | cAST=retrieval only | AST -> triplas -> grafo |
| 6 | Fusao de 3 estrategias | HybridRAG=2, GraphRAG=2 modos | Graph+Vector+Community |
| 7 | Community summaries de dominio | GraphRAG=generico | Prompt econometrics-expert |
| 8 | Incremental com hash | iText2KG=sem hash | SHA-256+manifesto+meta |

---

## 8. Referencias Adicionais para Explorar

### Knowledge Graphs
- Ji et al. (2021) "A Survey on Knowledge Graphs" IEEE TNNLS
- Hogan et al. (2021) "Knowledge Graphs" ACM Computing Surveys

### RAG Fundamentals
- Lewis et al. (2020) "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" NeurIPS
- Gao et al. (2024) "Retrieval-Augmented Generation for LLMs: A Survey" arXiv:2312.10997

### Entity Resolution
- Christophides et al. (2021) "An Overview of End-to-End Entity Resolution" ACM Computing Surveys
- Barlaug & Gulla (2021) "Neural Networks for Entity Matching" ACM TIST

### Community Detection
- Traag et al. (2019) "From Louvain to Leiden" Scientific Reports

### GraphRAG Resources
- Awesome-GraphRAG: https://github.com/DEEP-PolyU/Awesome-GraphRAG
- Neo4j GraphRAG Field Guide: https://neo4j.com/blog/developer/graphrag-field-guide-rag-patterns/
- GraphRAG on Technical Documents (Dagstuhl): https://drops.dagstuhl.de/entities/document/10.4230/TGDK.3.2.3

---

*Compilado em: Marco 2026*
*Proxima atualizacao: Apos FASE 1 (leitura completa dos papers)*
