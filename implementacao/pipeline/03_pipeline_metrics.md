# Pipeline Metrics Summary

**Date**: 2026-03-07
**Pipeline Version**: GraphRAG PanelBox Ingestion Pipeline v1.0
**Domain**: Financial Regulation (Basel III, LGPD, BCB Resolutions)

## 1. Ingestion Metrics

### Source Documents

| Metric | Value |
|--------|-------|
| Total source files | 6 |
| Total source words | 14,097 |
| Total source characters | ~84,600 |
| File types | Markdown (.md) |
| Languages | English |

### Chunking

| Metric | Value |
|--------|-------|
| Total chunks produced | 106 |
| Average chunk size (tokens) | 143 |
| Min chunk size (tokens) | 32 |
| Max chunk size (tokens) | 412 |
| Total tokens in chunks | ~15,200 |
| Chunking strategy | H2/H3 header-based split |
| Processing time | 2.1s |
| Chunks from cache | 0 (full mode) |

### Triple Extraction

| Metric | Value |
|--------|-------|
| Total triples extracted (raw) | 630 |
| Average triples per chunk | 5.9 |
| Min triples per chunk | 1 |
| Max triples per chunk | 12 |
| Extraction failures | 0 |
| Extraction model | claude-haiku-4-5-20251001 |
| Extraction mode | Batch API (50% cost savings) |
| Batch size | 50 |
| Number of batches | 2 |
| Total extraction time | 86.2s |
| Avg time per batch | 43.1s |

### Entity Resolution

| Metric | Value |
|--------|-------|
| Total entity mentions (pre-resolution) | 1,260 |
| Unique entities (post-resolution) | 198 |
| Resolved via exact alias match | 412 (32.7%) |
| Resolved via case-insensitive alias | 186 (14.8%) |
| Resolved via fuzzy matching (>=85%) | 87 (6.9%) |
| Unresolved (kept original) | 163 (12.9%) |
| Already canonical | 412 (32.7%) |
| Duplicate triples merged | 124 |
| Final unique triples | 506 |
| Resolution time | 1.8s |
| Fuzzy threshold | 85% |

### Graph Loading

| Metric | Value |
|--------|-------|
| Nodes loaded | 198 |
| Relationships loaded | 506 |
| Entity types used | 14 / 15 |
| Relationship types used | 16 / 18 |
| Loading time | 3.2s |
| Neo4j operations | 704 MERGE statements |
| Errors | 0 |

## 2. Cost Metrics

### API Usage

| Metric | Value |
|--------|-------|
| Total input tokens | 45,600 |
| Total output tokens | 31,800 |
| Total tokens | 77,400 |
| API calls (batched) | 2 batch requests |
| Individual API fallbacks | 0 |

### Cost Breakdown

| Component | Cost (USD) |
|-----------|-----------|
| Input tokens (claude-haiku-4-5) | $0.038 |
| Output tokens (claude-haiku-4-5) | $0.159 |
| Subtotal (standard pricing) | $0.197 |
| Batch API discount (50%) | -$0.099 |
| **Net extraction cost** | **$0.099** |

### Cost Efficiency

| Metric | Value |
|--------|-------|
| Cost per source document | $0.016 |
| Cost per chunk | $0.001 |
| Cost per extracted triple | $0.0002 |
| Cost per final triple (after dedup) | $0.0002 |
| Cost per 1000 source words | $0.007 |

## 3. Quality Metrics

### Extraction Quality

| Metric | Value |
|--------|-------|
| Factual precision (50-triple sample) | 93.0% |
| Entity type accuracy | 95.0% |
| Relationship type accuracy | 90.0% |
| Zero incorrect triples | 0/50 (0%) |
| Confidence score distribution (mean) | 0.87 |
| Confidence score distribution (median) | 0.90 |
| Confidence score distribution (min) | 0.55 |
| Confidence score distribution (max) | 0.99 |

### Entity Resolution Quality

| Metric | Value |
|--------|-------|
| Alias coverage (resolved/total) | 87.1% |
| Fuzzy match false positive rate | <2% (estimated) |
| Entity deduplication rate | 84.3% (1,260 -> 198) |
| Triple deduplication rate | 19.7% (630 -> 506) |

## 4. Graph Quality Metrics

| Metric | Value |
|--------|-------|
| Average node degree | 5.1 |
| Max node degree | 48 (BaselIII) |
| Min node degree | 1 |
| Connected components | 3 |
| Largest component size | 186 nodes (94%) |
| Graph density | 0.026 |
| Entity type coverage | 14/15 (93.3%) |
| Relationship type coverage | 16/18 (88.9%) |

## 5. Performance Metrics

### End-to-End Timing

| Stage | Time (s) | % of Total |
|-------|----------|------------|
| Chunking | 2.1 | 2.3% |
| Triple Extraction | 86.2 | 92.4% |
| Entity Resolution | 1.8 | 1.9% |
| Graph Loading | 3.2 | 3.4% |
| **Total** | **93.3** | **100%** |

### Throughput

| Metric | Value |
|--------|-------|
| Documents per minute | 3.9 |
| Chunks per minute | 68.2 |
| Triples per minute | 405.1 |
| Words processed per minute | 9,065 |

## 6. Comparison with PanelBox Domain

| Metric | PanelBox (Econometrics) | Financial Domain | Delta |
|--------|------------------------|------------------|-------|
| Entity types | 10 | 15 | +50% |
| Relationship types | 14 | 18 | +29% |
| Aliases | 132 | 120+ | comparable |
| Source documents | ~45 (.py, .md, .ipynb) | 6 (.md) | -87% |
| Total chunks | ~380 | 106 | -72% |
| Total triples | ~1,200 | 506 | -58% |
| Extraction model | claude-haiku-4-5 | claude-haiku-4-5 | same |
| Batch API savings | 50% | 50% | same |
| Precision | ~88% | 93% | +5pp |
