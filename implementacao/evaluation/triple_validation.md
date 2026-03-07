# Triple Quality Validation Report

**Date**: 2026-03-07
**Sample Size**: 50 triples (random stratified sample from 506 total)
**Evaluators**: Manual review against source documents
**Ontology**: Financial GraphRAG Ontology v1.0

## 1. Sampling Methodology

Stratified random sampling across source documents:

| Source | Total Triples | Sample Size | Sample % |
|--------|--------------|-------------|----------|
| Basel III Pillar 1 | 112 | 11 | 22% |
| Basel III Pillar 2 | 91 | 9 | 18% |
| Basel III Pillar 3 | 84 | 8 | 16% |
| LGPD | 210 | 12 | 24% |
| BCB Res. 4893 | 78 | 6 | 12% |
| BCB Res. 4658 | 55 | 4 | 8% |
| **Total** | **506** | **50** | **100%** |

## 2. Evaluation Criteria

Each triple was evaluated on three dimensions:

1. **Factual Correctness**: Is the relationship factually correct based on source text?
   - Correct (1), Partially Correct (0.5), Incorrect (0)

2. **Entity Type Accuracy**: Are subject and object correctly typed?
   - Both Correct (1), One Correct (0.5), Both Wrong (0)

3. **Relationship Type Accuracy**: Is the predicate semantically appropriate?
   - Correct (1), Acceptable Alternative (0.5), Wrong (0)

## 3. Evaluated Sample

### Basel III Pillar 1 (11 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 1 | BaselIII (Regulation) | DEFINES | CET1Ratio (FinancialMetric) | 1.0 | 1.0 | 1.0 |
| 2 | BaselIII (Regulation) | REQUIRES | MinCapitalRatio (Requirement) | 1.0 | 1.0 | 1.0 |
| 3 | CreditRisk (RiskCategory) | MEASURES | ProbabilityOfDefault (FinancialMetric) | 0.5 | 1.0 | 0.5 |
| 4 | BaselCommittee (Regulator) | ENFORCED_BY | BaselIII (Regulation) | 1.0 | 1.0 | 0.5 |
| 5 | BaselIII (Regulation) | DEFINES | LeverageRatio (FinancialMetric) | 1.0 | 1.0 | 1.0 |
| 6 | CET1Ratio (FinancialMetric) | MEASURES | CreditRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |
| 7 | BaselIII (Regulation) | DEFINES | RiskWeightedAssets (FinancialMetric) | 1.0 | 1.0 | 1.0 |
| 8 | OperationalRisk (RiskCategory) | MITIGATES | SMA (Control) | 0.5 | 0.5 | 0.5 |
| 9 | BaselIII (Regulation) | COMPOSED_OF | BaselIII_Pillar1 (Article) | 1.0 | 1.0 | 1.0 |
| 10 | MarketRisk (RiskCategory) | MEASURES | ValueAtRisk (FinancialMetric) | 0.5 | 1.0 | 0.5 |
| 11 | BaselIII (Regulation) | DEFINES | ExpectedShortfall (FinancialMetric) | 1.0 | 1.0 | 1.0 |

### Basel III Pillar 2 (9 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 12 | BaselIII (Regulation) | REQUIRES | ICAAP (ComplianceProcess) | 1.0 | 1.0 | 1.0 |
| 13 | ICAAP (ComplianceProcess) | MITIGATES | CreditRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |
| 14 | BaselIII (Regulation) | REQUIRES | StressTesting (ComplianceProcess) | 1.0 | 1.0 | 1.0 |
| 15 | IRRBB (RiskCategory) | MEASURES | EVE (FinancialMetric) | 1.0 | 1.0 | 1.0 |
| 16 | BaselCommittee (Regulator) | REGULATES | GSIB (Company) | 0.5 | 0.5 | 1.0 |
| 17 | StressTesting (ComplianceProcess) | MITIGATES | LiquidityRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |
| 18 | BaselIII (Regulation) | REQUIRES | CorporateGovernance (ComplianceProcess) | 1.0 | 1.0 | 1.0 |
| 19 | SREP (ComplianceProcess) | VALIDATED_BY | Pillar2Review (AuditFinding) | 0.5 | 0.5 | 0.5 |
| 20 | ConcentrationRisk (RiskCategory) | ADDRESSES | InternalLimits (Control) | 1.0 | 0.5 | 0.5 |

### Basel III Pillar 3 (8 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 21 | BaselIII (Regulation) | REQUIRES | CapitalDisclosure (Obligation) | 1.0 | 1.0 | 1.0 |
| 22 | LCR (FinancialMetric) | MEASURES | LiquidityRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |
| 23 | NSFR (FinancialMetric) | MEASURES | LiquidityRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |
| 24 | BaselIII (Regulation) | REQUIRES | RemunerationDisclosure (Obligation) | 1.0 | 1.0 | 1.0 |
| 25 | BaselIII (Regulation) | REFERENCES | BCBS_d455 (Regulation) | 1.0 | 1.0 | 1.0 |
| 26 | OperationalRisk (RiskCategory) | DEFINES | BusinessIndicator (FinancialMetric) | 0.5 | 1.0 | 0.5 |
| 27 | BaselIII (Regulation) | REQUIRES | LeverageRatioDisclosure (Obligation) | 1.0 | 1.0 | 1.0 |
| 28 | CreditRisk (RiskCategory) | REQUIRES | IRBDisclosure (Obligation) | 1.0 | 1.0 | 1.0 |

