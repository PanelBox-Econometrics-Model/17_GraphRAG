# Subfase 05 - Paper: Results, Applications, Discussion, Conclusion

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: SUBFASE_04
**Bloqueia**: SUBFASE_06

## Objetivo

Escrever as secoes 5-8 do paper: Results (5 experimentos), Empirical Applications (3 aplicacoes financeiras), Discussion e Conclusion. Integrar tabelas e figuras de resultados.

## Descricao Tecnica

**Resultados experimentais em**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/results/`

**Secoes existentes em main.tex** (da SUBFASE_04):
- Sections 1-4 ja escritas

**Secoes a escrever**:
- Section 5: Results (~8 paginas)
- Section 6: Empirical Applications (~6 paginas)
- Section 7: Discussion (~3 paginas)
- Section 8: Conclusion (~2 paginas)
- Online Appendix (se necessario)

## INSTRUCAO CRITICA

**Todas as tabelas e figuras devem ter**:
- Captions descritivas e auto-explicativas
- Referencia no texto antes de aparecer
- Numeros com precisao adequada (2 casas decimais para %, 3 para scores)
- Bold para melhor resultado em cada metrica

**Formato ESWA**:
- Discussao deve ser separada dos resultados
- Conclusion nao deve repetir resultados — focar em implicacoes
- Nao usar "we" excessivamente (preferir voz passiva ou "this paper")
- Limitacoes devem ser honestas e especificas

### Etapa 1: Section 5 — Results (8 paginas)

**5.1 Hallucination Reduction (Experiment 1)**
- Table: Faithfulness, Grounding rate, Factual accuracy por sistema
- Figure: Bar chart comparando faithfulness por tipo de pergunta
- Analise: onde GraphRAG supera e onde nao supera
- Breakdown por dificuldade (simple vs multi-hop)

**5.2 Token Economy Analysis (Experiment 2)**
- Table: tokens_per_query, cost_per_1000_queries, indexing_cost por sistema
- Figure: Stacked bar chart mostrando composicao de tokens (intent + retrieval + generation)
- Analise: economia com Batch API vs individual
- ROI calculation: break-even point para investimento em KG

**5.3 Processing Speed (Experiment 3)**
- Table: p50, p95 latency, cache_hit_rate por configuracao
- Figure: CDF de latencia ou box plot
- Analise: impacto do paralelismo e cache
- Breakdown: tempo por componente (intent parsing, retrieval, ranking, generation)

**5.4 Security Evaluation (Experiment 4)**
- Table: leakage_rate, extraction_success, inference_accuracy
- Analise qualitativa dos ataques
- Mapeamento de compliance atingido
- Residual risks identificados

**5.5 End-to-End Benchmark (Experiment 5)**
- Table: score por categoria e por sistema
- Figure: Radar chart ou heatmap de performance por categoria
- Analise: quais categorias se beneficiam mais do GraphRAG
- Ablation: contribuicao de cada retriever (graph, vector, community)

### Etapa 2: Section 6 — Empirical Applications (6 paginas)

**6.1 Regulatory Compliance (Basel III / LGPD)**
- Descricao do dataset e setup
- Exemplos de queries e respostas (2-3 exemplos completos com source attribution)
- Metricas de performance
- Feedback de especialistas (se disponivel)

**6.2 Financial Report Analysis (SEC 10-K/10-Q)**
- Descricao do dataset (empresas S&P 100)
- Exemplos de queries simples e multi-hop
- Comparacao com FinanceBench baseline
- Token savings analysis

**6.3 Internal Audit QA System**
- Descricao do dataset sintetico
- Demonstracao de RBAC (auditor A vs auditor B)
- Metricas de latencia sob acesso concorrente
- Security isolation results

### Etapa 3: Section 7 — Discussion (3 paginas)

**7.1 Key Findings**
- Resumo dos achados principais dos 5 experimentos
- Quais hipoteses foram confirmadas e quais nao

**7.2 When to Use GraphRAG vs VectorRAG**
- Guidelines praticas para practitioners
- Decision tree: quando GraphRAG vale o custo adicional
- Reference: "When to Use Graphs in RAG" (arXiv:2506.05690)

**7.3 Limitations**
- Qualidade do KG depende da extracao LLM
- Dados sinteticos em aplicacao de auditoria
- Custos de API podem variar
- Avaliacao de seguranca com limitacoes (nao formal prova)
- Resultados especificos ao dominio financeiro

**7.4 Practical Implications**
- Para bancos: custo-beneficio da implementacao
- Para reguladores: rastreabilidade e compliance
- Para auditores: eficiencia e seguranca

### Etapa 4: Section 8 — Conclusion (2 paginas)

- Resumo do paper (1 paragrafo)
- Contribuicoes principais (5 items, revisitados com evidencia)
- Implicacoes praticas (1 paragrafo)
- Trabalhos futuros:
  - Avaliacao com dados reais de bancos
  - Extensao para outros dominios regulados (saude, energia)
  - Integracao com provas formais de seguranca (SAG)
  - Suporte a grafos temporais (FinDKG)
  - Otimizacao de custos com modelos menores (fine-tuned)

### Etapa 5: Online Appendix (se necessario)

- Appendix A: Especificacao completa da ontologia financeira
- Appendix B: Templates de prompt para extracao de triplas
- Appendix C: 50 perguntas do benchmark com respostas
- Appendix D: Resultados detalhados por pergunta
- Appendix E: Guia de implementacao

## Criterios de Aceite

- [x] Section 5.1 (Hallucination) escrita com tabela e figura
- [x] Section 5.2 (Token Economy) escrita com tabela e figura
- [x] Section 5.3 (Processing Speed) escrita com tabela e figura
- [x] Section 5.4 (Security) escrita com tabela e analise qualitativa
- [x] Section 5.5 (Benchmark) escrita com tabela e figura
- [x] Ablation study incluido em Section 5 (contribuicao de cada retriever)
- [x] Section 6.1 (Compliance) escrita com exemplos de queries
- [x] Section 6.2 (Financial Reports) escrita com exemplos multi-hop
- [x] Section 6.3 (Audit QA) escrita com demonstracao RBAC
- [x] Section 7 (Discussion) escrita com limitacoes honestas e guidelines praticas
- [x] Section 8 (Conclusion) escrita com trabalhos futuros
- [x] Online Appendix preparado (se aplicavel)
- [x] Paper compila sem erros
- [x] Total do paper: 25-35 paginas single column

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Resultados experimentais fracos em algum pilar | Media | Alto | Ser transparente nas limitacoes, ajustar claims |
| Paper excede 35 paginas | Media | Medio | Mover detalhes para appendix online |
| Ablation study mostra retriever dispensavel | Baixa | Medio | Documentar como finding e discutir trade-offs |
| Exemplos de queries nao convincentes | Media | Medio | Selecionar exemplos que demonstram valor claramente |

**End of Specification**
