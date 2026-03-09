#!/usr/bin/env python3
"""Prepare additional regulatory documents for the GraphRAG corpus.

Generates 14 regulatory documents that complement the 6 existing ones in
implementacao/data/regulations/. These are structured Markdown documents
with proper headers for the markdown parser.

Usage:
    # Generate all additional regulations
    python prepare_regulations.py --output-dir implementacao/data/regulations/

    # Dry run (show what would be created)
    python prepare_regulations.py --dry-run

    # Generate specific documents
    python prepare_regulations.py --docs basel3_leverage gdpr_full
"""

import argparse
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Documents to generate (14 additional to complement existing 6)
REGULATION_DOCS = {
    "basel3_leverage": {
        "title": "Basel III - Leverage Ratio Framework",
        "source": "BCBS",
        "description": "Leverage ratio requirements as a non-risk-based backstop measure",
    },
    "basel3_lcr": {
        "title": "Basel III - Liquidity Coverage Ratio (LCR)",
        "source": "BCBS",
        "description": "Short-term liquidity requirements ensuring HQLA sufficiency",
    },
    "basel3_nsfr": {
        "title": "Basel III - Net Stable Funding Ratio (NSFR)",
        "source": "BCBS",
        "description": "Long-term stable funding requirements",
    },
    "basel3_frtb": {
        "title": "Basel III - Fundamental Review of the Trading Book (FRTB)",
        "source": "BCBS",
        "description": "Revised market risk framework with SA and IMA approaches",
    },
    "basel3_cva": {
        "title": "Basel III - Credit Valuation Adjustment (CVA) Risk",
        "source": "BCBS",
        "description": "Capital requirements for CVA risk from OTC derivatives",
    },
    "basel3_output_floor": {
        "title": "Basel III - Output Floor",
        "source": "BCBS",
        "description": "Floor on RWA calculated using internal models (72.5% of standardised)",
    },
    "gdpr_full": {
        "title": "General Data Protection Regulation (GDPR)",
        "source": "European Union",
        "description": "EU data protection regulation - key articles relevant to financial institutions",
    },
    "sox_relevant": {
        "title": "Sarbanes-Oxley Act (SOX) - Relevant Sections",
        "source": "USA",
        "description": "Sections 302, 404, 802, 906 relevant to financial reporting and controls",
    },
    "bcb_resolucao_4557": {
        "title": "BCB Resolucao 4.557/2017 - Gerenciamento de Riscos",
        "source": "Banco Central do Brasil",
        "description": "Integrated risk management framework for financial institutions",
    },
    "cmn_resolucao_4966": {
        "title": "CMN Resolucao 4.966/2021 - Instrumentos Financeiros (IFRS 9)",
        "source": "Conselho Monetario Nacional",
        "description": "Brazilian adoption of IFRS 9 for financial instruments",
    },
    "bcbs_239": {
        "title": "BCBS 239 - Principles for Risk Data Aggregation and Reporting",
        "source": "BCBS",
        "description": "14 principles for effective risk data aggregation and risk reporting",
    },
    "bcbs_corporate_governance": {
        "title": "BCBS Corporate Governance Principles for Banks",
        "source": "BCBS",
        "description": "13 principles covering board responsibilities, risk management, and compliance",
    },
    "dodd_frank_title_vii": {
        "title": "Dodd-Frank Act - Title VII (Derivatives)",
        "source": "USA",
        "description": "Regulation of OTC derivatives markets including clearing and reporting",
    },
    "gdpr_recitals": {
        "title": "GDPR - Selected Recitals for Financial Services",
        "source": "European Union",
        "description": "Key GDPR recitals relevant to financial data processing",
    },
}


