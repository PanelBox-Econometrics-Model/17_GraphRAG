# GraphRAG versus VectorRAG for Financial Document Processing

**Target journal:** Expert Systems with Applications (Elsevier)

## Overview

This paper presents a multi-strategy GraphRAG architecture for financial document processing and provides a rigorous empirical comparison against conventional vector-based RAG (VectorRAG). The system fuses three parallel retrieval strategies---graph traversal, vector similarity, and community summarization---with intent-aware weighting across six query types, evaluated on 250 financial and regulatory questions.

### Key Results

| Metric | GraphRAG (ours) | VectorRAG | Improvement |
|--------|-----------------|-----------|-------------|
| Faithfulness | 87.4% | 72.9% | +14.5 pp |
| Grounding rate | 96.4% | 55.0% | +41.3 pp |
| Weighted benchmark | 88.0% | 59.5% | +28.5 pp |
| Context tokens/query | 3,982 | 5,918 | -32.7% |
| Tokens vs. FullDocument | 3,982 | 15,014 | -73.5% |
| Latency (parallel+cache) | 797 ms | 1,182 ms | -33% |

### Ablation Study

The ablation study confirms all three retrieval strategies are complementary:

| Configuration | Score | Delta |
|---------------|-------|-------|
| Full system (Graph + Vector + Community) | 88.0% | --- |
| Without Graph retriever | 71.8% | -16.1 pp |
| Without Vector retriever | 78.4% | -9.5 pp |
| Without Community retriever | 83.2% | -4.7 pp |

## Paper Structure

| Section | Content |
|---------|---------|
| 1. Introduction | Problem statement: VectorRAG limitations for financial documents |
| 2. Related Work | VectorRAG to GraphRAG evolution, financial RAG, token efficiency |
| 3. Architecture | Ontology (10 entity types, 14 relationships), ingestion pipeline, multi-strategy retrieval with intent-aware fusion |
| 4. Methodology | Baselines (VectorRAG, MS GraphRAG, HybridRAG, No Retrieval), metrics, 250-question evaluation |
| 5. Results | Hallucination reduction, token economy, latency, end-to-end benchmark, ablation study |
| 6. Discussion | Key findings, GraphRAG vs. VectorRAG guidelines, limitations |
| 7. Conclusion | Summary and future work |

## Implementation Stack

Based on the PanelBox GraphRAG module (`/graphrag`):

- **Graph database:** Neo4j 5.x (knowledge graph + vector index)
- **Metadata store:** PostgreSQL 16 (cache, audit logs)
- **LLM:** Claude API (extraction and generation)
- **Embeddings:** all-MiniLM-L6-v2 (384 dimensions)
- **Community detection:** Leiden algorithm
- **API:** FastAPI
- **Entity resolution:** Exact + case-insensitive + fuzzy matching (threshold 0.85)

## Repository Structure

```
17_GraphRAG/
├── README.md                     # This file
├── paper/                        # Manuscript (LaTeX)
│   ├── main.tex                  # Main manuscript (~20-25 pages)
│   ├── references.bib            # Bibliography (43 entries)
│   ├── highlights.tex            # Journal highlights
│   ├── cover_letter.tex          # Cover letter
│   └── appendix/
│       └── online_appendix.tex   # Supplementary material
├── literatura/                   # Literature review notes
├── teoria/                       # Theoretical foundations
├── simulacoes/                   # Benchmarks and experiments
├── implementacao/                # Code and scripts
└── aplicacoes/                   # Empirical applications
```

## Contributions

1. **Multi-strategy retrieval with intent-aware fusion.** Three parallel strategies (graph, vector, community) with weights adapted to six query intent types. Achieves 87.4% faithfulness (+14.5 pp over VectorRAG).

2. **Token economy framework.** 70% token reduction versus full-document retrieval; 33% versus VectorRAG. Batch API indexation provides 50% cost savings. Break-even at ~687 queries.

3. **Financial domain ontology.** 10 entity types and 14 relationship types validated against Basel III, LGPD, GDPR, and SEC filings. Three-level entity resolution.

4. **Empirical evaluation with ablation.** 250-question evaluation demonstrating complementarity of all three strategies. Practical guidelines for when to adopt GraphRAG vs. VectorRAG.

## Reviewer Notes

### Reproducibility

- All experiments use fixed random seed (42)
- Hardware: 8 CPU cores, 32 GB RAM, Neo4j 5.x, PostgreSQL 16
- Evaluation protocol: LLM-as-judge validated by 2 domain experts on 10% sample
- Latency: median of 3 runs per query

### Datasets

- **Regulatory questions (200):** Basel III and LGPD, expert-annotated ground truth
- **Financial benchmark (50):** FinanceBench-style, 5 categories
- **Document corpus (150):** Regulatory frameworks, SEC 10-K filings, audit reports

### Baselines

All baselines use the same LLM for generation to isolate retrieval strategy effects:

| Baseline | Description |
|----------|-------------|
| VectorRAG | all-MiniLM-L6-v2 embeddings + cosine similarity |
| MS GraphRAG | Microsoft GraphRAG with Leiden communities |
| HybridRAG | Graph + vector without communities (BlackRock/NVIDIA) |
| No Retrieval | LLM parametric knowledge only |
| FullDocument | Complete source document as context (token baseline) |

### Known Limitations

1. Knowledge graph quality bounded by LLM extraction capability
2. Audit application uses simulated (not real institutional) data
3. API costs reflect pricing at evaluation time
4. Results validated on financial domain; generalization requires new ontology per domain
5. Single LLM provider (Claude API)
6. 250-question evaluation; larger datasets would strengthen statistical confidence

## Literature

43 papers catalogued across 9 categories:

| Category | Count | Key References |
|----------|-------|----------------|
| Core GraphRAG | 4 | Microsoft GraphRAG, GRAG, 2 surveys |
| Financial applications | 7 | HybridRAG (BlackRock), FinReflectKG, GraphCompliance |
| Token efficiency | 6 | TERAG, LazyGraphRAG, LightRAG, PolyG |
| Evaluation & benchmarks | 3 | RAG vs GraphRAG, Unbiased Evaluation, When-to-Use |
| Community detection | 3 | CommunityKG-RAG, Leiden, k-core |
| Other | 20 | Security, KG in finance, medical, foundational NLP |
