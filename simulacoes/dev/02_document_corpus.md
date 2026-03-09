# TEST 02 — Corpus de 150 Documentos

## Objetivo

Construir o corpus de 150 documentos financeiros descrito na Section 4.3 do paper,
processar pela pipeline de ingestao, e popular o knowledge graph no Neo4j.

## Contexto

O paper afirma:

> "Document corpus. 150 financial documents comprising regulatory frameworks,
> SEC 10-K filings from S&P 100 companies, central bank resolutions, and
> 50 simulated audit reports."

Atualmente existem apenas 6 documentos regulatorios em
`implementacao/data/regulations/`. O diretorio `implementacao/data/filings/`
esta vazio.

## Composicao do corpus (150 documentos)

### Grupo 1: Frameworks regulatorios (20 documentos)

| # | Documento | Fonte | Formato | Status |
|---|-----------|-------|---------|--------|
| 1 | Basel III - Pillar 1 (Capital) | BCBS | MD | JA EXISTE |
| 2 | Basel III - Pillar 2 (Supervision) | BCBS | MD | JA EXISTE |
| 3 | Basel III - Pillar 3 (Disclosure) | BCBS | MD | JA EXISTE |
| 4 | Basel III - Leverage Ratio | BCBS | MD | CRIAR |
| 5 | Basel III - LCR Framework | BCBS | MD | CRIAR |
| 6 | Basel III - NSFR Framework | BCBS | MD | CRIAR |
| 7 | Basel III - FRTB (Market Risk) | BCBS | MD | CRIAR |
| 8 | Basel III - CVA Risk | BCBS | MD | CRIAR |
| 9 | Basel III - Output Floor | BCBS | MD | CRIAR |
| 10 | LGPD (Lei 13.709/2018) completa | Brasil | MD | JA EXISTE |
| 11 | GDPR - General Data Protection Regulation | EU | MD | CRIAR |
| 12 | GDPR - Recitals selecionados | EU | MD | CRIAR |
| 13 | SOX - Sarbanes-Oxley Act (secoes relevantes) | USA | MD | CRIAR |
| 14 | Dodd-Frank - Titulo VII (Derivativos) | USA | MD | CRIAR |
| 15 | BCB Resolucao 4.893/2021 | BCB | MD | JA EXISTE |
| 16 | BCB Resolucao 4.658/2018 | BCB | MD | JA EXISTE |
| 17 | BCB Resolucao 4.557/2017 (Gerenciamento de Riscos) | BCB | MD | CRIAR |
| 18 | CMN Resolucao 4.966/2021 (IFRS 9 Brasil) | CMN | MD | CRIAR |
| 19 | BCBS 239 - Risk Data Aggregation | BCBS | MD | CRIAR |
| 20 | BCBS - Corporate Governance Principles | BCBS | MD | CRIAR |

### Grupo 2: SEC 10-K Filings (30 documentos)

Selecionar 30 empresas do S&P 100 com diversidade setorial.
Extrair secoes relevantes de cada 10-K filing mais recente.

