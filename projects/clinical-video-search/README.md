# Clinical Training Video Search Demo

A local web interface for finding timestamped passages in synthetic clinical-training transcripts.

## User flow

1. Enter a phrase such as `appointment` or `consent documentation`.
2. The search API scores transcript passages with BM25.
3. Results display passage text, the fictional source-session identifier, start timestamp, and five-minute segment number.
4. A reviewer can trace each result to its catalog record without needing a model or external service.

## Implementation

- [search.py](../../src/retrieval_portfolio/search.py): normalization, document frequencies, length normalization, deterministic BM25 ranking.
- [video.py](../../src/retrieval_portfolio/video.py): source metadata and timestamp mapping.
- [index.html](../../src/retrieval_portfolio/index.html): responsive search UI with live result announcements.
- [sample_catalog.json](../../src/retrieval_portfolio/sample_catalog.json): synthetic content suitable for local demonstration.

Segment intervals are half-open: seconds 0–299 belong to segment 1; second 300 starts segment 2. This makes zero-time and boundary behavior explicit.

Run `python3 run.py` from the repository root and open the first tab. API: `GET /api/search?q=appointment`.

## Scope

This is transcript retrieval, not video analysis. The corpus has six invented passages. No real videos, patient records, medical recommendations, institutional branding, or external media URLs are shipped. Timestamp references do not open playable media. BM25 is lexical; semantic retrieval and reranking are possible extensions, not existing features.
