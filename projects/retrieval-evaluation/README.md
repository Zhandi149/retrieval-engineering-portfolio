# Retrieval Evaluation Toolkit

An editable ranking-evaluation interface with per-query results and macro averages.

## Metrics

For cutoff `k` and binary relevance:

- Precision@k divides relevant hits by `k`, including unfilled slots in the denominator.
- Recall@k divides relevant hits by the number of relevant documents.
- Reciprocal rank@k uses the first relevant hit, or zero when absent.
- Average precision@k sums precision at relevant ranks and divides by `min(k, number of relevant documents)`.
- nDCG@k uses binary gains, logarithmic rank discounting, and an ideal ordering at the same cutoff.

The average is computed per query, then averaged equally across queries. Empty relevance sets and duplicate ranked IDs are rejected to keep metric conventions explicit.

## Implementation

[evaluation.py](../../src/retrieval_portfolio/evaluation.py) contains the evaluator and aggregation. [server.py](../../src/retrieval_portfolio/server.py) validates request size and exposes `POST /api/evaluate`. The browser displays a comparison table.

Run `python3 run.py` from the repository root and open the third tab. Move a relevant ID lower in a ranking and observe how ranking-sensitive metrics change while recall may remain constant.

## Scope

The examples are fictional. This toolkit does not retrieve passages, train rankers, generate answers, report paper results, or establish statistical significance. Graded relevance, confidence intervals, and large-scale experiment tracking are possible future extensions.
