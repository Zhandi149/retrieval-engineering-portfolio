"""Local demonstration server. Run with python -m retrieval_portfolio.server."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .evaluation import compare
from .graph import Graph
from .video import VideoCatalog

EDGES = [("Search UI", "Search API"), ("Search API", "Transcript index"),
         ("Search API", "Metadata catalog"), ("Transcript index", "Token scoring"),
         ("Metadata catalog", "Timestamp formatter"), ("Timestamp formatter", "Clip reference")]
GRAPH = Graph(EDGES)
CATALOG = VideoCatalog()


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, value):
        body = json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path)
        values = parse_qs(route.query)
        try:
            if route.path == "/":
                body = Path(__file__).with_name("index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route.path == "/api/search":
                query = values.get("q", [""])[0].strip()
                if not query or len(query) > 500:
                    raise ValueError("query must contain 1–500 characters")
                self.reply(200, {"results": CATALOG.search(query), "synthetic": True})
            elif route.path == "/api/graph":
                source = values.get("source", ["Search UI"])[0]
                target = values.get("target", ["Clip reference"])[0]
                depth = int(values.get("depth", ["6"])[0])
                result = GRAPH.shortest_path(source, target, depth)
                self.reply(200, dict(result, edges=EDGES, nodes=sorted(GRAPH.nodes)))
            else:
                self.reply(404, {"error": "route not found"})
        except (ValueError, TypeError) as error:
            self.reply(400, {"error": str(error)})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/evaluate":
            self.reply(404, {"error": "route not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 65536:
                self.reply(413, {"error": "body must contain 1–65536 bytes"})
                return
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
                raise ValueError("expected an object containing a cases list")
            self.reply(200, compare(payload["cases"], payload.get("k", 3)))
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            self.reply(400, {"error": str(error)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Portfolio: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
