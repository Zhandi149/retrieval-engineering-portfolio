import json
from http.server import ThreadingHTTPServer
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from retrieval_portfolio.search import Document, SearchIndex
from retrieval_portfolio.graph import Graph
from retrieval_portfolio.evaluation import evaluate
from retrieval_portfolio.video import segment_number, timestamp
from retrieval_portfolio.server import Handler


class AlgorithmTests(unittest.TestCase):
    def test_search_empty_index_and_duplicate_ids(self):
        self.assertEqual(SearchIndex([]).search("appointment"), [])
        with self.assertRaises(ValueError):
            SearchIndex([Document("a", "one"), Document("a", "two")])

    def test_search_stable_ties_and_relevance(self):
        index = SearchIndex([Document("b", "blue book"), Document("a", "blue book"),
                             Document("c", "green garden"), Document("d", "")])
        self.assertEqual([h["id"] for h in index.search("BLUE")], ["a", "b"])
        self.assertEqual(index.search("unmatched"), [])
        self.assertEqual(index.search("blue", limit=0), [])

    def test_directed_graph_cycles_and_depth(self):
        graph = Graph([("a", "b"), ("b", "a"), ("b", "c")])
        self.assertEqual(graph.shortest_path("a", "c")["path"], ["a", "b", "c"])
        self.assertEqual(graph.shortest_path("c", "a")["path"], [])
        self.assertEqual(graph.shortest_path("a", "c", max_depth=1)["path"], [])
        self.assertEqual(graph.shortest_path("a", "a", max_depth=0)["path"], ["a"])

    def test_graph_budget_keeps_already_discovered_target(self):
        graph = Graph([("a", "b"), ("a", "c")])
        result = graph.shortest_path("a", "b", max_nodes=2)
        self.assertEqual(result["path"], ["a", "b"])
        self.assertLessEqual(result["visited"], 2)
        self.assertTrue(result["truncated"])

    def test_metrics_known_ranking(self):
        result = evaluate({"a", "c"}, ["a", "b", "c"], 3)
        self.assertAlmostEqual(result["precision"], 2 / 3)
        self.assertEqual(result["recall"], 1)
        self.assertAlmostEqual(result["average_precision"], 5 / 6)
        self.assertEqual(evaluate({"a"}, ["x"], 3)["recall"], 0)
        with self.assertRaises(ValueError):
            evaluate({"a"}, ["a", "a"], 3)

    def test_video_timestamp_and_segment_boundaries(self):
        self.assertEqual([segment_number(t) for t in (0, 299, 300, 600)], [1, 1, 2, 3])
        self.assertEqual(timestamp(3661), "01:01:01")
        with self.assertRaises(ValueError):
            timestamp(-1)
        with self.assertRaises(ValueError):
            segment_number(0, 0)


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_ui_and_search_api(self):
        with urlopen(self.base) as response:
            self.assertIn(b"Clinical video search", response.read())
        with urlopen(self.base + "/api/search?q=consent") as response:
            result = json.load(response)
        self.assertEqual(result["results"][0]["timestamp"], "00:05:00")
        self.assertTrue(result["synthetic"])

    def test_graph_api(self):
        with urlopen(self.base + "/api/graph") as response:
            data = json.load(response)
        self.assertEqual(data["path"], ["Search UI", "Search API", "Metadata catalog",
                                         "Timestamp formatter", "Clip reference"])

    def test_evaluation_api(self):
        body = {"cases": [{"query_id": "q", "relevant": ["a"], "ranking": ["a"]}], "k": 1}
        request = Request(self.base + "/api/evaluate", data=json.dumps(body).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            self.assertEqual(json.load(response)["macro_average"]["ndcg"], 1)

    def test_bad_requests_are_rejected(self):
        for path in ("/api/search?q=", "/api/graph?depth=-1", "/missing"):
            with self.assertRaises(HTTPError) as caught:
                urlopen(self.base + path)
            self.assertIn(caught.exception.code, (400, 404))
            caught.exception.close()
        for body in (b"not json", b"[]", b'{"cases":[]}', b"x" * 65537):
            request = Request(self.base + "/api/evaluate", data=body)
            with self.assertRaises(HTTPError) as caught:
                urlopen(request)
            self.assertIn(caught.exception.code, (400, 413))
            caught.exception.close()


if __name__ == "__main__":
    unittest.main()