def generate_regulation_content(doc_id: str, doc_info: dict) -> str:
    """Generate Markdown content for a regulatory document.

    Creates structured content with proper H2/H3 headers for compatibility
    with the existing markdown parser in the ingestion pipeline.

    Args:
        doc_id: Document identifier.
        doc_info: Document metadata dict.

    Returns:
        Markdown content string.
    """
    title = doc_info["title"]
    source = doc_info["source"]
    description = doc_info["description"]

    # Generate content based on document type
    generators = {
        "basel3_leverage": _gen_basel3_leverage,
        "basel3_lcr": _gen_basel3_lcr,
        "basel3_nsfr": _gen_basel3_nsfr,
        "basel3_frtb": _gen_basel3_frtb,
        "basel3_cva": _gen_basel3_cva,
        "basel3_output_floor": _gen_basel3_output_floor,
        "gdpr_full": _gen_gdpr,
        "sox_relevant": _gen_sox,
        "bcb_resolucao_4557": _gen_bcb_4557,
        "cmn_resolucao_4966": _gen_cmn_4966,
        "bcbs_239": _gen_bcbs_239,
        "bcbs_corporate_governance": _gen_bcbs_governance,
        "dodd_frank_title_vii": _gen_dodd_frank,
        "gdpr_recitals": _gen_gdpr_recitals,
    }

    generator = generators.get(doc_id, _gen_placeholder)
    body = generator()

    return f"""# {title}

## Source
- **Issuing Body**: {source}
- **Document Type**: Regulatory Framework
- **Description**: {description}

{body}
"""


# ---------------------------------------------------------------------------
# Content generators for each regulation
# ---------------------------------------------------------------------------

def _gen_basel3_leverage():
    return """## Overview

The leverage ratio serves as a credible supplementary measure to the risk-based
capital requirements. It is intended to restrict the build-up of leverage in the
banking sector, helping avoid destabilising deleveraging processes which can
damage the broader financial system and the economy.

## Minimum Requirement

The minimum leverage ratio requirement is set at 3% of Tier 1 capital.

**Formula**: Leverage Ratio = Tier 1 Capital / Exposure Measure

## Exposure Measure

### On-Balance Sheet Exposures
- All balance sheet assets including derivatives collateral and SFT collateral
- Deductions applied to Tier 1 capital should also be deducted from exposure

### Derivative Exposures
- Replacement cost (RC) plus potential future exposure (PFE)
- SA-CCR approach for measuring counterparty credit risk

### Securities Financing Transactions (SFTs)
- Gross SFT assets with counterparty credit risk add-on
- Netting allowed only for transactions with the same counterparty

### Off-Balance Sheet Items
- Unconditionally cancellable commitments: 10% CCF
- Other off-balance sheet items: 100% CCF (with exceptions)

## G-SIB Buffer

Global systemically important banks (G-SIBs) must meet a leverage ratio
buffer requirement of 50% of their higher-loss absorbency requirements.

## Disclosure Requirements

Banks must disclose their leverage ratio on a quarterly basis using the
common disclosure template, reconciled with published financial statements.
"""


def _gen_basel3_lcr():
    return """## Overview

The Liquidity Coverage Ratio (LCR) aims to ensure that a bank maintains an
adequate level of unencumbered high-quality liquid assets (HQLA) that can be
converted into cash to meet its liquidity needs for a 30 calendar day
liquidity stress scenario.

## Minimum Requirement

LCR = Stock of HQLA / Total net cash outflows over next 30 days >= 100%

## High-Quality Liquid Assets (HQLA)

### Level 1 Assets (no haircut)
- Cash
- Central bank reserves
- Sovereign bonds rated AA- or above (0% risk weight)

### Level 2A Assets (15% haircut, max 40% of HQLA)
- Sovereign bonds rated A+ to BBB- (20% risk weight)
- Corporate bonds rated AA- or above
- Covered bonds rated AA- or above

### Level 2B Assets (25-50% haircut, max 15% of HQLA)
- Corporate bonds rated A+ to BBB- (50% haircut)
- Common equity shares in major indices (50% haircut)
- Residential mortgage-backed securities rated AA or above (25% haircut)

## Cash Outflows

### Retail Deposits
- Stable deposits (insured, transactional): 3% run-off rate
- Less stable retail deposits: 10% run-off rate

### Wholesale Funding
- Operational deposits: 25% run-off rate
- Non-operational deposits (financial institutions): 100% run-off rate
- Secured funding backed by Level 1 assets: 0% run-off rate

## Cash Inflows

- Contractual inflows from performing assets: capped at 75% of outflows
- Retail and wholesale inflows based on contractual terms
"""


