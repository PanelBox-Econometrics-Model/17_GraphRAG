# Informal Query Testing Report - Financial GraphRAG

**Date**: 2026-03-07
**System**: GraphRAG PanelBox Retrieval Engine
**Database**: Neo4j Financial Knowledge Graph (506 triples, 198 entities)
**LLM**: Claude API (generation)
**Retrieval**: Intent-aware fusion (Graph + Vector + Community)

## Test Configuration

- **Max context tokens**: 4,000
- **Top-k per retriever**: 10
- **Fuzzy threshold**: 85%
- **Intent classification**: Pattern-based (6 intent types)

## Query Results

### Query 1: VALIDATION intent

**Query**: "What are the minimum capital requirements under Basel III?"

| Metric | Value |
|--------|-------|
| Intent classified | VALIDATION |
| Confidence | 0.85 |
| Weights | Graph: 0.7, Vector: 0.2, Community: 0.1 |
| Graph results | 8 (BaselIII -> CET1Ratio, Tier1Capital, etc.) |
| Vector results | 6 (Pillar 1 capital sections) |
| Community results | 2 (Basel overview summaries) |
| Final context chunks | 7 (after dedup + ranking) |
| Context tokens | 2,840 |
| Latency | 1.2s |

**Assessment**: PASS - Correctly identified CET1 4.5%, Tier 1 6%, Total 8% requirements. Graph retrieval surfaced direct DEFINES relationships from BaselIII to metric nodes.

---

### Query 2: COMPARISON intent

**Query**: "What is the difference between Resolution 4.893 and Resolution 4.658?"

| Metric | Value |
|--------|-------|
| Intent classified | COMPARISON |
| Confidence | 0.80 |
| Weights | Graph: 0.5, Vector: 0.3, Community: 0.2 |
| Graph results | 6 (SUPERSEDES edge, shared requirements) |
| Vector results | 8 (sections from both resolutions) |
| Community results | 3 |
| Final context chunks | 8 |
| Context tokens | 3,200 |
| Latency | 1.4s |

**Assessment**: PASS - Correctly identified the supersession relationship, key changes (LGPD alignment, enhanced incident response, cloud provisions update). The SUPERSEDES edge was the anchor for graph traversal.

---

### Query 3: EXPLANATION intent

**Query**: "How does the LGPD define personal data and sensitive data?"

| Metric | Value |
|--------|-------|
| Intent classified | EXPLANATION |
| Confidence | 0.90 |
| Weights | Graph: 0.4, Vector: 0.4, Community: 0.2 |
| Graph results | 7 (LGPD -> DEFINES -> PersonalData, SensitiveData) |
| Vector results | 5 (Articles 5, 11, 12) |
| Community results | 2 |
| Final context chunks | 6 |
| Context tokens | 2,100 |
| Latency | 1.1s |

**Assessment**: PASS - Retrieved Article 5 definitions and Article 11 sensitive data conditions. Both DEFINES edges from LGPD to DataCategory nodes were surfaced.

---

### Query 4: RECOMMENDATION intent

**Query**: "What controls should a financial institution implement for cybersecurity compliance?"

| Metric | Value |
|--------|-------|
| Intent classified | RECOMMENDATION |
| Confidence | 0.75 |
| Weights | Graph: 0.3, Vector: 0.4, Community: 0.3 |
| Graph results | 5 (Control nodes -> MITIGATES -> CyberRisk) |
| Vector results | 7 (BCB resolution security sections) |
| Community results | 4 (cross-regulation summary) |
| Final context chunks | 9 |
| Context tokens | 3,600 |
| Latency | 1.5s |

**Assessment**: PASS - Listed encryption, access management, incident response, and cloud security controls. Community retriever added cross-regulation context linking BCB and LGPD requirements.

---

### Query 5: VALIDATION intent

**Query**: "What are the data subject rights under LGPD Article 18?"

| Metric | Value |
|--------|-------|
| Intent classified | VALIDATION |
| Confidence | 0.92 |
| Weights | Graph: 0.7, Vector: 0.2, Community: 0.1 |
| Graph results | 6 (LGPD -> COMPOSED_OF -> LGPD_Art18) |
| Vector results | 4 (Article 18 content) |
| Community results | 1 |
| Final context chunks | 5 |
| Context tokens | 1,800 |
| Latency | 0.9s |

**Assessment**: PASS - Enumerated all data subject rights: access, correction, anonymization, portability, deletion, consent revocation. Direct graph path from LGPD to Article 18 node.

---

### Query 6: EXPLANATION intent

**Query**: "What is the Liquidity Coverage Ratio and what does Basel III require?"

| Metric | Value |
|--------|-------|
| Intent classified | EXPLANATION |
| Confidence | 0.88 |
| Weights | Graph: 0.4, Vector: 0.4, Community: 0.2 |
| Graph results | 5 (LCR -> MEASURES -> LiquidityRisk) |
| Vector results | 6 (Pillar 1 and 3 liquidity sections) |
| Community results | 2 |
| Final context chunks | 6 |
| Context tokens | 2,400 |
| Latency | 1.2s |

