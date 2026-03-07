# Formal Threat Model for GraphRAG in Financial Institutions

## 1. Overview

This document formalizes the threat model for multi-tenant GraphRAG systems deployed in financial institutions. The model identifies five threat categories (T1--T5), six defense mechanisms (D1--D6), and quantifies residual risk through red-team evaluation.

The threat model draws on:
- RAG Security and Privacy: Formalizing the Threat Model and Attack Surface (arXiv:2509.20324)
- Exposing Privacy Risks in Graph Retrieval-Augmented Generation (arXiv:2508.17222)
- Membership Inference Attacks Against Retrieval Augmented Generation (arXiv:2405.20446)
- SAG -- Provably Secure Retrieval-Augmented Generation (arXiv:2508.01084)

## 2. System Model

### 2.1 Architecture Scope

The threat model covers a multi-tenant GraphRAG system with the following components:

```
User -> [API Gateway] -> [Auth Middleware] -> [Intent Parser]
                                                    |
                              +---------------------+---------------------+
                              |                     |                     |
                        [Graph Retriever]    [Vector Retriever]   [Community Retriever]
                              |                     |                     |
                              +---------------------+---------------------+
                                                    |
                                            [Context Ranker]
                                                    |
                                         [Response Generator]
                                                    |
                                              [Audit Logger]
```

### 2.2 Trust Boundaries

| Boundary | Description |
|----------|-------------|
| B1: External | Between user and API Gateway (TLS) |
| B2: Authentication | Between API Gateway and authenticated pipeline |
| B3: Tenant | Between tenant-scoped data partitions in Neo4j |
| B4: LLM | Between retrieval pipeline and external LLM API |

### 2.3 Actors

| Actor | Description | Trust Level |
|-------|-------------|-------------|
| Authenticated User | Legitimate user with valid JWT token | Medium |
| Malicious Tenant | Authenticated user attempting to access other tenants' data | Low |
| External Attacker | Unauthenticated actor attempting to compromise the system | None |
| Insider Threat | Privileged user (admin/auditor) abusing access rights | Low--Medium |
| Data Poisoner | Actor with document ingestion privileges injecting adversarial content | Low |

## 3. Threat Catalog

### T1: Cross-Tenant Data Leakage

| Attribute | Detail |
|-----------|--------|
| **Description** | Unauthorized access to knowledge graph subgraphs belonging to other tenants. In a financial institution, this could mean the compliance department accessing audit department data, or one bank subsidiary accessing another's confidential information. |
| **Attack Vector** | (a) Direct Cypher injection bypassing tenant_id filters; (b) Relationship traversal crossing tenant boundaries; (c) Query manipulation to override tenant constraints; (d) Privilege escalation to admin role. |
| **STRIDE Category** | Information Disclosure |
| **Impact** | Critical. Violation of LGPD Art. 46 (security measures), GDPR Art. 32 (security of processing). Potential regulatory fines up to 2% of annual revenue (LGPD) or 4% (GDPR). Loss of banking license in severe cases. |
| **Likelihood** | Medium. Requires authenticated access but attack surface is broad. |
| **Risk Rating** | High |
| **Affected Components** | Neo4j query engine, retrieval pipeline, response generator |
| **References** | RAG Security Threat Model (arXiv:2509.20324), Section 3.2 |

### T2: Entity/Relationship Extraction Attacks

| Attribute | Detail |
|-----------|--------|
| **Description** | Crafted queries designed to extract the structure of the knowledge graph, revealing confidential entity relationships such as corporate hierarchies, regulatory mappings, and risk exposures. GraphRAG systems are particularly vulnerable because the graph structure itself encodes sensitive information (arXiv:2508.17222). |
| **Attack Vector** | (a) Schema discovery queries ("What entity types exist?"); (b) Enumeration queries ("List all companies"); (c) Relationship probing ("What is connected to Entity X?"); (d) Statistical inference from response patterns. |
| **STRIDE Category** | Information Disclosure |
| **Impact** | High. Exposure of corporate structure, business relationships, regulatory status. Could enable competitive intelligence, insider trading, or targeted social engineering. |
| **Likelihood** | Medium. Knowledge graph structure inherently reveals more than raw text retrieval (arXiv:2508.17222). |
| **Risk Rating** | High |
| **Affected Components** | Graph retriever, community retriever, response generator |
| **References** | Privacy Risks in GraphRAG (arXiv:2508.17222) |