**Fonte**: SEC EDGAR (https://www.sec.gov/cgi-bin/browse-edgar)

**Secoes a extrair de cada 10-K**:
- Item 1A: Risk Factors
- Item 7: Management Discussion & Analysis (MD&A)
- Item 8: Financial Statements (notas selecionadas)

**Empresas sugeridas** (30 de setores diversos):

| # | Empresa | Ticker | Setor |
|---|---------|--------|-------|
| 1 | JPMorgan Chase | JPM | Banking |
| 2 | Bank of America | BAC | Banking |
| 3 | Goldman Sachs | GS | Investment Banking |
| 4 | Morgan Stanley | MS | Investment Banking |
| 5 | Citigroup | C | Banking |
| 6 | Wells Fargo | WFC | Banking |
| 7 | BlackRock | BLK | Asset Management |
| 8 | American Express | AXP | Financial Services |
| 9 | Visa | V | Payments |
| 10 | Mastercard | MA | Payments |
| 11 | Berkshire Hathaway | BRK.B | Conglomerate |
| 12 | MetLife | MET | Insurance |
| 13 | Progressive | PGR | Insurance |
| 14 | Charles Schwab | SCHW | Brokerage |
| 15 | S&P Global | SPGI | Financial Data |
| 16 | Apple | AAPL | Technology |
| 17 | Microsoft | MSFT | Technology |
| 18 | Amazon | AMZN | E-commerce |
| 19 | Alphabet | GOOGL | Technology |
| 20 | Meta | META | Technology |
| 21 | Johnson & Johnson | JNJ | Healthcare |
| 22 | Pfizer | PFE | Pharmaceuticals |
| 23 | UnitedHealth | UNH | Health Insurance |
| 24 | ExxonMobil | XOM | Energy |
| 25 | Chevron | CVX | Energy |
| 26 | Procter & Gamble | PG | Consumer Goods |
| 27 | Walmart | WMT | Retail |
| 28 | Coca-Cola | KO | Beverages |
| 29 | 3M | MMM | Industrials |
| 30 | Caterpillar | CAT | Industrials |

**Script de download**:

```python
# scripts/download_10k.py
import edgar  # pip install edgar-sec

def download_10k_sections(ticker: str, output_dir: str):
    """Download latest 10-K and extract relevant sections."""
    filing = edgar.get_filings(ticker, form_type="10-K", count=1)

    # Parse HTML -> extract Item 1A, Item 7, Item 8
    sections = extract_sections(filing)

    # Convert to Markdown
    for section_name, content in sections.items():
        filename = f"{ticker.lower()}_{section_name}.md"
        save_as_markdown(content, output_dir / filename)
```

### Grupo 3: Resolucoes do Banco Central (20 documentos)

| # | Documento | Tema |
|---|-----------|------|
| 1-6 | Ja existentes | Pillar 1, 2, 3, LGPD, BCB 4893, BCB 4658 |
| 7 | Res. 4.557/2017 | Gerenciamento integrado de riscos |
| 8 | Res. 4.677/2018 | Politica de seguranca cibernetica |
| 9 | Res. 4.945/2021 | Politica de sustentabilidade |
| 10 | Circ. 3.978/2020 | PLD/FT (prevencao a lavagem) |
| 11 | Circ. 3.681/2013 | Gerenciamento do risco de liquidez |
| 12 | Res. CMN 4.966/2021 | Instrumentos financeiros (IFRS 9) |
| 13 | Res. CMN 4.968/2021 | Demonstracoes financeiras |
| 14 | Carta Circular 4.001/2020 | Relatorios de riscos |
| 15 | Instrucao CVM 480 | Registro de emissores |
| 16 | Manual de supervisao BCB (trechos) | Supervisao prudencial |
| 17 | Res. CMN 4.606/2017 | Ouvidoria |
| 18 | Res. BCB 260/2022 | Open Finance |
| 19 | Res. BCB 229/2022 | Capital regulamentar |
| 20 | Res. BCB 356/2023 | Risco operacional (novo SMA) |

**Fonte**: https://www.bcb.gov.br/estabilidadefinanceira/buscanormas

**Formato**: Converter PDF/HTML para Markdown estruturado com headers H2/H3
para compatibilidade com o parser_markdown.py existente.

### Grupo 4: Audit Reports Simulados (50 documentos)

Gerar 50 relatorios de auditoria sinteticos usando Claude API.

**Template estruturado**:

```markdown
# Audit Report: {area} - {institution}

## Executive Summary
{summary}

## Scope
- Period: {period}
- Areas reviewed: {areas}
- Methodology: {methodology}

## Findings

### Finding {n}: {title}
- **Severity**: {Critical|High|Medium|Low}
- **Category**: {Compliance|Operational|Financial|IT}
- **Description**: {description}
- **Root Cause**: {root_cause}
- **Regulation Reference**: {regulation_articles}
- **Recommendation**: {recommendation}
- **Management Response**: {response}
- **Remediation Deadline**: {deadline}

## Control Assessment
| Control | Rating | Gaps |
|---------|--------|------|
| {control_name} | {Effective|Needs Improvement|Ineffective} | {gaps} |

## Overall Rating: {Satisfactory|Needs Improvement|Unsatisfactory}
```

**Distribuicao dos 50 reports**:

| Area | Quantidade | Temas |
|------|-----------|-------|
| Capital Adequacy | 8 | CET1, leverage ratio, stress testing |
| Credit Risk | 8 | PD/LGD models, provisioning, portfolio quality |
| Market Risk | 5 | VaR backtesting, FRTB readiness, limits |
| Operational Risk | 7 | SMA, incidents, business continuity |
| Compliance / AML | 7 | KYC, PLD/FT, sanctions screening |
| Data Protection | 5 | LGPD compliance, data governance, breach response |
| Cybersecurity | 5 | Penetration testing, access controls, BCB 4893 |
| IT General Controls | 5 | Change management, BCP/DR, SDLC |

**Script de geracao**:

```python
# scripts/generate_audit_reports.py

AUDIT_PROMPT = """Generate a realistic internal audit report for a Brazilian
financial institution. The report should cover {area} and reference specific
articles from {regulations}. Include {n_findings} findings with severity
levels and remediation recommendations.

Output format: Markdown with the following structure:
{template}
"""

async def generate_reports(count: int = 50):
    for i, config in enumerate(REPORT_CONFIGS):
        response = await claude_batch_api(
            prompt=AUDIT_PROMPT.format(**config),
            model="claude-haiku-4-5-20251001"
        )
        save_report(f"audit_{i+1:03d}_{config['area']}.md", response)
```

### Grupo 5: Documentos complementares (30 documentos)

| # | Tipo | Quantidade | Descricao |
|---|------|-----------|-----------|
| 1-10 | Relatorios de estabilidade financeira | 10 | BCB, Fed, ECB (trechos) |
| 11-20 | Notas tecnicas regulatorias | 10 | QIS, impact studies |
| 21-30 | Manuais de compliance | 10 | KYC, AML, controles internos |

## Estrutura de diretorios

```
implementacao/data/
├── regulations/          # Grupo 1 + 3 (40 docs)
│   ├── basel3_pillar1.md          (existente)
│   ├── basel3_pillar2.md          (existente)
│   ├── basel3_pillar3.md          (existente)
│   ├── basel3_leverage.md         (novo)
│   ├── basel3_lcr.md              (novo)
│   ├── basel3_nsfr.md             (novo)
│   ├── gdpr_full.md              (novo)
│   ├── sox_relevant.md            (novo)
│   ├── lgpd_full.md              (existente)
│   ├── bcb_resolucao_4893.md      (existente)
│   ├── bcb_resolucao_4658.md      (existente)
│   ├── bcb_resolucao_4557.md      (novo)
│   └── ...
├── filings/              # Grupo 2 (30 docs)
│   ├── jpm_risk_factors.md
│   ├── jpm_mda.md
│   ├── bac_risk_factors.md
│   └── ...
├── audit_reports/        # Grupo 4 (50 docs)
│   ├── audit_001_capital_adequacy.md
│   ├── audit_002_credit_risk.md
│   └── ...
└── supplementary/        # Grupo 5 (30 docs)
    ├── bcb_financial_stability_2024.md
    └── ...
```

## Pipeline de ingestao

Apos criar os documentos, rodar a pipeline existente:

```bash
# 1. Chunking
python scripts/ingest.py --step chunk --source-dir implementacao/data/ --full

# 2. Triple extraction (Batch API para economia)
python scripts/ingest.py --step extract --batch-size 50

# 3. Entity resolution
python scripts/ingest.py --step resolve

# 4. Graph loading
python scripts/ingest.py --step load

# 5. Community detection
python scripts/detect_communities.py

# 6. Build embeddings
python scripts/build_embeddings.py
```

## Estimativa de custos

| Etapa | Tokens estimados | Custo (Haiku Batch) |
|-------|-----------------|---------------------|
| Triple extraction (150 docs, ~1500 chunks) | ~400K input, ~280K output | ~$0.72 |
| Audit report generation (50 reports) | ~150K input, ~500K output | ~$2.12 |
| Community summaries (~50 communities) | ~50K input, ~25K output | ~$0.14 |
| **Total** | | **~$3.00** |

## Metricas esperadas do KG resultante

Baseado nos valores do paper (Table 1):

| Entity Type | Count esperado |
|-------------|---------------|
| Regulation | ~15 |
| Article | ~120 |
| Requirement | ~85 |
| RiskCategory | ~12 |
| FinancialMetric | ~45 |
| Company | ~50 |
| Subsidiary | ~80 |
| Jurisdiction | ~20 |
| Control | ~100 |
| AuditFinding | ~200 |
| **Total entities** | **~727** |

## Criterios de aceite

1. Exatamente 150 documentos no corpus
2. Pipeline de ingestao executa sem erros
3. KG resultante tem >= 500 entidades unicas
4. KG tem >= 1000 triples
5. Todos os 10 entity types da ontologia estao representados
6. Pelo menos 12 dos 14 relationship types estao presentes
7. Entity resolution atinge >= 85% de alias coverage
8. Custo total de ingestao <= $5.00

## Dependencias

- `graphrag/src/ingestion/pipeline.py` (pipeline completa)
- `implementacao/ontology/financial_ontology.yaml` (ontologia)
- `implementacao/ontology/financial_aliases.yaml` (aliases)
- API key Anthropic (para triple extraction e audit report generation)
- Neo4j rodando (docker-compose)
- Acesso ao SEC EDGAR (para 10-K downloads)

## Riscos

1. SEC EDGAR pode ter rate limiting — usar delays entre requests
2. Qualidade dos audit reports gerados depende do prompt — iterar no template
3. Documentos regulatorios muito longos (GDPR tem 88 paginas) — extrair secoes relevantes
4. Entity resolution pode precisar de novos aliases para cobrir SEC filings