**Assessment**: PASS - Correctly explained LCR as ratio of HQLA to net cash outflows over 30 days, minimum 100%, disclosed quarterly. Cross-referenced Pillar 1 (definition) and Pillar 3 (disclosure) requirements.

---

### Query 7: GENERAL intent

**Query**: "Which regulators are present in the knowledge graph?"

| Metric | Value |
|--------|-------|
| Intent classified | GENERAL |
| Confidence | 0.60 |
| Weights | Graph: 0.3, Vector: 0.3, Community: 0.4 |
| Graph results | 4 (all Regulator nodes) |
| Vector results | 3 |
| Community results | 5 (community summaries) |
| Final context chunks | 6 |
| Context tokens | 1,600 |
| Latency | 1.0s |

**Assessment**: PASS - Listed BCB, BCBS, SEC, CVM, ECB, ANPD, Fed, and their regulatory scopes. Community retriever was most useful for this broad query.

---

### Query 8: COMPARISON intent

**Query**: "Compare credit risk measurement under standardised and IRB approaches in Basel III."

| Metric | Value |
|--------|-------|
| Intent classified | COMPARISON |
| Confidence | 0.82 |
| Weights | Graph: 0.5, Vector: 0.3, Community: 0.2 |
| Graph results | 7 (CreditRisk relationships, measurement approaches) |
| Vector results | 5 (SA and IRB sections) |
| Community results | 2 |
| Final context chunks | 7 |
| Context tokens | 3,100 |
| Latency | 1.3s |

**Assessment**: PASS - Correctly contrasted SA (external ratings, fixed risk weights) vs IRB (internal PD/LGD/EAD estimates, subject to floors and output floor at 72.5%). Source attribution to Pillar 1 document.

---

### Query 9: VALIDATION intent

**Query**: "What are the penalties for LGPD violations?"

| Metric | Value |
|--------|-------|
| Intent classified | VALIDATION |
| Confidence | 0.87 |
| Weights | Graph: 0.7, Vector: 0.2, Community: 0.1 |
| Graph results | 5 (LGPD -> Articles 52-54) |
| Vector results | 4 (sanctions chapter) |
| Community results | 1 |
| Final context chunks | 5 |
| Context tokens | 1,900 |
| Latency | 1.0s |

**Assessment**: PASS - Listed all sanctions: warning, fine up to 2% revenue (R$50M cap), daily fine, publication of infraction, data blocking, data deletion, suspension of operations. Referenced Articles 52, 53, 54.

---

### Query 10: EXPLANATION intent

**Query**: "How does the BCB cybersecurity resolution relate to the LGPD?"

| Metric | Value |
|--------|-------|
| Intent classified | EXPLANATION |
| Confidence | 0.78 |
| Weights | Graph: 0.4, Vector: 0.4, Community: 0.2 |
| Graph results | 6 (ResBCB4893 -> REFERENCES -> LGPD, shared entities) |
| Vector results | 5 (data protection sections from both) |
| Community results | 3 (cross-regulation community) |
| Final context chunks | 7 |
| Context tokens | 2,800 |
| Latency | 1.3s |

**Assessment**: PASS - Identified the REFERENCES edge between BCB 4.893 and LGPD, explained complementary data protection requirements, noted that 4.893 explicitly aligns with LGPD obligations for financial institutions. Cross-regulation connections were key.

## Summary

### Overall Results

| Metric | Value |
|--------|-------|
| Total queries tested | 10 |
| Queries passed | 10 |
| Queries failed | 0 |
| **Pass rate** | **100%** |

### By Intent Type

| Intent Type | Queries | Passed | Pass Rate |
|-------------|---------|--------|-----------|
| VALIDATION | 3 | 3 | 100% |
| COMPARISON | 2 | 2 | 100% |
| EXPLANATION | 3 | 3 | 100% |
| RECOMMENDATION | 1 | 1 | 100% |
| GENERAL | 1 | 1 | 100% |

### Performance Statistics

| Metric | Value |
|--------|-------|
| Average latency | 1.19s |
| Min latency | 0.9s |
| Max latency | 1.5s |
| Average context tokens | 2,534 |
| Average final chunks | 6.6 |
| Average graph results | 5.9 |
| Average vector results | 5.3 |
| Average community results | 2.5 |

### Key Observations

1. **Graph retrieval dominance**: For VALIDATION queries, the graph retriever consistently outperformed vector search by following direct relationship edges (e.g., DEFINES, REQUIRES, COMPOSED_OF).

2. **Cross-regulation queries**: The community retriever added significant value for queries spanning multiple regulations (Queries 4, 7, 10), surfacing connections that individual document retrieval missed.

3. **Entity resolution impact**: Bilingual aliases (PT/EN) enabled accurate entity matching even when queries used Portuguese terms (tested informally with "Basileia III", "risco de credito").

4. **Intent classification accuracy**: All 10 queries were correctly classified. The VALIDATION intent produced the most focused results due to high graph weight (0.7).

5. **Token efficiency**: Average context size (2,534 tokens) was well within the 4,000 token budget, leaving room for more complex queries or larger result sets.
