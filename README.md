# Retrieval Engineering Portfolio

Three runnable software projects covering retrieval backends, graph traversal, ranking evaluation, and a clinical training transcript search interface.

**Python 3.10+ · Zero runtime dependencies · Browser UI + JSON APIs · Fictional data · Offline**

## Explore the projects

| Project | What a reviewer can try | Engineering demonstrated |
| --- | --- | --- |
| [Clinical video search](projects/clinical-video-search/README.md) | Search synthetic transcripts and inspect timestamped passage results. | BM25 indexing, metadata mapping, segment boundaries, accessible browser forms, JSON API. |
| [Graph search explorer](projects/graph-search/README.md) | Trace a route through a service dependency map and adjust the hop budget. | Directed BFS, cycle handling, deterministic traversal, resource bounds, API integration. |
| [Retrieval evaluation](projects/retrieval-evaluation/README.md) | Edit relevance labels and ranked lists; compare per-query and aggregate metrics. | Precision, recall, reciprocal rank, AP, nDCG, input validation, metric reporting. |

These are independently written portfolio demonstrations of conventional algorithms. They are not paper implementations, benchmark reproductions, or evidence of research performance. The clinical example uses invented training-session text and contains no real patient data or media.

## Run in one command

```bash
python3 run.py
```

Open **http://127.0.0.1:8765**. All three projects are available as tabs. If that port is occupied:

```bash
python3 run.py --port 8766
```

For a terminal-only walkthrough:

```bash
python3 run.py --demo
```

No API key, GPU, model download, database server, or package installation is required. The server binds to loopback for local demonstration. Stop it with Ctrl+C.

## Architecture

```text
Browser tabs / HTTP clients
           │
           ▼
Local threaded HTTP server
  ├── /api/search   → BM25 index → synthetic transcript catalog → timestamp metadata
  ├── /api/graph    → directed graph → bounded breadth-first search
  └── /api/evaluate → input validation → per-query metrics → macro averages
```

Business logic lives in small Python modules, independent of HTTP request handling. The browser sends search and evaluation requests to the same local origin. It renders returned strings as text nodes rather than inserting them as HTML.

## API examples

```bash
curl 'http://127.0.0.1:8765/api/search?q=appointment'
curl 'http://127.0.0.1:8765/api/graph?depth=3'
curl -X POST http://127.0.0.1:8765/api/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"k":3,"cases":[{"query_id":"demo","relevant":["a","c"],"ranking":["a","b","c"]}]}'
```

Search requires 1–500 non-whitespace query characters. Evaluation requests are limited to 64 KiB. Invalid queries, traversal budgets, duplicate ranked IDs, empty relevance sets, and malformed JSON receive errors rather than plausible-looking scores.

## Code map

```text
src/retrieval_portfolio/
  search.py             # Document model and in-memory BM25 index
  graph.py              # Directed breadth-first traversal
  evaluation.py         # Per-query metrics and macro averages
  video.py              # Transcript catalog and timestamp/segment projection
  server.py             # Local HTTP routes and JSON error responses
  index.html            # Responsive, keyboard-accessible three-tab interface
  sample_catalog.json   # Six entirely fictional transcript passages
projects/               # Project-specific design notes and limitations
tests/                 # Algorithm and live HTTP integration tests
```

## Verification

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Ten tests cover scoring and stable ties, empty indexes, graph cycles and budgets, known metric values, timestamp boundaries, HTTP success responses, invalid inputs, and oversized requests. A [GitHub Actions template](ci/github-actions.yml.example) is included for Python 3.10 and 3.12. It is not active: the current GitHub token lacks workflow-write permission. To enable it later, authorize that permission and place the template at `.github/workflows/checks.yml`.

For optional installation in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
retrieval-portfolio
```

## Tradeoffs and next steps

The implementations favor readability and easy local execution. BM25 scans a small in-memory corpus; it is not a vector index. The video demo locates transcript moments and does not perform speech recognition, video understanding, playback, or clinical decision support. The graph explorer uses a simple service map, not a domain reasoning engine. Metrics use binary relevance; aggregate scores are examples, not experimental findings.

A larger application could add an indexed storage backend, a media provider with authorized playback, browser automation tests, authentication, and deployment infrastructure. Those features are not implemented here. The built-in HTTP server is intended for local review rather than public hosting.

No external datasets, original research source, manuscripts, development logs, credentials, or institutional video URLs are included. No open-source license is granted; reuse permissions can be discussed separately.
