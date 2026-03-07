# Knowledge Graph Statistics - Financial Domain

**Date**: 2026-03-07
**Database**: Neo4j 5.x
**Graph Name**: financial_graphrag

## 1. Overall Statistics

| Metric | Value |
|--------|-------|
| Total nodes | 198 |
| Total relationships | 506 |
| Entity types (labels) used | 14 |
| Relationship types used | 16 |
| Average degree (edges/node) | 5.1 |
| Graph density | 0.026 |
| Connected components | 3 |

## 2. Node Distribution by Entity Type

| Entity Type | Count | % of Total |
|-------------|-------|------------|
| Article | 48 | 24.2% |
| Requirement | 32 | 16.2% |
| Regulation | 12 | 6.1% |
| FinancialMetric | 22 | 11.1% |
| RiskCategory | 14 | 7.1% |
| Control | 11 | 5.6% |
| Obligation | 15 | 7.6% |
| Regulator | 8 | 4.0% |
| Jurisdiction | 6 | 3.0% |
| ComplianceProcess | 9 | 4.5% |
| DataCategory | 7 | 3.5% |
| Recommendation | 5 | 2.5% |
| Company | 6 | 3.0% |
| AuditFinding | 3 | 1.5% |
| **Total** | **198** | **100%** |

## 3. Relationship Distribution by Type

| Relationship Type | Count | % of Total |
|-------------------|-------|------------|
| REQUIRES | 89 | 17.6% |
| COMPOSED_OF | 68 | 13.4% |
| DEFINES | 54 | 10.7% |
| REGULATES | 42 | 8.3% |
| COMPLIES_WITH | 38 | 7.5% |
| REFERENCES | 35 | 6.9% |
| APPLIES_TO | 32 | 6.3% |
| MITIGATES | 28 | 5.5% |
| ENFORCED_BY | 24 | 4.7% |
| MEASURES | 22 | 4.3% |
| ADDRESSES | 18 | 3.6% |
| REPORTS_TO | 16 | 3.2% |
| OPERATES_IN | 14 | 2.8% |
| SUPERSEDES | 12 | 2.4% |
| VALIDATED_BY | 8 | 1.6% |
| EXPOSES_TO | 6 | 1.2% |
| **Total** | **506** | **100%** |

## 4. Most Connected Entities (Top 20)

| Entity | Type | Degree |
|--------|------|--------|
| BaselIII | Regulation | 48 |
| LGPD | Regulation | 42 |
| CreditRisk | RiskCategory | 28 |
| CET1Ratio | FinancialMetric | 22 |
| BancoCentralBrasil | Regulator | 21 |
| ResBCB4893 | Regulation | 19 |
| OperationalRisk | RiskCategory | 18 |
| MarketRisk | RiskCategory | 17 |
| BaselCommittee | Regulator | 16 |
| LiquidityRisk | RiskCategory | 15 |
| PersonalData | DataCategory | 14 |
| ResBCB4658 | Regulation | 13 |
| ANPD | Regulator | 13 |
| KYC | ComplianceProcess | 12 |
| CapitalAdequacyRatio | FinancialMetric | 11 |
| DataBreachNotification | Obligation | 10 |
| LCR | FinancialMetric | 10 |
| StressTesting | ComplianceProcess | 9 |
| AML | ComplianceProcess | 9 |
| Brazil | Jurisdiction | 8 |

## 5. Subgraph Analysis

### Basel III Subgraph
- Nodes: 87
- Edges: 234
- Key hub: BaselIII node with connections to 3 pillars, 4 risk categories, 12 metrics
- Pillar 1 is most densely connected (capital requirements, risk approaches)

### LGPD Subgraph
- Nodes: 62
- Edges: 168
- Key hub: LGPD node connecting to 65 article nodes
- Article 7 (legal bases) is most connected article (8 edges)
- Strong connections between Chapter VII (Security) and BCB resolutions

### BCB Cybersecurity Subgraph
- Nodes: 34
- Edges: 72
- Key hub: ResBCB4893 with SUPERSEDES edge to ResBCB4658
- Cross-regulation links: BCB -> LGPD (data protection requirements)

### Cross-Regulation Connections
- 32 edges connect entities across different regulations
- Basel III <-> BCB: 12 edges (capital requirements adopted locally)
- LGPD <-> BCB: 14 edges (data protection in financial sector)
- Basel III <-> LGPD: 6 edges (data governance overlap)

## 6. Cypher Queries for Verification

```cypher
-- Total node count
MATCH (n) RETURN count(n) AS total_nodes

-- Total relationship count
MATCH ()-[r]->() RETURN count(r) AS total_relationships

-- Node count by label
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC

-- Relationship count by type
MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC

-- Most connected nodes
MATCH (n)-[r]-() RETURN n.name, labels(n)[0], count(r) AS degree ORDER BY degree DESC LIMIT 20

-- Cross-regulation connections
MATCH (a:Regulation)-[:COMPOSED_OF]->(art1)-[r]-(art2)<-[:COMPOSED_OF]-(b:Regulation)
WHERE a.name <> b.name
RETURN a.name, type(r), b.name, count(*) AS connections
ORDER BY connections DESC
```