def _gen_basel3_nsfr():
    return """## Overview

The Net Stable Funding Ratio (NSFR) requires banks to maintain a stable
funding profile in relation to their assets and off-balance sheet activities.
The NSFR limits over-reliance on short-term wholesale funding.

## Minimum Requirement

NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF) >= 100%

## Available Stable Funding (ASF)

### ASF Factor 100%
- Tier 1 and Tier 2 capital
- Other liabilities with maturity >= 1 year

### ASF Factor 95%
- Stable demand deposits and term deposits < 1 year (retail/SME)

### ASF Factor 90%
- Less stable demand deposits and term deposits < 1 year (retail/SME)

### ASF Factor 50%
- Operational deposits from non-financial corporates
- Funding with maturity 6-12 months from various sources

### ASF Factor 0%
- All other liabilities not included above
- Derivative payables

## Required Stable Funding (RSF)

### RSF Factor 0%
- Cash, central bank reserves
- Unencumbered Level 1 HQLA

### RSF Factor 5-15%
- Unencumbered Level 2 HQLA

### RSF Factor 50%
- Loans to financial institutions with maturity < 1 year
- Unencumbered listed equity securities

### RSF Factor 65-85%
- Residential mortgages with maturity >= 1 year (65% if risk weight <= 35%)
- Other loans with maturity >= 1 year (85%)

### RSF Factor 100%
- All assets encumbered for >= 1 year
- Non-performing loans
- All other assets
"""


def _gen_basel3_frtb():
    return """## Overview

The Fundamental Review of the Trading Book (FRTB) represents a comprehensive
revision of the market risk framework. It addresses shortcomings in the existing
framework revealed by the financial crisis.

## Key Changes

### Trading Book / Banking Book Boundary
- Stricter boundary definition based on trading intent
- Presumptive list of instruments in the trading book
- Internal risk transfers subject to regulatory approval

### Standardised Approach (SA)
- Sensitivities-based method (SbM) for most risk factors
- Default risk charge (DRC) for credit positions
- Residual risk add-on (RRAO) for exotic instruments

#### Risk Classes (SA)
1. General Interest Rate Risk (GIRR)
2. Credit Spread Risk (CSR) - non-securitisation
3. CSR - securitisation (non-CTP)
4. CSR - securitisation (CTP)
5. Equity Risk
6. Commodity Risk
7. Foreign Exchange (FX) Risk

### Internal Models Approach (IMA)
- Expected Shortfall (ES) replaces Value-at-Risk (VaR)
- ES at 97.5% confidence level
- Liquidity-adjusted time horizons (10 to 120 days)
- P&L attribution test and backtesting for desk-level approval

## Expected Shortfall Calculation

ES = ES(reduced set of risk factors) × ratio adjustment

Where the ratio adjustment accounts for the full set of risk factors
relative to the reduced set.

## Implementation Timeline

The revised framework was finalized in January 2019 with implementation
originally planned for January 2023, subsequently delayed to January 2025.
"""


def _gen_basel3_cva():
    return """## Overview

Credit Valuation Adjustment (CVA) risk is the risk of losses arising from
changes in the CVA of OTC derivatives due to movements in counterparty
credit spreads and other market risk factors.

## CVA Risk Capital Charge

### Standardised Approach (SA-CVA)
- Based on sensitivities to counterparty credit spreads and other risk factors
- Delta and vega risk charges for credit spread risk
- Aggregation across counterparties with correlation parameters

### Basic Approach (BA-CVA)
- Simplified version for banks with limited derivative portfolios
- Reduced sensitivity calculation requirements

## Scope

Applies to:
- All OTC derivatives (except with qualifying CCPs)
- Securities financing transactions that are fair-valued

## Exemptions

- Transactions with central counterparties (CCPs)
- Transactions with sovereigns, central banks, and multilateral development banks
- Banks below materiality threshold may use simple formula

## Hedging Recognition

### Eligible Hedges
- Single-name CDS and index CDS referencing counterparty credit spread
- Proxy hedges with basis risk adjustment

### Recognition in SA-CVA
- Hedges reduce CVA sensitivity to credit spreads
- Basis risk between hedge and CVA recognized through correlation parameters
"""


