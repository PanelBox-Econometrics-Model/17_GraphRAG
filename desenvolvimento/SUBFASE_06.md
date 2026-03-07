# Subfase 06 - Formatacao Final ESWA e Preparacao para Submissao

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: SUBFASE_05
**Bloqueia**: Nenhuma

## Objetivo

Finalizar formatacao do paper conforme guidelines ESWA, preparar materiais de submissao (highlights, graphical abstract, CRediT statement, cover letter, data availability), revisar qualidade geral e gerar PDF final.

## Descricao Tecnica

**ESWA submission requirements**:
1. Manuscript (PDF via LaTeX)
2. Highlights (3-5 bullets, max 85 chars)
3. Graphical Abstract (opcional mas recomendado, min 531x1328 px)
4. Cover Letter (destacando novidade)
5. CRediT Author Statement
6. Declaration of Competing Interests
7. Data Availability Statement
8. Supplementary material / Online Appendix

**Submission system**: Elsevier Editorial Manager
- URL: https://www.editorialmanager.com/eswa/

**Arquivos a criar/finalizar**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/main.tex` (revisao final)
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/highlights.tex`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/cover_letter.tex`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/graphical_abstract.pdf`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/appendix/online_appendix.tex`

## INSTRUCAO CRITICA

**Checklist ESWA antes da submissao**:
1. Abstract <= 250 palavras? Paragrafo unico?
2. Highlights: 3-5 bullets, cada um <= 85 caracteres?
3. Keywords: 1-7 keywords?
4. Referencias: formato author-year consistente?
5. Figuras: alta resolucao (300 DPI)?
6. Tabelas: sem linhas verticais, booktabs?
7. Declaration of Competing Interests incluida?
8. Data Availability Statement incluida?
9. CRediT statement incluida?
10. Paper compila sem warnings/errors?

**IMPORTANTE**: ESWA usa double-anonymized review. Remover informacoes identificadoras do manuscrito (nomes de autores, afiliacao, agradecimentos com nomes).

### Etapa 1: Revisao de formatacao LaTeX

Verificar:
- `\documentclass[review]{elsarticle}` correto
- `\biboptions{authoryear}` configurado
- `\bibliographystyle{model5-names}` usado
- Todas as secoes numeradas
- Todas as figuras e tabelas referenciadas no texto
- Equacoes numeradas
- Algoritmos formatados com `algorithm` + `algpseudocode`
- Listings de codigo com `listings` package

### Etapa 2: Preparar Highlights

Criar `highlights.tex` com 3-5 items:
```latex
\begin{highlights}
\item Multi-strategy GraphRAG for regulated financial institutions
\item Formal security model with five-threat analysis for financial RAG
\item Intent-aware retrieval fusion reduces hallucination by 13+ points
\item Structured retrieval cuts token consumption by 60-80 percent
\item Open-source implementation with three financial applications
\end{highlights}
```

Cada item: max 85 caracteres (contar cuidadosamente).

### Etapa 3: Preparar Cover Letter

Conteudo da cover letter:
- Enderecamento ao Editor-in-Chief
- Titulo do paper
- Contribuicao principal (2-3 sentencas)
- Por que ESWA (journal fit): expert system para financas, AI applied
- Novidade: primeiro paper a combinar 4 pilares em GraphRAG financeiro
- Confirmacao: nao submetido a outro journal
- Confirmacao: todos os autores aprovaram

### Etapa 4: Declaracoes obrigatorias

Incluir no paper:
```latex
\section*{Declaration of Competing Interest}
The authors declare that they have no known competing financial interests
or personal relationships that could have appeared to influence the work
reported in this paper.

\section*{Data Availability}
The implementation source code and benchmark datasets are available at
[repository URL]. SEC 10-K filings used in the study are publicly
available through the SEC EDGAR database.

\section*{CRediT Authorship Contribution Statement}
[Author 1]: Conceptualization, Methodology, Software, Writing - original draft.
[Author 2]: ...
```

### Etapa 5: Revisao de qualidade do texto

Verificar:
- Consistencia terminologica (GraphRAG vs Graph RAG, sempre o mesmo)
- Acronimos definidos na primeira ocorrencia
- Numeros com unidades (e.g., "4,000 tokens", "1.8 seconds")
- Voz consistente (ativa ou passiva)
- Sem repeticao excessiva de "we"
- Sem typos ou erros gramaticais
- Figuras e tabelas em posicao logica
- Cross-references corretas (\ref{}, \cite{})

### Etapa 6: Gerar PDF final

```bash
cd /home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Verificar:
- PDF compila sem erros
- Sem "??" em referencias
- Paginas dentro do range (25-35)
- Figuras visiveis e legiveis

### Etapa 7: Checklist final pre-submissao

Executar checklist completo e documentar status.

## Criterios de Aceite

- [x] Formatacao LaTeX revisada e consistente com ESWA guidelines
- [x] Abstract <= 250 palavras verificado
- [x] Highlights criados (3-5 bullets, cada <= 85 chars, verificado)
- [x] Keywords definidos (1-7)
- [x] Cover letter escrita
- [x] Declaration of Competing Interests incluida
- [x] Data Availability Statement incluida
- [x] CRediT Author Statement incluida
- [x] Informacoes identificadoras removidas (double-blind)
- [x] Revisao de qualidade do texto completa
- [x] Todas as figuras em alta resolucao (300 DPI)
- [x] Todas as tabelas com booktabs (sem linhas verticais)
- [x] Cross-references corretas (sem "??")
- [x] PDF final gerado sem erros
- [x] Paper entre 25-35 paginas
- [x] Online Appendix preparado como material suplementar

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| elsarticle class incompativel com packages | Baixa | Medio | Testar compilacao apos cada package adicionada |
| Highlights excedem 85 chars | Media | Baixo | Contar caracteres manualmente |
| Figuras pixeladas no PDF | Baixa | Medio | Usar formato vetorial (PDF/EPS) para diagramas |
| Paper muito longo apos formatacao | Media | Medio | Mover conteudo para appendix |

**End of Specification**
