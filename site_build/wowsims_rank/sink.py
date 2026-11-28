"""Local sink for the browser: POST /save?name=<file> with a body writes requests/<file>.json (the RaidSimRequest that
wowsims.com/forever's 'Export > CLI' gives for a spec's preset). usage: py sink.py [port]"""
import re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

OUT = Path(__file__).parent / "requests"
OUT.mkdir(exist_ok=True)


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        name = parse_qs(urlparse(self.path).query).get("name", [""])[0]
        if not re.fullmatch(r"[a-z0-9_]+", name):
            self.send_response(400); self._cors(); self.end_headers(); return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if "form-urlencoded" in (self.headers.get("Content-Type") or ""):   # a form POST from the page (fetch to localhost is blocked there)
            body = parse_qs(body.decode("utf-8"))["data"][0].encode("utf-8")
        (OUT / (name + ".json")).write_bytes(body)
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b"ok")


HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8961), H).serve_forever()