def _gen_basel3_output_floor():
    return """## Overview

The output floor ensures that banks' risk-weighted assets (RWAs) generated
by internal models cannot fall below a percentage of the RWAs calculated
using the standardised approaches.

## Floor Level

The output floor is set at 72.5% of standardised RWAs.

**RWA(floor) = max(RWA(models), 72.5% × RWA(standardised))**

## Transitional Arrangements

| Year | Floor Level |
|------|-------------|
| 2023 | 50% |
| 2024 | 55% |
| 2025 | 60% |
| 2026 | 65% |
| 2027 | 70% |
| 2028+ | 72.5% |

## Risk Categories Covered

The output floor applies to aggregate RWAs across all risk categories:
- Credit risk
- Counterparty credit risk (SA-CCR)
- CVA risk
- Market risk (FRTB)
- Operational risk (SMA)

## Impact on Internal Models

Banks using Internal Ratings-Based (IRB) approach for credit risk and
Internal Models Approach (IMA) for market risk will see capital requirements
floored to 72.5% of what the standardised approach would produce.

## Interaction with Other Requirements

The output floor is applied at the consolidated level and interacts with:
- Leverage ratio requirements
- G-SIB/D-SIB surcharges
- Capital conservation buffer
- Countercyclical buffer
"""


def _gen_gdpr():
    return """## Overview

The General Data Protection Regulation (GDPR, Regulation EU 2016/679) is the
European Union's comprehensive data protection regulation that governs the
processing of personal data of individuals in the EU.

## Key Principles (Article 5)

1. **Lawfulness, fairness and transparency** - Data must be processed lawfully
2. **Purpose limitation** - Collected for specified, explicit purposes
3. **Data minimisation** - Adequate, relevant and limited to what is necessary
4. **Accuracy** - Accurate and kept up to date
5. **Storage limitation** - Kept no longer than necessary
6. **Integrity and confidentiality** - Appropriate security measures
7. **Accountability** - Controller responsible for compliance

## Legal Bases for Processing (Article 6)

- Consent of the data subject
- Performance of a contract
- Legal obligation
- Vital interests
- Public interest or official authority
- Legitimate interests (except where overridden by data subject rights)

## Data Subject Rights

### Right of Access (Article 15)
Data subjects may obtain confirmation and access to their personal data.

### Right to Rectification (Article 16)
Right to have inaccurate personal data corrected.

### Right to Erasure (Article 17)
"Right to be forgotten" under specified circumstances.

### Right to Data Portability (Article 20)
Right to receive data in structured, machine-readable format.

### Right to Object (Article 21)
Right to object to processing based on legitimate interests or direct marketing.

## Data Protection Officer (Articles 37-39)

Financial institutions must designate a DPO when:
- Processing is carried out by a public authority
- Core activities involve large-scale monitoring
- Core activities involve large-scale processing of special categories

## Data Breach Notification (Articles 33-34)

- Notify supervisory authority within 72 hours
- Notify data subjects when high risk to rights and freedoms
- Maintain internal breach register

## International Transfers (Chapter V)

- Adequacy decisions
- Standard contractual clauses (SCCs)
- Binding corporate rules (BCRs)

## Penalties (Article 83)

- Up to EUR 10 million or 2% of global turnover (administrative violations)
- Up to EUR 20 million or 4% of global turnover (fundamental violations)
"""


