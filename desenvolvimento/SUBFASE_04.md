# Subfase 04 - Paper: Introduction, Related Work, Methodology

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: SUBFASE_01, SUBFASE_02, SUBFASE_03
**Bloqueia**: SUBFASE_05

## Objetivo

Escrever as primeiras 4 secoes do paper para ESWA: Introduction, Related Work, System Architecture e Experimental Methodology. Formato LaTeX usando elsarticle class.

## Descricao Tecnica

**Journal target**: Expert Systems with Applications (ESWA) — Elsevier
- LaTeX class: `\documentclass[review]{elsarticle}`
- Formato: single column (review mode)
- Referencias: author-year (APA-like), usando `\bibliographystyle{model5-names}` com `\biboptions{authoryear}`
- Abstract: max 250 palavras, nao estruturado (paragrafo unico)
- Keywords: 1-7
- Highlights: 3-5 bullets, max 85 chars cada

**Proposta completa**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/PROPOSTA_6_GraphRAG.md`

**Literatura catalogada**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/literatura/REVISAO_LITERATURA.md`

**Resultados experimentais**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/results/`

**Arquivos a criar**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/main.tex`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/references.bib`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/figures/` (diagramas)

## INSTRUCAO CRITICA

**FORMATO ESWA obrigatorio**. O paper DEVE seguir estas regras:

1. **LaTeX class**: `elsarticle` com opcao `review`
2. **Abstract**: max 250 palavras, paragrafo unico, sem referencias
3. **Highlights**: arquivo separado ou secao, 3-5 bullets, max 85 caracteres cada
4. **Keywords**: 1-7 keywords apos abstract
5. **Referencias**: author-year format (Smith, 2024), nao numerico
6. **Secoes**: numeradas (1, 1.1, 1.1.1)
7. **Figuras/Tabelas**: alta resolucao, referenciadas no texto, captions descritivas
8. **Tamanho alvo**: 25-35 paginas single column

**Estrutura LaTeX base**:
```latex
\documentclass[review]{elsarticle}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}

\biboptions{authoryear}

\journal{Expert Systems with Applications}

\begin{document}
\begin{frontmatter}
\title{...}
\author{...}
\begin{abstract} ... \end{abstract}
\begin{keyword} ... \end{keyword}
\begin{highlights} ... \end{highlights}
\end{frontmatter}
...
\bibliographystyle{model5-names}
\bibliography{references}
\end{document}
```

### Etapa 1: Setup do projeto LaTeX

Criar estrutura:
```
paper/
├── main.tex          # Documento principal
├── references.bib    # Bibliografia
├── figures/          # Diagramas e figuras
└── tables/           # Tabelas de resultados
```

Configurar `main.tex` com:
- Frontmatter (titulo, abstract, keywords, highlights)
- Estrutura de secoes
- Bibliografia

### Etapa 2: Escrever Abstract (max 250 palavras)

Conteudo:
- Problema: LLMs em financas com alucinacao, custo, seguranca
- Proposta: GraphRAG multi-estrategia com 4 pilares
- Metodo: 5 experimentos, 3 aplicacoes financeiras
- Resultados chave: faithfulness >85%, reducao tokens >60%, latencia p50 <2s, 0% cross-tenant leakage
- Contribuicao: primeiro paper a abordar conjuntamente seguranca + eficiencia em GraphRAG financeiro

### Etapa 3: Escrever Highlights (3-5 bullets, max 85 chars)

Exemplos:
- "Multi-strategy GraphRAG architecture for regulated financial institutions"
- "Formal security model with threat analysis for financial RAG systems"
- "Intent-aware retrieval fusion reduces hallucination by 13+ percentage points"
- "Token consumption reduced by 60-80% through structured graph retrieval"
- "Open-source implementation with three empirical financial applications"

### Etapa 4: Escrever Section 1 — Introduction (4 paginas)

