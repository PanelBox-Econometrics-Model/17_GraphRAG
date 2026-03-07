# Paper 17: GraphRAG para Instituições Financeiras

## Descrição

Paper explorando a construção e aplicação de GraphRAG (Graph Retrieval-Augmented Generation) para instituições financeiras, baseado na implementação real desenvolvida no projeto PanelBox (`/graphrag`). O paper aborda segurança, redução de alucinações, economia de tokens e velocidade de processamento como pilares centrais da proposta.

## Status

- [x] Estrutura de pastas criada
- [x] Revisão de literatura completa (30+ papers catalogados)
- [ ] Proposta do paper (PROPOSTA)
- [ ] Fase 1: Fundamentação teórica
- [ ] Fase 2: Teoria e metodologia
- [ ] Fase 3: Simulações e benchmarks
- [ ] Fase 4: Aplicação empírica
- [ ] Fase 5: Escrita do manuscrito

## Pilares do Paper

1. **Segurança**: Isolamento de dados, criptografia, privacidade diferencial, prevenção de vazamento de entidades
2. **Redução de Alucinações**: Fundamentação em knowledge graph, rastreabilidade de fontes, raciocínio multi-hop
3. **Economia de Tokens**: Retrieval estruturado vs. vectorial, community summaries, cache de queries
4. **Velocidade de Processamento**: Retrieval paralelo, indexação incremental, detecção de comunidades

## Implementação de Referência

Baseado na implementação em `/home/guhaase/projetos/panelbox/graphrag`:
- **Stack**: Neo4j + PostgreSQL + Claude API + sentence-transformers + Leiden
- **Pipeline**: Chunking → Triple Extraction → Entity Resolution → Graph Loading → Community Detection
- **Retrieval**: Graph + Vector + Community (3 estratégias paralelas com fusão ponderada)
- **API**: FastAPI + Streamlit + JWT Auth + Cost Tracking

## Estrutura de Pastas

```
17_GraphRAG/
├── README.md                    # Este arquivo
├── literatura/                  # Revisão bibliográfica
│   └── REVISAO_LITERATURA.md   # 30+ papers catalogados
├── desenvolvimento/             # Guias de desenvolvimento por fase
├── teoria/                      # Fundamentação teórica
├── simulacoes/                  # Benchmarks e experimentos
├── implementacao/               # Código e scripts
├── aplicacoes/                  # Aplicações empíricas
└── paper/                       # Manuscrito final (LaTeX)
```

## Literatura Catalogada

| Categoria | Qtd. Papers | Destaques |
|-----------|-------------|-----------|
| Core GraphRAG | 4 | Microsoft GraphRAG, GRAG, 2 surveys |
| Finanças/Banking | 7 | HybridRAG (BlackRock), FinReflectKG, FinDKG, GraphCompliance |
| Redução de alucinações | 6 | RAG vs GraphRAG, Think-on-Graph, HippoRAG, SubgraphRAG |
| Eficiência de tokens | 6 | TERAG, LazyGraphRAG, LightRAG, E2GraphRAG, PolyG, RAPTOR |
| Segurança | 6 | Threat models, Privacy-Aware RAG, SAG, FairRAG |
| Benchmarks | 3 | Vector vs Graph vs Hybrid, GFM-RAG |
| KG em finanças | 5 | KG-RAG SEC, KG2RAG, Fraud Detection, Audit, Reporting |
| Detecção de comunidades | 3 | CommunityKG-RAG, Leiden, k-core |
| Complementares | 3 | MedGraphRAG, RAG Financial Docs, PwC Graph LLMs |

**Total: 43 papers/publicações catalogados**

## Métricas Quantitativas da Literatura

- GraphRAG alcança **86.31%** vs **72.36%** do RAG tradicional (RobustQA)
- Redução de tokens: **89-97%** (TERAG), **95%** (PolyG)
- Custo de indexação: **0.1%** do GraphRAG completo (LazyGraphRAG)
- Speedup retrieval: **100x** sobre LightRAG (E2GraphRAG)
- Acurácia detecção de fraude: **95.4%** (LSTM-GraphSAGE)

## Target Journal/Conference

A definir.

## Timeline

A definir após aprovação da proposta.
