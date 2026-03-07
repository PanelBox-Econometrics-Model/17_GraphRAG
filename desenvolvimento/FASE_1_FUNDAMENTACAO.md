# FASE 1: Fundamentação e Adaptação ao Domínio Financeiro

**Duração**: 2 meses
**Esforço**: 15 horas/semana
**Risco**: Baixo
**Status**: 🔴 Não iniciada

---

## OBJETIVOS

1. Adaptar a ontologia do PanelBox GraphRAG para o domínio financeiro
2. Curar e processar corpus de documentos regulatórios e financeiros
3. Construir knowledge graph financeiro funcional com >500 triplas validadas
4. Validar entity resolution para entidades financeiras
5. Aprofundar revisão de literatura e identificar positioning do paper

---

## PRÉ-REQUISITOS

- [x] Implementação GraphRAG funcional (`/graphrag`)
- [x] Neo4j 5.x instalado e configurado
- [x] PostgreSQL 16 com migrações
- [x] Chave API Anthropic (Claude)
- [x] Revisão de literatura inicial (43 papers em `literatura/REVISAO_LITERATURA.md`)
- [ ] Familiaridade com a ontologia atual (`ontology/panelbox_ontology.yaml`)
- [ ] Acesso ao EDGAR para download de SEC filings

---

## TAREFA 1: Estudar a Ontologia Atual

### Contexto

A ontologia atual do PanelBox define 10 entity types e 14 relationship types voltados para econometria de painel. Precisamos entender profundamente a estrutura para adaptá-la ao domínio financeiro.

### Atividades

1. Ler e documentar `ontology/panelbox_ontology.yaml`:
   - Entity types atuais: Estimator, DiagnosticTest, Parameter, StatisticalConcept, Literature, ModelFamily, StandardError, Dataset, CodePattern, ResultMetric
   - Relationship types atuais: BELONGS_TO, INHERITS_FROM, VALIDATES, REQUIRES, PRODUCES, ADDRESSES, TESTS_FOR, BASED_ON, ALTERNATIVE_TO, PRECONDITION, SUPPORTS_SE, DEMONSTRATED_IN, IMPLEMENTED_BY, SUCCEEDS
   - Propriedades de cada tipo (required vs optional)

2. Ler `ontology/aliases.yaml` (~130 aliases):
   - Entender padrão de mapeamento de aliases
   - Identificar como bilíngue (PT/EN) é tratado

3. Ler `ontology/seed_entities.yaml`:
   - Entender formato de seed knowledge
   - Modelo para criar seeds financeiros

### Entregável
- [ ] Documento `teoria/analise_ontologia_atual.md` descrevendo a ontologia e gaps para finanças

---

## TAREFA 2: Definir Ontologia Financeira

### Contexto

A ontologia financeira precisa capturar entidades e relações do domínio regulatório e financeiro. Deve ser compatível com o pipeline de extração existente.

### Entity Types Propostos

```yaml
entity_types:
  # Regulatórios
  Regulation:       # Basel III, LGPD, GDPR, Resoluções BCB
  Article:          # Artigos específicos de regulações
  Requirement:      # Requisitos regulatórios (capital, liquidez, etc.)
  Obligation:       # Obrigações de compliance

  # Financeiros
  Company:          # Empresas, bancos, instituições
  Subsidiary:       # Subsidiárias e controladas
  FinancialMetric:  # Receita, lucro, índice de basileia, etc.
  RiskCategory:     # Risco de crédito, mercado, operacional, liquidez

  # Auditoria
  AuditFinding:     # Achados de auditoria
  Control:          # Controles internos
  Recommendation:   # Recomendações de auditoria

  # Jurisdição
  Jurisdiction:     # Brasil, EU, EUA, etc.
  Regulator:        # BCB, SEC, EBA, etc.
```

### Relationship Types Propostos

