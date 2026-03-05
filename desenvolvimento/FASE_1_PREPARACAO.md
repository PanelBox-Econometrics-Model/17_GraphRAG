# FASE 1: Preparacao e Baseline

**Duracao**: 2 meses
**Objetivo**: Compilar literatura, definir dataset de avaliacao, implementar metricas, estabelecer baselines
**Pre-requisitos**: Sistema GraphRAG funcional (ja cumprido)

---

## Tarefa 1.1: Revisao Bibliografica Completa

**Duracao**: 2-3 semanas
**Entrega**: `literatura/REVISAO_COMPLETA.md`

### Subtarefas:
- [ ] Compilar e ler os ~25 papers listados na proposta
- [ ] Classificar cada paper por: contribuicao, dominio, limitacoes, relacao com nosso trabalho
- [ ] Criar tabela comparativa de features (GraphRAG vs LightRAG vs HybridRAG vs nosso)
- [ ] Identificar papers adicionais via forward/backward citation
- [ ] Compilar arquivo BibTeX: `literatura/references.bib`

### Papers Prioritarios:
1. Edge et al. (2024) - Microsoft GraphRAG [FOUNDATIONAL]
2. Peng et al. (2025) - GraphRAG Survey (ACM TOIS) [SURVEY]
3. Singh et al. (2024) - HybridRAG (ACM ICAIF) [CLOSEST COMPETITOR]
4. Liu et al. (2024) - FinDKG (ACM ICAIF) [FINANCIAL DOMAIN]
5. Chen et al. (2025) - cAST (EMNLP) [AST CHUNKING]
6. "Ontology-Grounded Triple Extraction" (2024) [ONTOLOGY]
7. Conte et al. (2024) - iText2KG [INCREMENTAL]

---

## Tarefa 1.2: Construcao do Dataset de Avaliacao

**Duracao**: 3-4 semanas
**Entrega**: `aplicacoes/evaluation_dataset.json`

### Subtarefas:
- [ ] Definir 50+ perguntas reais sobre econometria de painel
- [ ] Classificar cada pergunta por intent type (VALIDATION, COMPARISON, etc.)
- [ ] Para cada pergunta, definir gold-standard:
  - Entidades relevantes que devem ser recuperadas
  - Relacoes relevantes no grafo
  - Resposta de referencia (escrita por especialista)
  - Trechos de codigo esperados (se CODE_EXAMPLE)
- [ ] Balancear distribuicao entre os 6 intent types
- [ ] Incluir perguntas com diferentes niveis de dificuldade

### Distribuicao Alvo:
| Intent Type | Quantidade | Exemplos |
|-------------|:---:|---------|
| VALIDATION | 10 | "Quais testes rodar antes de System GMM?" |
| COMPARISON | 8 | "Diferenca entre FE e RE?" |
| RECOMMENDATION | 7 | "Melhor estimador para T=5, N=200?" |
| EXPLANATION | 10 | "O que e o teste de Hansen J?" |
| CODE_EXAMPLE | 8 | "Como estimar Difference GMM?" |
| GENERAL | 7 | "O que e o PanelBox?" |
| **Total** | **50** | |

---

## Tarefa 1.3: Implementacao de Metricas Automaticas

**Duracao**: 2-3 semanas
**Entrega**: `simulacoes/metrics.py`

### Metricas de Retrieval:
- [ ] nDCG@k (k=3, 5, 10) - normalized Discounted Cumulative Gain
- [ ] MRR (Mean Reciprocal Rank)
- [ ] Hit Rate@k (k=1, 3, 5)
- [ ] Precision@k
- [ ] Recall@k

### Metricas de Qualidade de Resposta:
- [ ] ROUGE-L (overlap textual com gold-standard)
- [ ] BERTScore (similaridade semantica)
- [ ] Faithfulness (respostas nao alucinam informacoes)
- [ ] Coverage (% dos fatos relevantes presentes na resposta)

### Metricas de Custo:
- [ ] Tokens consumidos por query
- [ ] Custo USD por query
- [ ] Latencia end-to-end (ms)
- [ ] Latencia por estagio (intent, graph, vector, community, generation)

---

## Tarefa 1.4: Execucao dos Baselines

**Duracao**: 2-3 semanas
**Entrega**: `simulacoes/baseline_results/`

### Baseline 1: Vector-Only RAG
- [ ] Usar apenas o VectorRetriever do sistema
- [ ] Pesos: graph=0.0, vector=1.0, community=0.0
- [ ] Rodar todas as 50 perguntas
- [ ] Salvar resultados com metricas

### Baseline 2: Static Weights (HybridRAG-style)
- [ ] Pesos fixos: graph=0.5, vector=0.5, community=0.0
- [ ] Sem entity resolution
- [ ] Sem intent classification
- [ ] Rodar todas as 50 perguntas

### Baseline 3: Microsoft GraphRAG Vanilla
- [ ] Extracao de entidades sem ontologia restrita
- [ ] Community summaries sem prompt de dominio
- [ ] Local + Global modes (sem fusao)
- [ ] Rodar todas as 50 perguntas

### Baseline 4: Nosso Sistema Completo
- [ ] Todos os componentes ativos
- [ ] Pesos adaptativos por intencao
- [ ] Entity resolution com aliases
- [ ] Community summaries especializados
- [ ] Rodar todas as 50 perguntas

---

## Criterios de Conclusao

FASE 1 esta completa quando:
- [ ] 25+ papers lidos e classificados
- [ ] BibTeX compilado
- [ ] 50+ perguntas definidas com gold-standard
- [ ] Metricas implementadas e testadas
- [ ] 4 baselines executados com resultados salvos
- [ ] Relatorio preliminar comparando baselines

---

*Status: Pendente*
*Inicio previsto: Marco 2026*
