# Subfase 01 - Ontologia Financeira, Corpus e Knowledge Graph

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: Nenhuma
**Bloqueia**: SUBFASE_02, SUBFASE_03

## Objetivo

Adaptar a ontologia do PanelBox GraphRAG para o dominio financeiro, curar corpus regulatorio, processar documentos e construir knowledge graph financeiro com >500 triplas validadas.

## Descricao Tecnica

**Implementacao de referencia**: `/home/guhaase/projetos/panelbox/graphrag/`

**Ontologia atual** (PanelBox):
- Arquivo: `/home/guhaase/projetos/panelbox/graphrag/ontology/panelbox_ontology.yaml`
- 10 entity types: Estimator, DiagnosticTest, Parameter, StatisticalConcept, Literature, ModelFamily, StandardError, Dataset, CodePattern, ResultMetric
- 14 relationship types: BELONGS_TO, INHERITS_FROM, VALIDATES, REQUIRES, PRODUCES, ADDRESSES, TESTS_FOR, BASED_ON, ALTERNATIVE_TO, PRECONDITION, SUPPORTS_SE, DEMONSTRATED_IN, IMPLEMENTED_BY, SUCCEEDS

**Pipeline existente**:
- Chunker: `src/ingestion/chunker.py` (Python/Markdown/Notebook parsers)
- Triple Extractor: `src/ingestion/triple_extractor.py` (Claude API + Batch API)
- Entity Resolver: `src/ingestion/entity_resolver.py` (alias + fuzzy matching, threshold=85%)
- Graph Loader: `src/graph/graph_loader.py` (Cypher MERGE -> Neo4j)
- Prompts: `src/ingestion/prompts.py` (ontology-constrained extraction)

**Corpus a curar**:
- Basel III Framework (bis.org — publico)
- LGPD Lei 13.709/2018 (planalto.gov.br — publico)
- Resolucoes BCB selecionadas (bcb.gov.br — publico)
- SEC 10-K filings (EDGAR — publico, subconjunto 10-20 empresas)

**Arquivos a criar**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/ontology/financial_ontology.yaml`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/ontology/financial_aliases.yaml`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/data/regulations/*.md`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/data/filings/*.md`

## INSTRUCAO CRITICA

**ANTES de criar qualquer arquivo**, leia a ontologia existente:
```bash
cat /home/guhaase/projetos/panelbox/graphrag/ontology/panelbox_ontology.yaml
cat /home/guhaase/projetos/panelbox/graphrag/ontology/aliases.yaml
cat /home/guhaase/projetos/panelbox/graphrag/src/ingestion/prompts.py
```

Entenda o formato EXATO para replicar na ontologia financeira.

### Etapa 1: Definir ontologia financeira

Criar `financial_ontology.yaml` com entity types financeiros:
- Regulation, Article, Requirement, Obligation (regulatorios)
- Company, Subsidiary, FinancialMetric, RiskCategory (financeiros)
- AuditFinding, Control, Recommendation (auditoria)
- Jurisdiction, Regulator (jurisdicao)

E relationship types:
- REGULATES, REQUIRES, DEFINES, EXPOSES_TO, SUBSIDIARY_OF
- OPERATES_IN, AUDITED_BY, MITIGATES, REFERENCES, SUPERSEDES
- COMPOSED_OF, REPORTS_TO, VALIDATED_BY, COMPLIES_WITH

### Etapa 2: Criar aliases financeiros

Criar `financial_aliases.yaml` com pelo menos 50 aliases mapeando:
- "Basel III" -> BaselIII, "basileia iii" -> BaselIII
- "LGPD" -> LGPD, "lei geral de protecao de dados" -> LGPD
- Nomes de empresas, reguladores, metricas financeiras
- Bilingual (PT/EN)

### Etapa 3: Curar corpus regulatorio

Converter documentos regulatorios para Markdown:
- Basel III Pilar 1, 2, 3 (resumos estruturados)
- LGPD texto integral (65 artigos)
- Resolucoes BCB 4.893/2021 e 4.658/2018

Formato alvo: Markdown com headers H2/H3, YAML front matter:
```yaml
---
title: "Basel III - Pilar 1"
source: "Bank for International Settlements"
year: 2023
type: regulation
jurisdiction: international
---
```

### Etapa 4: Processar corpus via pipeline

Executar pipeline existente com ontologia financeira:
1. Chunking dos documentos
2. Extracao de triplas (ajustar prompts.py para tipos financeiros)
3. Resolucao de entidades
4. Carregamento no Neo4j

### Etapa 5: Validar qualidade do KG

Amostrar 50 triplas e avaliar:
- Precision > 80%
- Entity type accuracy > 85%
- Documentar metricas

## Criterios de Aceite

- [x] Ontologia financeira criada com >=12 entity types e >=14 relationship types
- [x] Arquivo financial_aliases.yaml com >=50 aliases bilingual (PT/EN)
- [x] Corpus Basel III (Pilar 1, 2, 3) convertido para Markdown
- [x] Corpus LGPD (65 artigos) convertido para Markdown
- [x] Resolucoes BCB convertidas para Markdown
- [x] Pipeline de ingestao executado com ontologia financeira
- [x] Knowledge graph no Neo4j com >=500 triplas
- [x] Amostra de 50 triplas avaliada com precision >=80%
- [x] Metricas do pipeline documentadas (chunks, triplas, entidades, custo)
- [x] Teste informal com 10 queries financeiras executado e documentado

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Qualidade de extracao baixa com ontologia nova | Media | Alto | Ajustar prompts few-shot com exemplos financeiros |
| Documentos regulatorios dificeis de converter | Baixa | Medio | Usar versoes resumidas se necessario |
| Entity resolution falha em entidades financeiras | Media | Medio | Expandir aliases e ajustar threshold |
| Pipeline nao aceita novos entity types | Baixa | Alto | Verificar validacao em prompts.py antes |

**End of Specification**