Estrutura:
1.1 Contexto (LLMs em financas, adocao crescente)
1.2 Problema (5 razoes por que RAG falha em financas — da PROPOSTA secao 1.1)
1.3 Gap na literatura (da PROPOSTA secao 1.2)
1.4 Contribuicoes (5 contribuicoes — da PROPOSTA Executive Summary)
1.5 Organizacao do paper

### Etapa 5: Escrever Section 2 — Related Work (5 paginas)

Estrutura baseada na REVISAO_LITERATURA.md:
2.1 GraphRAG Architectures (Edge et al. 2024, LightRAG, HippoRAG, surveys)
2.2 RAG for Financial Applications (HybridRAG, FinReflectKG, FinDKG, GraphCompliance, FinanceBench)
2.3 Security in RAG Systems (threat models, privacy risks, SAG, membership inference)
2.4 Token Efficiency (TERAG, LazyGraphRAG, PolyG, RAPTOR)

Cada subsecao: 3-5 paragrafos com citacoes author-year.
Final da secao: tabela comparativa (Table 1) mostrando gap.

### Etapa 6: Escrever Section 3 — System Architecture (8 paginas)

3.1 Formal Notation and Ontology
- Notacao matematica (G, V, E, phi, psi, T_V, T_E — da PROPOSTA secao 2.1)
- Tabela de entity types e relationship types

3.2 Ingestion Pipeline
- Chunking, Triple Extraction, Entity Resolution, Graph Loading
- Algorithm 1: Ingestion Pipeline (pseudocode)
- Figure 1: System Architecture diagram

3.3 Multi-Strategy Retrieval
- Intent Parser (6 types, weight table)
- Graph Retriever (N-hop, score formula)
- Vector Retriever (cosine similarity)
- Community Retriever (Leiden + summaries)
- Context Ranker (weighted fusion formula)
- Algorithm 2: Multi-Strategy Retrieval (pseudocode)
- Figure 2: Retrieval Pipeline diagram

3.4 Security Model
- Threat Model (Table: 5 threats)
- Defense Mechanisms (Table: 6 defenses)
- Compliance Mapping (Table: LGPD/GDPR/Basel III/SOX)

### Etapa 7: Escrever Section 4 — Experimental Methodology (4 paginas)

4.1 Baselines and Metrics
- Tabela de baselines (4 sistemas)
- Tabela de metricas (4 pilares x metricas)

4.2 Datasets and Evaluation Protocol
- 200 perguntas regulatorias
- 50 perguntas benchmark
- Protocolo de avaliacao (LLM-as-judge + amostra manual)

### Etapa 8: Criar references.bib

Incluir todas as 43+ referencias da REVISAO_LITERATURA.md em formato BibTeX.
Usar chaves consistentes: `edge2024graphrag`, `sarmah2024hybridrag`, etc.

## Criterios de Aceite

- [x] Projeto LaTeX criado com elsarticle class e estrutura completa
- [x] Abstract escrito (max 250 palavras, paragrafo unico)
- [x] Highlights escritos (3-5 bullets, max 85 chars cada)
- [x] Keywords definidos (1-7)
- [x] Section 1 (Introduction) escrita (~4 paginas)
- [x] Section 2 (Related Work) escrita (~5 paginas) com tabela comparativa
- [x] Section 3 (System Architecture) escrita (~8 paginas) com 2 algorithms e 2 figures
- [x] Section 4 (Experimental Methodology) escrita (~4 paginas) com tabelas de baselines e metricas
- [x] references.bib com >=40 entradas BibTeX
- [x] Paper compila sem erros com pdflatex/lualatex
- [x] Figuras criadas (architecture diagram, retrieval pipeline)

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| elsarticle template nao disponivel | Baixa | Alto | Download do CTAN ou usar Overleaf template |
| Paper muito longo (>35 paginas) | Media | Medio | Mover detalhes para online appendix |
| Figuras de baixa qualidade | Media | Medio | Usar TikZ ou pgfplots para diagramas vetoriais |
| Bibliografia incompleta | Baixa | Baixo | Cross-check com REVISAO_LITERATURA.md |

**End of Specification**
