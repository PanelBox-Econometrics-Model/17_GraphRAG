# GraphRAG Paper - Plano de Desenvolvimento

## Objetivo

Construir e submeter paper ao **Expert Systems with Applications (ESWA)** sobre GraphRAG para instituicoes financeiras.

## Journal Target

- **Expert Systems with Applications (ESWA)** — Elsevier
- Impact Factor: 7.5 (WoS) / CiteScore: 12.2-15
- Acceptance rate: ~16%
- Formato: elsarticle LaTeX, single column (review), ~25-35 paginas
- Abstract: max 250 palavras
- Highlights: 3-5 bullets, max 85 chars cada
- Referencias: author-year (APA-like)

## Subfases

| Subfase | Descricao | Dependencia |
|---------|-----------|-------------|
| 01 | Ontologia financeira + corpus + KG | Nenhuma |
| 02 | Experimentos e benchmarks (5 experimentos) | 01 |
| 03 | Avaliacao de seguranca + threat model | 02 |
| 04 | Paper: Introduction, Related Work, Methodology | 01+02+03 |
| 05 | Paper: Results, Applications, Discussion, Conclusion | 04 |
| 06 | Formatacao ESWA, highlights, submission | 05 |

## Execucao

```bash
cd /home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento
chmod +x prompt.sh
./prompt.sh
```

## Monitoramento

```bash
# Status rapido
cat /home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/LOG/status.txt

# Log em tempo real
tail -f /home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/LOG/latest.log

# Log Claude atual
tail -f /home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/LOG/claude_current.log
```