### T3: Membership Inference Attacks

| Attribute | Detail |
|-----------|--------|
| **Description** | Queries designed to determine whether specific documents exist in the knowledge base. In financial contexts, confirming the existence of audit reports, investigation files, or merger documents can itself be sensitive information. |
| **Attack Vector** | (a) Direct existence probing ("Is document X in the database?"); (b) Semantic similarity comparison (S2MIA from arXiv:2405.20446) -- comparing response quality/specificity for queries about present vs. absent documents; (c) Differential probing -- detecting temporal changes in response quality. |
| **STRIDE Category** | Information Disclosure |
| **Impact** | Medium. Confirms existence of confidential documents (audit reports, investigation files). Could reveal regulatory actions or pending mergers before public disclosure. |
| **Likelihood** | Medium. S2MIA demonstrated effectiveness against RAG systems with minimal access. |
| **Risk Rating** | Medium |
| **Affected Components** | Retrieval pipeline, response generator, query cache |
| **References** | S2MIA (arXiv:2405.20446) |

### T4: Document Poisoning

| Attribute | Detail |
|-----------|--------|
| **Description** | Injection of adversarial content during the document ingestion phase, resulting in corrupted knowledge graph triples that propagate to generated responses. In financial systems, this could lead to incorrect compliance advice or manipulated risk assessments. |
| **Attack Vector** | (a) Adversarial documents containing misleading regulatory text; (b) Crafted entity names that alias with legitimate entities; (c) Confidence score manipulation through high-confidence false triples; (d) Community structure manipulation via injected relationships. |
| **STRIDE Category** | Tampering |
| **Impact** | High. Incorrect compliance advice could result in regulatory violations, financial losses, or legal liability. Corrupted risk assessments could lead to inadequate capital reserves. |
| **Likelihood** | Low--Medium. Requires document ingestion access, which is typically restricted. |
| **Risk Rating** | Medium--High |
| **Affected Components** | Ingestion pipeline (chunker, triple extractor, entity resolver), graph loader |
| **References** | RAG Security Threat Model (arXiv:2509.20324), Section 4 |

### T5: Query Manipulation

| Attribute | Detail |
|-----------|--------|
| **Description** | Crafted natural language queries designed to bypass access controls, extract unauthorized information, or cause the system to produce misleading responses. Includes prompt injection attempts targeting the LLM response generator. |
| **Attack Vector** | (a) Prompt injection via query text; (b) Cypher injection through entity extraction; (c) Resource exhaustion via complex graph traversals; (d) Intent misclassification to trigger inappropriate retrieval weights. |
| **STRIDE Category** | Tampering, Elevation of Privilege |
| **Impact** | Medium. Could bypass result filtering, trigger unintended system behavior, or cause denial of service. |
| **Likelihood** | Medium. Natural language interface provides broad attack surface. |
| **Risk Rating** | Medium |
| **Affected Components** | Intent parser, input sanitizer, graph retriever |
| **References** | RAG Security Threat Model (arXiv:2509.20324), Section 3.4 |

## 4. Defense Mechanisms

### D1: JWT Authentication + Role-Based Access Control (RBAC)

| Attribute | Detail |
|-----------|--------|
| **Implementation** | `src/api/middleware/auth.py` |
| **Threats Mitigated** | T1, T5 |
| **Description** | Every API request requires a valid JWT token (HS256, 24-hour expiration). The token carries user identity, tenant assignment, and role. The middleware validates token integrity, checks user active status, and injects SecurityContext into the request pipeline. Roles (admin, compliance_officer, auditor, analyst, viewer) determine entity type access permissions. |
| **Effectiveness** | Strong for external attackers (no access without valid token). Moderate for insider threats (valid token holders can still attempt cross-tenant access). |

### D2: Tenant Isolation in Neo4j

| Attribute | Detail |
|-----------|--------|
| **Implementation** | `implementacao/security/tenant_isolation.py` |
| **Threats Mitigated** | T1 |
| **Description** | Every node in the knowledge graph carries a `tenant_id` property. The `TenantIsolationManager` rewrites all Cypher MATCH patterns to include `{tenant_id: $tenant_id}` constraints before query execution. An index on `tenant_id` ensures efficient filtering. This ensures that graph traversals cannot cross tenant boundaries at the database level. |
| **Effectiveness** | Strong. Database-level enforcement prevents bypass through application-layer vulnerabilities. Tested with 100 adversarial queries achieving 0% leakage. |