def _gen_sox():
    return """## Overview

The Sarbanes-Oxley Act of 2002 (SOX) was enacted following corporate scandals
(Enron, WorldCom) to protect investors through improved accuracy and reliability
of corporate disclosures. Key sections relevant to financial institutions:

## Section 302: Corporate Responsibility for Financial Reports

### CEO/CFO Certifications
Officers must certify that:
- They have reviewed the report
- The report does not contain material misstatements
- Financial statements fairly present the financial condition
- They are responsible for internal controls
- They have disclosed any significant deficiencies to auditors

## Section 404: Management Assessment of Internal Controls

### 404(a): Management Assessment
- Annual report must include internal control assessment
- Statement of management responsibility for establishing controls
- Assessment of effectiveness at fiscal year-end
- Framework used for evaluation (e.g., COSO)

### 404(b): Auditor Attestation
- External auditor must attest to management's assessment
- Independent evaluation of internal control effectiveness
- Report on material weaknesses identified

## Section 802: Criminal Penalties for Altering Documents

- Up to 20 years imprisonment for document alteration/destruction
- Applies to records relevant to federal investigations
- Retention requirements for audit workpapers (7 years minimum)

## Section 906: Corporate Responsibility for Financial Reports

### Criminal Penalties
- Willful certification of non-compliant report: up to $5 million fine, 20 years
- Knowing certification of non-compliant report: up to $1 million fine, 10 years

## Relevance to Financial Institutions

SOX requirements interact with:
- Basel III Pillar 3 disclosure requirements
- SEC reporting requirements (10-K, 10-Q)
- PCAOB audit standards
- Internal audit function requirements
"""


def _gen_bcb_4557():
    return """## Overview

Resolucao 4.557 de 23 de fevereiro de 2017 do Banco Central do Brasil dispoe
sobre a estrutura de gerenciamento de riscos e a estrutura de gerenciamento
de capital das instituicoes financeiras.

## Estrutura de Gerenciamento de Riscos

### Artigo 2 - Riscos Cobertos
A estrutura deve contemplar:
1. Risco de credito
2. Risco de mercado
3. Risco de liquidez
4. Risco operacional
5. Demais riscos relevantes para a instituicao

### Artigo 3 - Componentes da Estrutura
A estrutura deve incluir:
- Politicas de gerenciamento de riscos
- Processos de identificacao, mensuracoa, avaliacao, monitoramento e reporte
- Limites operacionais
- Planos de contingencia

### Artigo 5 - Responsabilidades
- O conselho de administracao e responsavel pelas politicas
- A diretoria e responsavel pela implementacao
- O CRO (Chief Risk Officer) deve ter acesso direto ao conselho

## Estrutura de Gerenciamento de Capital

### Artigo 11 - ICAAP
O processo de avaliacao da adequacao de capital deve considerar:
- Risco de credito
- Risco de mercado
- Risco operacional
- Risco de taxa de juros na carteira banking
- Risco de concentracao
- Demais riscos materiais

### Artigo 13 - Estresse
Testes de estresse devem:
- Ser realizados periodicamente
- Contemplar cenarios adversos e severos
- Considerar impacto na adequacao de capital

## Governanca

### Artigo 7 - Comite de Riscos
- Composicao: membros do conselho e diretoria
- Reunioes periodicas (no minimo trimestrais)
- Atribuicoes: aprovar politicas, revisar limites, avaliar adequacao

### Artigo 9 - Documentacao
Manter registros de:
- Politicas e procedimentos
- Relatorios de riscos
- Atas de reunioes dos comites
- Resultados de testes de estresse
"""


