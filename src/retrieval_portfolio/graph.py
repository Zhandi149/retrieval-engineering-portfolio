"""Conventional directed breadth-first search with bounded depth and expansion."""
from collections import defaultdict, deque


class Graph:
    def __init__(self, edges):
        self.adjacency = defaultdict(set)
        self.nodes = set()
        for source, target in edges:
            self.adjacency[source].add(target)
            self.nodes.update((source, target))

    def shortest_path(self, source, target, max_depth=6, max_nodes=1000):
        if not 0 <= max_depth <= 20 or not 1 <= max_nodes <= 10000:
            raise ValueError("invalid traversal budget")
        if source not in self.nodes or target not in self.nodes:
            return {"path": [], "visited": 0, "truncated": False}
        queue, seen = deque([[source]]), {source}
        truncated = False
        while queue:
            path = queue.popleft()
            if path[-1] == target:
                return {"path": path, "visited": len(seen), "truncated": truncated}
            if len(path) - 1 >= max_depth:
                continue
            for neighbor in sorted(self.adjacency[path[-1]]):
                if neighbor in seen:
                    continue
                if len(seen) >= max_nodes:
                    truncated = True
                    continue
                seen.add(neighbor)
                queue.append(path + [neighbor])
        return {"path": [], "visited": len(seen), "truncated": truncated}