```yaml
relationship_types:
  REGULATES:        # Regulation → Company/Sector
  REQUIRES:         # Regulation → Requirement
  DEFINES:          # Regulation → Concept/Metric
  EXPOSES_TO:       # Company → RiskCategory
  SUBSIDIARY_OF:    # Subsidiary → Company
  OPERATES_IN:      # Company → Jurisdiction
  AUDITED_BY:       # Company → Regulator
  MITIGATES:        # Control → RiskCategory
  REFERENCES:       # Article → Article (cross-references)
  SUPERSEDES:       # Regulation → Regulation (versioning)
  COMPOSED_OF:      # Regulation → Article
  REPORTS_TO:       # Company → Regulator
  VALIDATED_BY:     # FinancialMetric → AuditFinding
  COMPLIES_WITH:    # Company → Regulation
```

### Atividades

1. Criar `ontology/financial_ontology.yaml` seguindo formato do `panelbox_ontology.yaml`
2. Definir propriedades para cada entity type:
   - name (required, unique)
   - description (required)
   - Propriedades específicas (e.g., year para FinancialMetric, severity para AuditFinding)
3. Definir constraints e indexes para Neo4j
4. Validar que o pipeline de extração (`src/ingestion/prompts.py`) aceita os novos tipos

### Entregável
- [ ] Arquivo `ontology/financial_ontology.yaml` completo
- [ ] Arquivo `ontology/financial_aliases.yaml` com aliases iniciais (~50+)

---

## TAREFA 3: Curar Corpus Regulatório

### Contexto

Precisamos de um corpus de documentos financeiros e regulatórios em formato processável (Markdown) para alimentar o pipeline de ingestão.

### Documentos a Curar

**Prioridade Alta** (obrigatórios):
1. **Basel III Framework** — Comitê de Basileia
   - Pilar 1: Requisitos mínimos de capital
   - Pilar 2: Processo de supervisão
   - Pilar 3: Divulgação de mercado
   - Fonte: bis.org (público)

2. **LGPD** — Lei nº 13.709/2018
   - Texto integral (65 artigos)
   - Fonte: planalto.gov.br (público)

3. **Resoluções BCB selecionadas**:
   - Res. 4.893/2021 (Política de Segurança Cibernética)
   - Res. 4.658/2018 (Política de Segurança)
   - Fonte: bcb.gov.br (público)

**Prioridade Média** (desejáveis):
4. **GDPR** — Regulamento UE 2016/679 (texto integral)
5. **SEC 10-K filings** — S&P 100 (subconjunto de 10-20 empresas)
   - Download via SEC EDGAR
   - Converter HTML → Markdown

**Prioridade Baixa** (opcionais):
6. SOX Section 404 — texto resumido
7. Manuais internos de compliance (sintéticos)

### Formato Alvo

Cada documento deve ser convertido para Markdown com:
- Headers H2 para seções principais
- Headers H3 para subseções
- Texto limpo sem formatação HTML residual
- Metadados YAML front matter:
  ```yaml
  ---
  title: "Basel III - Pilar 1: Requisitos Mínimos de Capital"
  source: "Bank for International Settlements"
  year: 2023
  type: regulation
  jurisdiction: international
  ---
  ```

### Atividades

1. Download e conversão dos documentos de Prioridade Alta
2. Organização em `data/regulations/` e `data/filings/`
3. Verificar qualidade da conversão (headers corretos, texto legível)
4. Testar chunking com `Chunker` existente

### Entregável
- [ ] Corpus organizado em `data/regulations/` (~20 documentos Markdown)
- [ ] (Opcional) `data/filings/` com 10-20 SEC 10-K filings convertidos
- [ ] Relatório de estatísticas: nº de arquivos, tokens totais, chunks estimados

---

## TAREFA 4: Processar Corpus via Pipeline

### Contexto

Usar o pipeline de ingestão existente para processar o corpus financeiro e construir o knowledge graph.

### Atividades

1. **Chunking**: Executar `Chunker` no corpus regulatório
   ```python
   chunker = Chunker(cache_dir="data/chunks")
   chunks = chunker.process_sources([
       {"path": "data/regulations", "file_types": [".md"]},
   ], incremental=True)
   print(chunker.get_stats())
   ```
   - Verificar que chunks são significativos (não muito pequenos/grandes)
   - Ajustar parsers se necessário