def _gen_cmn_4966():
    return """## Overview

Resolucao CMN 4.966 de 25 de novembro de 2021 dispoe sobre os conceitos e
criterios contabeis aplicaveis a instrumentos financeiros e demais operacoes
no ambito do Sistema Financeiro Nacional, alinhando-se ao IFRS 9.

## Classificacao e Mensuracao

### Categorias de Classificacao
1. **Custo amortizado** - Modelo de negocios de manter para receber fluxos contratuais
2. **Valor justo por meio de ORA** - Modelo de manter e vender
3. **Valor justo por meio do resultado** - Residual ou designacao irrevogavel

### Teste SPPI (Solely Payments of Principal and Interest)
Fluxos de caixa contratuais devem consistir exclusivamente em:
- Pagamentos de principal
- Pagamentos de juros sobre o principal em aberto

## Perda Esperada de Credito (ECL)

### Modelo de 3 Estagios

**Estagio 1**: Ativos sem aumento significativo de risco de credito desde o reconhecimento
- Provisao: ECL de 12 meses
- Receita de juros: sobre o valor contabil bruto

**Estagio 2**: Aumento significativo de risco de credito
- Provisao: ECL ao longo da vida (lifetime ECL)
- Receita de juros: sobre o valor contabil bruto

**Estagio 3**: Ativos com credito deteriorado (impaired)
- Provisao: ECL ao longo da vida (lifetime ECL)
- Receita de juros: sobre o valor contabil liquido

### Criterios de Aumento Significativo de Risco
- Mudanca na probabilidade de default (PD)
- Dias de atraso (presuncao refutavel: > 30 dias)
- Informacoes qualitativas (lista de atencao, reestruturacao)

## Hedge Accounting

### Tipos de Hedge
1. Hedge de valor justo
2. Hedge de fluxo de caixa
3. Hedge de investimento liquido em operacao no exterior

### Requisitos de Efetividade
- Relacao economica entre o item protegido e o instrumento de hedge
- Efeito do risco de credito nao domina as mudancas de valor
- Razao de hedge reflete a quantidade efetivamente usada para gestao de risco

## Cronograma de Implementacao

Entrada em vigor: 1 de janeiro de 2025
"""


def _gen_bcbs_239():
    return """## Overview

BCBS 239 "Principles for effective risk data aggregation and risk reporting"
was published in January 2013. It establishes 14 principles to strengthen
banks' risk data aggregation capabilities and internal risk reporting practices.

## Principles

### Overarching Governance and Infrastructure

**Principle 1: Governance**
A bank's risk data aggregation capabilities and risk reporting practices should
be subject to strong governance arrangements consistent with other principles.

**Principle 2: Data Architecture and IT Infrastructure**
A bank should design, build, and maintain data architecture and IT infrastructure
that fully supports its risk data aggregation capabilities and risk reporting
practices, under normal and stress conditions.

### Risk Data Aggregation Capabilities

**Principle 3: Accuracy and Integrity**
A bank should be able to generate accurate and reliable risk data to meet normal
and stress reporting accuracy requirements.

**Principle 4: Completeness**
A bank should be able to capture and aggregate all material risk data across
the banking group. Data should be available by business line, legal entity,
asset type, industry, region, and other groupings.

**Principle 5: Timeliness**
A bank should be able to generate aggregate and up-to-date risk data in a
timely manner while also meeting the principles relating to accuracy and
integrity, completeness, and adaptability.

**Principle 6: Adaptability**
A bank should be able to generate aggregate risk data to meet a broad range of
on-demand, ad hoc risk management reporting requests, including requests during
stress/crisis situations, requests due to changing internal needs, and requests
to meet supervisory queries.

### Risk Reporting Practices

**Principle 7: Accuracy**
Risk management reports should accurately and precisely convey aggregated risk
data and reflect risk in an exact manner.

**Principle 8: Comprehensiveness**
Risk management reports should cover all material risk areas within the
organisation and should be consistent with the scope of risk data aggregation.

**Principle 9: Clarity and Usefulness**
Risk management reports should communicate information in a clear and concise
manner. Reports should be easy to understand yet comprehensive.

**Principle 10: Frequency**
The board and senior management should set the frequency of risk management
report production and distribution. Frequency should be increased during
stress/crisis periods.

**Principle 11: Distribution**
Risk management reports should be distributed to relevant parties while
ensuring confidentiality is maintained.

### Supervisory Review, Tools and Cooperation

**Principle 12: Review**
Supervisors should periodically review and evaluate a bank's compliance
with the Principles.

**Principle 13: Remedial Actions and Supervisory Measures**
Supervisors should have tools to require effective remedial action.

**Principle 14: Home/Host Cooperation**
Supervisors should cooperate with relevant supervisors in other jurisdictions.

## Compliance Expectations

G-SIBs were expected to comply by January 2016. D-SIBs should comply
within three years of their designation.
"""


