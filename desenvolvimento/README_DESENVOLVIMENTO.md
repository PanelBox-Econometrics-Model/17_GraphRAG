# GraphRAG Paper: Desenvolvimento em Fases

**Proposta**: 17_GraphRAG
**Tipo**: Systems / Applied AI
**Duracao total**: 8-12 meses
**Risco**: Baixo (sistema ja implementado)
**Status**: Planejamento

---

## VISAO GERAL

### O que e este paper?

Paper documentando um sistema GraphRAG **especializado em dominio** que demonstra como a customizacao end-to-end (ontologia, aliases, chunking, retrieval weights, community summaries) supera abordagens domain-agnostic para bibliotecas tecnicas especializadas.

### Por que o timing e bom?

- GraphRAG e um campo **nascente** (paper fundacional: abril 2024)
- Surveys de 2025 identificam lacunas exatamente nos pontos que cobrimos
- Nenhum paper combina todas estas contribuicoes
- Sistema ja funcional = menos risco de execucao

---

## ESTRUTURA DAS FASES

### FASE 1: Preparacao e Baseline (2 meses)
**Objetivo**: Compilar literatura, definir dataset de avaliacao, implementar metricas
**Risco**: Baixo
**Entrega**: Dataset de 50+ perguntas anotadas, baseline metrics

**Arquivo**: `FASE_1_PREPARACAO.md`

### FASE 2: Experimentos e Ablation (3 meses)
**Objetivo**: Ablation study completo, comparacao com baselines, analise de custo
**Risco**: Medio (resultados podem nao ser significativos)
**Entrega**: Todas as tabelas e figuras experimentais

**Arquivo**: `FASE_2_EXPERIMENTOS.md`

### FASE 3: Escrita do Manuscrito (3 meses)
**Objetivo**: Draft completo do paper, figuras, tabelas, supplementary
**Risco**: Baixo
**Entrega**: Manuscrito pronto para review interno

**Arquivo**: `FASE_3_ESCRITA.md`

### FASE 4: Revisao e Submissao (2 meses)
**Objetivo**: Review interno, ajustes, submissao ao journal
**Risco**: Baixo
**Entrega**: Paper submetido

**Arquivo**: `FASE_4_SUBMISSAO.md`

---

## TIMELINE

```
Mes 1-2:   FASE 1 (Preparacao)
Mes 3-5:   FASE 2 (Experimentos)
Mes 6-8:   FASE 3 (Escrita)
Mes 9-10:  FASE 4 (Submissao)
```

**Marcos importantes**:
- Mes 2: Dataset de avaliacao pronto
- Mes 5: Resultados experimentais completos
- Mes 8: Draft completo
- Mes 10: Paper submetido

---

## DELIVERABLES FINAIS

### Manuscrito
- [ ] `main.pdf` (30-40 paginas)
- [ ] `supplementary.pdf` (detalhes experimentais, exemplos adicionais)
- [ ] Replication package (codigo + dados + scripts)

### Dados
- [ ] Dataset de avaliacao: 50+ perguntas anotadas por tipo
- [ ] Gold-standard de respostas para avaliacao automatica
- [ ] Resultados de ablation study (JSON/CSV)
- [ ] Analise de custo detalhada

### Codigo
- [ ] Scripts de avaliacao (metricas automaticas)
- [ ] Scripts de ablation (remover componentes)
- [ ] Scripts de comparacao com baselines
- [ ] Jupyter notebooks de reproducao

---

*Criado em: Marco 2026*
*Status: Planejamento*