2. **Extração de Triplas**: Executar `TripleExtractor` com ontologia financeira
   - Atualizar `src/ingestion/prompts.py` com os novos entity/relation types
   - Usar Batch API para economia
   - Monitorar qualidade das triplas extraídas

3. **Resolução de Entidades**: Executar `EntityResolver`
   - Usar `financial_aliases.yaml`
   - Monitorar taxa de resolução (exact vs fuzzy vs unresolved)
   - Ajustar aliases e threshold conforme necessário

4. **Carregamento no Grafo**: Executar `GraphLoader`
   - Verificar constraints no Neo4j
   - Inspecionar grafo resultante via Neo4j Browser

5. **Detecção de Comunidades**: Executar `CommunityDetector`
   - Verificar que comunidades são semanticamente coerentes
   - Gerar e validar resumos de comunidade

### Métricas a Coletar

```
- Nº de chunks criados
- Nº de triplas extraídas (raw)
- Nº de triplas resolvidas
- Taxa de resolução (exact / fuzzy / unresolved)
- Nº de entidades únicas no grafo
- Nº de relacionamentos
- Nº de comunidades detectadas
- Tokens consumidos na extração
- Custo total (API)
```

### Entregável
- [ ] Knowledge graph financeiro no Neo4j com >500 triplas
- [ ] Relatório de métricas do pipeline
- [ ] Screenshots do Neo4j Browser mostrando o grafo

---

## TAREFA 5: Validar Qualidade do Knowledge Graph

### Contexto

Antes de prosseguir para experimentos, precisamos validar que o KG tem qualidade suficiente.

### Atividades

1. **Amostragem**: Selecionar 50 triplas aleatórias do grafo
2. **Avaliação manual**: Para cada tripla, verificar:
   - Sujeito é uma entidade válida? (Sim/Não)
   - Predicado é correto? (Sim/Não)
   - Objeto é uma entidade válida? (Sim/Não)
   - Confiança está calibrada? (Alta confiança = correto, baixa = questionável)
3. **Calcular métricas**:
   - Precision: % de triplas corretas na amostra
   - Entity type accuracy: % de entidades com tipo correto
   - Relationship accuracy: % de relacionamentos semanticamente corretos

### Critério de Sucesso

- Precision > 80% na amostra de 50 triplas
- Entity type accuracy > 85%
- Se abaixo: voltar à Tarefa 2/3 para ajustar ontologia/aliases

### Entregável
- [ ] Planilha de avaliação (50 triplas anotadas)
- [ ] Métricas de qualidade documentadas
- [ ] Decisão GO/NO-GO para Fase 2

---

## TAREFA 6: Aprofundar Revisão de Literatura

### Contexto

A revisão inicial (43 papers em `REVISAO_LITERATURA.md`) cobre a área amplamente. Nesta tarefa, aprofundamos em papers específicos para o positioning do nosso paper.

### Papers Obrigatórios (Leitura Completa)

1. **Edge et al. (2024)** — Microsoft GraphRAG (arXiv:2404.16130)
   - Entender detalhes de Leiden community detection
   - Comparar com nossa implementação

2. **Sarmah et al. (2024)** — HybridRAG (arXiv:2408.04948)
   - Entender métricas usadas para financial documents
   - Identificar gaps que nosso paper preenche

3. **Han et al. (2025)** — RAG vs GraphRAG (arXiv:2502.11371)
   - Entender framework de avaliação
   - Adaptar métricas para nosso contexto

4. **Privacy Risks in GraphRAG (2025)** (arXiv:2508.17222)
   - Entender vetores de ataque a GraphRAG
   - Informar nosso threat model

5. **PolyG (2025)** (arXiv:2504.02112)
   - Entender adaptive query planning
   - Comparar com nosso intent parser

### Papers Complementares (Leitura Direcionada)

6. **FinReflectKG** (arXiv:2508.17906) — pipeline de extração financeiro
7. **GraphCompliance** (arXiv:2510.26309) — compliance com grafos
8. **TERAG** (arXiv:2509.18667) — eficiência de tokens
9. **SAG** (arXiv:2508.01084) — segurança provável