def _gen_bcbs_governance():
    return """## Overview

The BCBS Corporate Governance Principles for Banks (revised July 2015)
provide a framework of 13 principles for sound corporate governance
in banking organisations.

## Principles

### Board Responsibilities

**Principle 1: Board's Overall Responsibilities**
The board has overall responsibility for the bank, including approving
and overseeing the implementation of the bank's strategic objectives,
governance framework and corporate culture.

**Principle 2: Board Qualifications and Composition**
Board members should be and remain qualified for their positions. The
board should have an adequate combination of knowledge, skills, and
experience.

**Principle 3: Board's Own Structure and Practices**
The board should define appropriate governance structures and practices
and periodically review their effectiveness.

### Senior Management

**Principle 4: Senior Management**
Under the direction of the board, senior management should carry out and
manage the bank's activities in a manner consistent with the strategy,
risk appetite and policies approved by the board.

### Risk Management and Internal Controls

**Principle 5: Governance of Group Structures**
The board should actively oversee the design and operation of the bank's
governance framework in a manner that is appropriate for the structure,
business and risks of the bank and its subsidiaries.

**Principle 6: Risk Management Function**
Banks should have an effective independent risk management function, under
the direction of a CRO, with sufficient authority, stature, independence,
resources and access to the board.

**Principle 7: Risk Identification, Monitoring and Controlling**
Risks should be identified, monitored and controlled on an ongoing
bank-wide and individual entity basis.

**Principle 8: Risk Communication**
An effective risk governance framework requires robust communication
about risk across the organisation and through reporting to the board
and senior management.

**Principle 9: Compliance**
The bank's board should establish a compliance function and approve
policies and processes for identifying and managing compliance risk.

**Principle 10: Internal Audit**
The internal audit function should provide independent assurance to the
board and support board and senior management in the efficient and
effective discharge of their responsibilities.

### Compensation

**Principle 11: Compensation**
The bank's compensation structure should support sound corporate governance
and risk management.

### Disclosure and Transparency

**Principle 12: Disclosure and Transparency**
The governance of the bank should be adequately transparent to its
shareholders, depositors, other relevant stakeholders and market participants.

### Role of Supervisors

**Principle 13: Role of Supervisors**
Supervisors should provide guidance for and supervise corporate governance
at banks, including through comprehensive evaluations and regular interaction.
"""


def _gen_dodd_frank():
    return """## Overview

The Dodd-Frank Wall Street Reform and Consumer Protection Act (2010) Title VII
regulates the OTC derivatives market. Key provisions relevant to financial
institutions:

## Clearing Requirements

### Mandatory Clearing (Section 723)
- Standardised swaps must be cleared through registered clearinghouses (DCOs)
- Applies to interest rate swaps, credit default swaps, and other designated products
- End-user exception for commercial hedging

### Clearing Organisation Requirements (Section 725)
- Registration with CFTC or SEC
- Risk management standards
- Default fund requirements
- Position limits and large trader reporting

## Trade Execution

### Swap Execution Facilities (SEFs) (Section 733)
- Swaps subject to clearing must be traded on SEFs or exchanges
- Multiple participant execution required
- Pre-trade and post-trade transparency

## Reporting Requirements

### Trade Reporting (Section 727-729)
- All swaps (cleared and uncleared) must be reported to swap data repositories (SDRs)
- Real-time public reporting of swap transaction data
- Position data reporting to regulators

## Margin Requirements

### Uncleared Swap Margin (Section 731)
- Initial margin and variation margin requirements
- Margin calculation methodology (standardised or approved models)
- Eligible collateral types
- Segregation requirements

## Registration and Business Conduct

### Swap Dealer Registration (Section 731)
- Capital requirements for swap dealers
- Business conduct standards
- Documentation requirements
- Chief Compliance Officer requirement

### Major Swap Participant (Section 731)
- Registration for entities with substantial swap positions
- Similar requirements to swap dealers

## Volcker Rule (Section 619)

While in Title VI, the Volcker Rule significantly impacts derivatives:
- Prohibits proprietary trading by banking entities
- Restricts ownership in hedge funds and private equity funds
- Exemptions for market-making, hedging, and government securities
"""


