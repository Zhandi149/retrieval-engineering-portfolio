# Directed Graph Search Explorer

An interactive service-map explorer using conventional breadth-first search.

Select a source and destination and adjust the maximum hop count. The interface displays a shortest directed path, discovered-node count, and expansion-budget status.

## Implementation

[graph.py](../../src/retrieval_portfolio/graph.py) stores deduplicated directed adjacency sets. Traversal uses a queue and visited set to handle cycles. Sorted neighbors produce deterministic choices between equally short paths. Depth and discovered-node limits bound exploration.

The [server](../../src/retrieval_portfolio/server.py) exposes the graph through `GET /api/graph`. The default path connects Search UI to Clip reference through the fictional service map.

Run `python3 run.py` from the repository root and open the second tab. Compare depth 3 with depth 4 for the default endpoints.

## Design limits

Edges are unweighted, so BFS is appropriate. Relations are directional. An unknown node or unreachable destination returns an empty path. The `truncated` flag reports exhaustion of the node expansion budget; the depth cutoff is supplied explicitly by the caller. This is not semantic reasoning or a research-method implementation.
