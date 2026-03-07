# Guia de Desenvolvimento — Paper 17: GraphRAG para Instituições Financeiras

## Objetivo

Desenvolver um paper acadêmico que propõe e avalia uma arquitetura GraphRAG para instituições financeiras, abordando quatro pilares: segurança, redução de alucinações, economia de tokens e velocidade de processamento.

## Periódico-alvo

Expert Systems with Applications, Decision Support Systems, Journal of Financial Data Science

## Duração Estimada

10 meses (5 fases)

---

## Visão Geral das Fases

| Fase | Nome | Duração | Status |
|------|------|---------|--------|
| 1 | Fundamentação e Adaptação ao Domínio Financeiro | 2 meses | 🔴 Não iniciada |
| 2 | Experimentos e Benchmarks | 2 meses | ⚪ Aguardando Fase 1 |
| 3 | Avaliação de Segurança | 1 mês | ⚪ Aguardando Fase 2 |
| 4 | Aplicações Empíricas | 2 meses | ⚪ Aguardando Fase 3 |
| 5 | Escrita e Submissão | 3 meses | ⚪ Aguardando Fase 4 |

---

## Estrutura de Arquivos Esperada

```
17_GraphRAG/
├── PROPOSTA_6_GraphRAG.md              # Proposta completa
├── README.md                           # Overview do paper
├── desenvolvimento/                    # Guias de desenvolvimento
│   ├── README_DESENVOLVIMENTO.md       # Este arquivo
│   ├── FASE_1_FUNDAMENTACAO.md         # Prompt autocontido Fase 1
│   ├── FASE_2_EXPERIMENTOS.md          # Prompt autocontido Fase 2
│   ├── FASE_3_SEGURANCA.md             # Prompt autocontido Fase 3
│   ├── FASE_4_APLICACOES.md            # Prompt autocontido Fase 4
│   └── FASE_5_ESCRITA.md               # Prompt autocontido Fase 5
├── literatura/                         # Revisão bibliográfica
│   └── REVISAO_LITERATURA.md           # 43 papers catalogados
├── teoria/                             # Fundamentação teórica
│   ├── ontologia_financeira.yaml       # Ontologia adaptada
│   ├── threat_model.md                 # Modelo formal de ameaças
│   └── formalizacao_retrieval.md       # Formalização matemática
├── simulacoes/                         # Benchmarks e experimentos
│   ├── datasets/                       # Datasets de avaliação
│   │   ├── regulatory_questions_200.json
│   │   └── benchmark_50.json
│   ├── results/                        # Resultados experimentais
│   └── scripts/                        # Scripts de avaliação
├── implementacao/                      # Adaptações ao código
│   ├── financial_ontology/             # Ontologia financeira
│   ├── baselines/                      # Implementação de baselines
│   └── security/                       # Módulos de segurança
├── aplicacoes/                         # Aplicações empíricas
│   ├── compliance/                     # Aplicação 1: Compliance
│   ├── financial_reports/              # Aplicação 2: SEC filings
│   └── audit_qa/                       # Aplicação 3: Auditoria
└── paper/                              # Manuscrito final
    ├── main.tex                        # Documento LaTeX principal
    ├── figures/                        # Figuras e diagramas
    ├── tables/                         # Tabelas de resultados
    └── appendix/                       # Online appendix
```

---

## Dependências entre Fases

```
FASE 1 (Fundamentação)
  │
  ├──→ FASE 2 (Experimentos)
  │       │
  │       └──→ FASE 3 (Segurança)
  │               │
  │               └──→ FASE 4 (Aplicações)
  │                       │
  │                       └──→ FASE 5 (Escrita)
  │
  └──→ (literatura contínua ao longo de todas as fases)
```

---

## Critérios de Sucesso por Fase

### Fase 1: Fundamentação
- [ ] Ontologia financeira definida com ≥10 entity types e ≥14 relationship types
- [ ] Corpus regulatório curado (Basel III + LGPD + resoluções BCB)
- [ ] Knowledge graph financeiro construído com >500 triplas
- [ ] Entity resolution validado para entidades financeiras (>80% precision)
- [ ] Revisão de literatura atualizada e aprofundada

### Fase 2: Experimentos
- [ ] 200 perguntas regulatórias com ground truth criadas
- [ ] 50 perguntas de benchmark financeiro adaptadas
- [ ] 3 baselines implementados e executados
- [ ] Métricas quantitativas para Experimentos 1-3 e 5 coletadas
- [ ] Resultados documentados em tabelas

### Fase 3: Segurança
- [ ] Tenant isolation implementado no Neo4j
- [ ] Red-team testing executado (cross-tenant, entity extraction, membership inference)
- [ ] Threat model formalizado
- [ ] Mapeamento de compliance documentado (LGPD, GDPR, Basel III, SOX)
- [ ] Experimento 4 executado com métricas

### Fase 4: Aplicações
- [ ] 3 aplicações empíricas executadas e documentadas
- [ ] Feedback de practitioners coletado (se possível)
- [ ] Resultados consolidados

### Fase 5: Escrita
- [ ] Draft completo (~40 páginas)
- [ ] Online appendix preparado
- [ ] Código de replicação disponibilizado
- [ ] Paper submetido

---

## Pontos de Decisão Críticos

### Após Fase 1 (GO/NO-GO):
- Knowledge graph tem qualidade suficiente? (>500 triplas, >80% precision)
- Ontologia financeira é expressiva o suficiente para as 3 aplicações?
- Se não: pivotar para ontologia mais simples ou mudar escopo das aplicações

### Durante Fase 2:
- Resultados de GraphRAG vs VectorRAG mostram diferença significativa (>10 pp)?
- Se não: focar em queries multi-hop onde a diferença é maior, ou ajustar pesos de retrieval

### Após Fase 3:
- Segurança é forte o suficiente para publicação?
- Se resultados de red-team são preocupantes: focar em framework/recomendações em vez de garantias

### Após Fase 4:
- Resultados empíricos suportam as claims?
- Se resultados são fracos em alguma aplicação: remover ou mover para appendix

---

## Recursos Necessários

### Infraestrutura
- Servidor com Neo4j 5.x + PostgreSQL 16 (disponível)
- Chave API Anthropic (Claude) — orçamento estimado: ~$200 total
- GPU para sentence-transformers (CPU é suficiente para all-MiniLM-L6-v2)

### Dados
- SEC EDGAR para 10-K filings (gratuito, público)
- Textos regulatórios (Basel III, LGPD — públicos)
- Dados de auditoria sintéticos (a serem gerados)

### Humanos
- Especialista em compliance para validação (Aplicação 1)
- Analista financeiro para validação (Aplicação 2)
- (Opcional) Auditor para feedback (Aplicação 3)