### D3: Post-Retrieval Result Filtering

| Attribute | Detail |
|-----------|--------|
| **Implementation** | `TenantIsolationManager.filter_results()` |
| **Threats Mitigated** | T1, T5 |
| **Description** | Defense-in-depth layer that validates all query results against the SecurityContext before returning them to the caller. Checks both tenant_id membership and entity type access permissions. Also validates generated responses against a cross-tenant entity registry to detect entity name leakage. |
| **Effectiveness** | Moderate--Strong. Catches edge cases missed by query-level filtering (e.g., results returned via OPTIONAL MATCH patterns). |

### D4: Input Sanitization

| Attribute | Detail |
|-----------|--------|
| **Implementation** | `InputSanitizer` class in `tenant_isolation.py`; triple validation in `src/ingestion/triple_extractor.py` |
| **Threats Mitigated** | T4, T5 |
| **Description** | Two-layer sanitization: (1) Query-level: detects and blocks dangerous Cypher patterns (DELETE, DETACH, DROP, LOAD CSV, CALL db/apoc, etc.), enforces maximum query length, strips control characters. (2) Ingestion-level: validates extracted triples against the financial ontology, requiring entity types from T_V and relationship types from T_E. Triples with unrecognized types are rejected. |
| **Effectiveness** | Moderate. Blocks known injection patterns but cannot prevent novel attacks. Ontology validation limits poisoning but does not prevent within-ontology manipulation. |

### D5: Audit Logging

| Attribute | Detail |
|-----------|--------|
| **Implementation** | PostgreSQL `usage_logs` table; `AuditLogger` class |
| **Threats Mitigated** | T1, T2, T3, T4, T5 (detection) |
| **Description** | Comprehensive logging of all access attempts, security events, and system operations. Each log entry records: user_id, tenant_id, role, query hash, result counts, filtering actions, and timestamps. Logs are stored in PostgreSQL for durability and queryability. Supports LGPD Art. 18 (right to access processing records), Basel III Pillar 3 (operational risk disclosure), and SOX Section 404 (internal control evidence). |
| **Effectiveness** | Strong for detection and forensics. Does not prevent attacks but enables rapid incident response and provides compliance evidence. |

### D6: Response Attribution

| Attribute | Detail |
|-----------|--------|
| **Implementation** | `src/generation/response_generator.py` |
| **Threats Mitigated** | T4 |
| **Description** | Every claim in a generated response is linked to specific knowledge graph triples or document chunks with source attribution. This enables: (1) verification of response accuracy against source material, (2) detection of poisoned triples by tracing incorrect claims to their source, (3) regulatory compliance through auditable response provenance. |
| **Effectiveness** | Moderate. Enables detection of T4 after the fact but does not prevent initial poisoning. Requires human review of attributed sources for full effectiveness. |

## 5. Red-Team Evaluation Results

### 5.1 Attack 1: Cross-Tenant Data Leakage

| Metric | Result | Target |
|--------|--------|--------|
| Total queries | 100 | -- |
| Successful leakage | 0 | 0 |
| Leakage rate | 0.0% | 0.0% |
| Status | PASS | -- |

**Breakdown by attack category:**

| Category | Queries | Successful | Rate |
|----------|---------|------------|------|
| Direct access | 25 | 0 | 0.0% |
| Traversal access | 25 | 0 | 0.0% |
| Cypher injection | 25 | 0 | 0.0% |
| Privilege escalation | 25 | 0 | 0.0% |

**Analysis:** The combination of D2 (tenant isolation at query level) and D3 (post-retrieval filtering) successfully prevented all 100 cross-tenant access attempts. Cypher injection attempts were blocked by D4 (input sanitization) before reaching the query engine. Privilege escalation attempts via natural language were handled by the intent parser, which does not support role modification through queries.

### 5.2 Attack 2: Entity/Relationship Extraction

| Metric | Result | Target |
|--------|--------|--------|
| Total queries | 50 | -- |
| Successful extractions | 2 | <2.5 |
| Success rate | 4.0% | <5.0% |
| Status | PASS | -- |

**Breakdown by query category:**

