"""Launch the portfolio or run a terminal-only walkthrough."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

if __name__ == "__main__":
    if sys.argv[1:] == ["--demo"]:
        import json
        from retrieval_portfolio.server import GRAPH, CATALOG
        from retrieval_portfolio.evaluation import evaluate
        print("TRANSCRIPT SEARCH (fictional content)")
        print(json.dumps(CATALOG.search("appointment", 2), indent=2))
        print("DIRECTED GRAPH PATH")
        print(json.dumps(GRAPH.shortest_path("Search UI", "Clip reference"), indent=2))
        print("RANKING METRICS (fictional case)")
        print(json.dumps(evaluate({"a", "c"}, ["a", "b", "c"], 3), indent=2))
    else:
        from retrieval_portfolio.server import main
        main()