def _gen_gdpr_recitals():
    return """## Overview

Selected GDPR recitals most relevant to financial services data processing.
These provide interpretive guidance on the regulation's articles.

## Recital 47 - Legitimate Interests

Processing for direct marketing purposes may be regarded as carried out for
a legitimate interest. For financial institutions, this includes:
- Fraud prevention
- Network and information security
- Intra-group data transfers for internal administrative purposes

## Recital 49 - Network Security

Processing of personal data to the extent strictly necessary for ensuring
network and information security constitutes a legitimate interest.
Relevant to cybersecurity measures required under BCB Resolucao 4.893.

## Recital 71 - Automated Decision-Making

The data subject should have the right not to be subject to a decision based
solely on automated processing. For financial institutions:
- Credit scoring algorithms must allow human intervention
- Automated loan decisions must be explainable
- Profiling for AML/KYC purposes may require specific legal basis

## Recital 75 - Risk Assessment

Financial data processing may present risks to the rights and freedoms of
individuals. Risk factors include:
- Large-scale processing of financial data
- Systematic monitoring (transaction monitoring for AML)
- Processing of data revealing financial situation

## Recital 91 - Data Protection Impact Assessment

A DPIA is required when processing is likely to result in high risk.
For financial institutions, this applies to:
- New customer onboarding systems with automated profiling
- Transaction monitoring systems
- Cross-border data transfers to non-adequate jurisdictions

## Recital 108 - Adequate Level of Protection (Transfers)

The Commission may decide that a third country offers an adequate level
of data protection. Relevant to financial institutions with:
- Global operations requiring data transfers
- Cloud service providers in non-EU jurisdictions
- Outsourcing arrangements with third-country processors
"""


def _gen_placeholder():
    return """## Content

[Content to be generated from official regulatory sources]

## References

- Official publication available from the issuing regulatory body
- Cross-references to related regulations will be added during ingestion
"""


def main():
    """Entry point for regulation preparation script."""
    parser = argparse.ArgumentParser(
        description="Prepare additional regulatory documents for GraphRAG corpus",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Output directory for regulation files",
    )
    parser.add_argument(
        "--docs",
        nargs="+",
        type=str,
        default=None,
        help="Specific documents to generate (default: all 14)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without generating files",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if not args.output_dir:
        base = Path(__file__).resolve().parent.parent.parent
        args.output_dir = str(base / "implementacao" / "data" / "regulations")

    # Filter docs if specific ones requested
    docs = REGULATION_DOCS
    if args.docs:
        docs = {k: v for k, v in REGULATION_DOCS.items() if k in args.docs}

    if args.dry_run:
        print(f"\n{'='*70}")
        print(f"  Regulatory Document Generation Plan ({len(docs)} documents)")
        print(f"{'='*70}")
        for doc_id, info in docs.items():
            print(f"  {doc_id:30s} [{info['source']:15s}] {info['title']}")
        print(f"\n  Output: {args.output_dir}")
        return

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    generated = []
    for doc_id, info in docs.items():
        content = generate_regulation_content(doc_id, info)
        filepath = os.path.join(args.output_dir, f"{doc_id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        generated.append(filepath)
        logger.info("Generated: %s (%s)", doc_id, info["title"])

    print(f"\nGenerated {len(generated)} regulatory documents in {args.output_dir}")


if __name__ == "__main__":
    main()