### Atividades

1. Ler papers obrigatórios integralmente
2. Ler seções relevantes dos complementares
3. Atualizar `REVISAO_LITERATURA.md` com notas aprofundadas
4. Identificar positioning statement do nosso paper:
   - O que fazemos que ninguém mais faz?
   - Quais claims podemos fazer com evidência?
   - Quais claims devemos evitar?

### Entregável
- [ ] `REVISAO_LITERATURA.md` atualizado com notas aprofundadas
- [ ] Positioning statement draft (1 parágrafo)
- [ ] Tabela comparativa detalhada (nosso paper vs top 5 concorrentes)

---

## TAREFA 7: Teste Inicial de Retrieval Financeiro

### Contexto

Antes de prosseguir para benchmarks formais, testar o retrieval com queries financeiras informais para verificar que o sistema funciona end-to-end.

### Atividades

1. Preparar 10 queries de teste informais:
   ```
   Q1: "O que é Basel III Pilar 2?"
   Q2: "Quais artigos da LGPD tratam de dados financeiros?"
   Q3: "Compare os requisitos de capital de Basel III vs Basel II"
   Q4: "Quais são os riscos operacionais sob Basel III?"
   Q5: "O Art. 18 da LGPD se aplica a dados de crédito?"
   Q6: "Quais controles mitigam risco de crédito?"
   Q7: "Quem regula instituições financeiras no Brasil?"
   Q8: "Qual a relação entre LGPD Art. 46 e Res. BCB 4.893?"
   Q9: "Quais subsidiárias estão expostas a risco cambial?"
   Q10: "Resuma os achados de auditoria de risco operacional"
   ```

2. Executar cada query no sistema completo
3. Avaliar qualitativamente:
   - Intent foi classificado corretamente?
   - Entidades foram extraídas?
   - Contexto recuperado é relevante?
   - Resposta é factualmente correta?

4. Identificar problemas:
   - Entidades não reconhecidas → adicionar a aliases
   - Comunidades sem sentido → ajustar resolução Leiden
   - Retrieval fraco → ajustar pesos ou threshold

### Entregável
- [ ] Relatório de teste (10 queries, classificação, resultado qualitativo)
- [ ] Lista de ajustes necessários (aliases, pesos, thresholds)

---

## TAREFA 8: Decisão GO/NO-GO

### Critérios para prosseguir à Fase 2

| Critério | Threshold | Status |
|----------|-----------|--------|
| Triplas no KG | >500 | [ ] |
| Precision das triplas | >80% | [ ] |
| Entity types financeiros | ≥10 | [ ] |
| Relationship types | ≥14 | [ ] |
| Teste informal (10 queries) | ≥6/10 relevantes | [ ] |
| Corpus regulatório processado | ≥10 documentos | [ ] |
| Posicionamento do paper definido | Sim | [ ] |

**Se todos os critérios forem atendidos**: Prosseguir para Fase 2.

**Se parcialmente atendidos**: Iterar nas tarefas necessárias (mais aliases, mais documentos, ajuste de pipeline).

**Se não atendidos**: Reavaliar escopo ou pivotar abordagem.

### Entregável
- [ ] Decisão documentada (GO/NO-GO/ITERAR)
- [ ] Plano de ajustes se necessário

---

## ENTREGAS FINAIS DA FASE 1

- [ ] `ontology/financial_ontology.yaml` — Ontologia financeira completa
- [ ] `ontology/financial_aliases.yaml` — Aliases financeiros (≥50)
- [ ] `data/regulations/` — Corpus regulatório curado (≥10 documentos)
- [ ] Knowledge graph no Neo4j com >500 triplas validadas
- [ ] `teoria/analise_ontologia_atual.md` — Análise da ontologia
- [ ] `REVISAO_LITERATURA.md` — Atualizado com notas aprofundadas
- [ ] Relatório de métricas do pipeline
- [ ] Relatório de teste informal (10 queries)
- [ ] Decisão GO/NO-GO documentada
