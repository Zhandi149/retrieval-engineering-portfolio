"""Conventional retrieval metrics; relevance labels are evaluator inputs only."""
import math


def evaluate(relevant, ranking, k):
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer")
    if len(set(ranking)) != len(ranking):
        raise ValueError("ranking must contain unique IDs")
    relevant = set(relevant)
    if not relevant:
        raise ValueError("at least one relevant document is required")
    top = ranking[:k]
    hits = [i for i, pid in enumerate(top, 1) if pid in relevant]
    ap = sum(count / rank for count, rank in enumerate(hits, 1)) / min(k, len(relevant))
    dcg = sum(1 / math.log2(rank + 1) for rank in hits)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
    return {"precision": len(hits) / k, "recall": len(hits) / len(relevant),
            "reciprocal_rank": 1 / hits[0] if hits else 0.0,
            "average_precision": ap, "ndcg": dcg / ideal}


def compare(cases, k):
    if not cases:
        raise ValueError("at least one evaluation case is required")
    rows = [dict(query_id=row["query_id"], **evaluate(row["relevant"], row["ranking"], k))
            for row in cases]
    names = [name for name in rows[0] if name != "query_id"]
    return {"per_query": rows, "macro_average": {
        name: sum(row[name] for row in rows) / len(rows) for name in names}}
