"""
Static file server for the Content Studio tool, with one extra route:
POST /save-png writes a base64 PNG straight to social_content/out/ instead of
going through the browser's download flow (Chrome silently blocks the 2nd+
automatic download from the same origin in a session, so relying on
`<a download>` clicks is not reliable for exporting several cards back to back).

Run via the "social-content-studio" launch.json config (serves the repo root
so relative paths to /logo/ and /site_build/dist/assets/... resolve).
"""
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

OUT_DIR = Path("D:/Site internet/RS")
OUT_DIR.mkdir(exist_ok=True, parents=True)


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/save-png":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        filename = re.sub(r"[^a-zA-Z0-9_-]", "", body["filename"]) + ".png"
        target = OUT_DIR / filename
        import base64
        import os
        import time
        raw = base64.b64decode(body["data"])
        # Write to a temp file then atomically replace the target. Windows
        # occasionally raises "OSError: Invalid argument" writing straight to
        # a path that a viewer/indexer/antivirus has a transient handle on
        # (seen in practice re-exporting a file right after it was opened to
        # preview it) -- os.replace + a couple retries rides that out.
        tmp = target.with_suffix(".tmp")
        for attempt in range(5):
            try:
                tmp.write_bytes(raw)
                os.replace(tmp, target)
                break
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(0.3)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "path": str(target)}).encode())

    def log_message(self, fmt, *args):
        pass  # keep preview_logs quiet for normal GETs


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8948
    import os
    os.chdir(Path(__file__).resolve().parent.parent)  # serve repo root
    ThreadingHTTPServer(("", port), Handler).serve_forever()