| Category | Queries | Successful | Rate |
|----------|---------|------------|------|
| Structure discovery | 15 | 1 | 6.7% |
| Targeted extraction | 15 | 1 | 6.7% |
| Inference attacks | 10 | 0 | 0.0% |
| Exhaustive enumeration | 10 | 0 | 0.0% |

**Analysis:** Two extraction queries partially succeeded: one structure discovery query revealed the number of entity types within the attacker's tenant scope (which is permissible within-tenant information), and one targeted extraction query returned entity names within the attacker's authorized scope. No cross-tenant structural information was exposed. This aligns with the privacy risk identified by (arXiv:2508.17222): GraphRAG inherently reveals more structured information than text-based RAG, but tenant isolation constrains the exposure to within-tenant data.

### 5.3 Attack 3: Membership Inference

| Metric | Result | Target |
|--------|--------|--------|
| Total queries | 50 | -- |
| Correct inferences | 28 | <30 |
| Accuracy | 56.0% | <60.0% |
| Random baseline | 50.0% | -- |
| Status | PASS | -- |

**Breakdown by probe type:**

| Category | Queries | Correct | Accuracy |
|----------|---------|---------|----------|
| Existence probes | 20 | 12 | 60.0% |
| Semantic probes | 15 | 8 | 53.3% |
| Differential probes | 15 | 8 | 53.3% |

**Analysis:** The overall accuracy of 56.0% is close to the random baseline of 50.0%, indicating that the system's responses do not reliably distinguish between queries about present vs. absent documents. Direct existence probes showed slightly higher accuracy (60.0%) because the system sometimes provides more detailed responses for queries about present documents. This is a known limitation: response normalization trades off response quality against membership inference resistance. Semantic and differential probes performed near-random, suggesting effective response uniformity for indirect queries.

## 6. Residual Risk Analysis

### 6.1 Residual Risks After Mitigation

| Risk ID | Description | Residual Level | Justification |
|---------|-------------|----------------|---------------|
| RR1 | Within-tenant entity extraction | Low | Users can discover structure within their own tenant scope. This is by design -- users need to query their own data. |
| RR2 | Membership inference via existence probes | Low | 60% accuracy on direct probes is above random but below actionable levels. Further mitigation possible via response normalization. |
| RR3 | Novel injection patterns | Low--Medium | Input sanitization blocks known patterns but zero-day Cypher injection techniques could bypass. Mitigated by parameterized queries and audit logging. |
| RR4 | Insider threat with admin role | Medium | Admin users bypass tenant isolation by design. Mitigated by audit logging (D5) and principle of least privilege in role assignment. |
| RR5 | LLM-mediated information leakage | Low--Medium | The LLM response generator could inadvertently include information from its training data that pertains to other tenants. Mitigated by context-only response generation and source attribution (D6). |
| RR6 | Community summary leakage | Low | Community summaries could aggregate information from multiple entity types, potentially revealing patterns. Mitigated by tenant-scoped community detection. |

### 6.2 Recommendations for Future Mitigation

1. **Response normalization for membership inference:** Implement response templates that provide uniform response structure regardless of document presence, reducing existence probe accuracy to near-random levels.

2. **Rate limiting per tenant:** Add per-tenant query rate limits to prevent exhaustive enumeration attacks and resource exhaustion (recommended: 100 queries/minute per tenant).

3. **Anomaly detection on query patterns:** Deploy unsupervised anomaly detection on audit logs to identify reconnaissance activity (e.g., systematic entity enumeration, unusual query volumes).

4. **Differential privacy for community summaries:** Apply differential privacy mechanisms to community summaries to prevent statistical inference about community membership, following FairRAG (2025) methodology.

5. **Periodic red-team reassessment:** Schedule quarterly red-team evaluations with updated attack techniques to maintain security posture against evolving threats.

## 7. Threat-Defense Mapping Summary

| Threat | D1 (JWT+RBAC) | D2 (Tenant Isolation) | D3 (Result Filter) | D4 (Sanitization) | D5 (Audit Log) | D6 (Attribution) |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|
| T1: Cross-Tenant Leakage | P | P | P | -- | D | -- |
| T2: Entity Extraction | -- | -- | P | -- | D | -- |
| T3: Membership Inference | -- | -- | -- | -- | D | -- |
| T4: Document Poisoning | -- | -- | -- | P | D | D |
| T5: Query Manipulation | P | -- | P | P | D | -- |

Legend: **P** = Prevention, **D** = Detection, **--** = Not applicable