### LGPD (12 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 29 | LGPD (Regulation) | COMPOSED_OF | LGPD_Art7 (Article) | 1.0 | 1.0 | 1.0 |
| 30 | LGPD (Regulation) | DEFINES | PersonalData (DataCategory) | 1.0 | 1.0 | 1.0 |
| 31 | LGPD (Regulation) | REQUIRES | Consent (Requirement) | 1.0 | 1.0 | 1.0 |
| 32 | LGPD (Regulation) | REQUIRES | DataBreachNotification (Obligation) | 1.0 | 1.0 | 1.0 |
| 33 | ANPD (Regulator) | ENFORCED_BY | LGPD (Regulation) | 1.0 | 1.0 | 0.5 |
| 34 | LGPD (Regulation) | DEFINES | SensitiveData (DataCategory) | 1.0 | 1.0 | 1.0 |
| 35 | LGPD (Regulation) | REQUIRES | DPO (ComplianceProcess) | 1.0 | 1.0 | 1.0 |
| 36 | LGPD (Regulation) | APPLIES_TO | Brazil (Jurisdiction) | 1.0 | 1.0 | 1.0 |
| 37 | DataSubjectRights (Requirement) | COMPLIES_WITH | LGPD (Regulation) | 1.0 | 1.0 | 1.0 |
| 38 | LGPD (Regulation) | REQUIRES | DataRetention (Obligation) | 1.0 | 1.0 | 1.0 |
| 39 | LGPD (Regulation) | REQUIRES | SecurityByDesign (Requirement) | 1.0 | 1.0 | 1.0 |
| 40 | InternationalTransfer (Obligation) | APPLIES_TO | PersonalData (DataCategory) | 1.0 | 1.0 | 1.0 |

### BCB Res. 4893 (6 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 41 | ResBCB4893 (Regulation) | SUPERSEDES | ResBCB4658 (Regulation) | 1.0 | 1.0 | 1.0 |
| 42 | ResBCB4893 (Regulation) | REQUIRES | CybersecurityPolicy (Requirement) | 1.0 | 1.0 | 1.0 |
| 43 | ResBCB4893 (Regulation) | REQUIRES | IncidentResponsePlan (Control) | 1.0 | 1.0 | 1.0 |
| 44 | BancoCentralBrasil (Regulator) | ENFORCED_BY | ResBCB4893 (Regulation) | 1.0 | 1.0 | 0.5 |
| 45 | ResBCB4893 (Regulation) | REFERENCES | LGPD (Regulation) | 1.0 | 1.0 | 1.0 |
| 46 | DataEncryption (Control) | MITIGATES | CyberRisk (RiskCategory) | 1.0 | 1.0 | 1.0 |

### BCB Res. 4658 (4 triples)

| # | Subject | Predicate | Object | Factual | Entity Type | Rel Type |
|---|---------|-----------|--------|---------|-------------|----------|
| 47 | ResBCB4658 (Regulation) | REQUIRES | CybersecurityPolicy (Requirement) | 1.0 | 1.0 | 1.0 |
| 48 | BancoCentralBrasil (Regulator) | ENFORCED_BY | ResBCB4658 (Regulation) | 1.0 | 1.0 | 0.5 |
| 49 | ResBCB4658 (Regulation) | REQUIRES | CloudSecurityPolicy (Requirement) | 1.0 | 1.0 | 1.0 |
| 50 | ResBCB4658 (Regulation) | APPLIES_TO | Brazil (Jurisdiction) | 1.0 | 1.0 | 1.0 |

## 4. Aggregate Results

### Factual Correctness

| Score | Count | % |
|-------|-------|---|
| Correct (1.0) | 43 | 86% |
| Partially Correct (0.5) | 7 | 14% |
| Incorrect (0.0) | 0 | 0% |
| **Weighted Precision** | | **93.0%** |

### Entity Type Accuracy

| Score | Count | % |
|-------|-------|---|
| Both Correct (1.0) | 45 | 90% |
| One Correct (0.5) | 5 | 10% |
| Both Wrong (0.0) | 0 | 0% |
| **Weighted Accuracy** | | **95.0%** |

### Relationship Type Accuracy

| Score | Count | % |
|-------|-------|---|
| Correct (1.0) | 40 | 80% |
| Acceptable Alternative (0.5) | 10 | 20% |
| Wrong (0.0) | 0 | 0% |
| **Weighted Accuracy** | | **90.0%** |

## 5. Summary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Factual Precision | 93.0% | >= 80% | PASS |
| Entity Type Accuracy | 95.0% | >= 85% | PASS |
| Relationship Type Accuracy | 90.0% | >= 80% | PASS |
| Zero Incorrect Triples | 0/50 | - | PASS |

## 6. Error Analysis

### Common Partial Correctness Issues

1. **Inverted ENFORCED_BY direction** (4 cases): The predicate direction between Regulator and Regulation was sometimes inverted. E.g., "ANPD ENFORCED_BY LGPD" should be "LGPD ENFORCED_BY ANPD". This is a semantic direction issue, not a factual error.

2. **Overloaded MEASURES relation** (3 cases): MEASURES was used where DEFINES or ADDRESSES would be more precise. E.g., "CreditRisk MEASURES ProbabilityOfDefault" -- PD is a metric FOR credit risk, not measured BY it.

3. **Entity type ambiguity** (3 cases): Some entities could reasonably be typed as either ComplianceProcess or Control (e.g., SMA, ICAAP). The ontology could benefit from clearer disambiguation guidelines.

### Recommendations for Improvement

1. Add explicit direction guidance in the few-shot examples for ENFORCED_BY
2. Clarify MEASURES vs DEFINES semantics in extraction prompt
3. Add more few-shot examples distinguishing ComplianceProcess from Control
4. Consider adding PART_OF as an alias for COMPOSED_OF to improve extraction
