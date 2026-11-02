"""Prototype server for the transmog viewer: serves this folder, and /modelviewer/* from a local cache
that is filled on demand from wow.zamimg.com (fetched without an Origin header, which the CDN accepts).
Everything that was ever requested ends up in ./modelviewer/, i.e. the self-hosted dataset."""
import sys, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
CDN = "https://wow.zamimg.com"

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_GET(self):
        path = self.path.split("?")[0]
        # baked assets (site_build/transmog_assets): compact characters / models, packed item metadata, recompressed textures.
        # Anything not baked falls through to the raw dev cache below.
        for sub, ctype in (("chars", "application/gzip"), ("models", "application/gzip"), ("items", "application/json"), ("textures", "image/webp"), ("meta/character", "application/json"), ("meta/charactercustomization", "application/json")):
            prefix = "/modelviewer/classicplus/" + sub + "/"
            if path.startswith(prefix):
                f = ROOT.parent / "transmog_assets" / sub / path[len(prefix):]
                if f.is_file():
                    data = f.read_bytes()
                    self.send_response(200); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
                    return
        if path == "/proficiency.json":      # armor / weapon types each class can equip (data/wow_items/proficiency.json)
            data = (ROOT.parent.parent / "data" / "wow_items" / "proficiency.json").read_bytes()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            return
        if path == "/catalog.json":      # the item catalogue built by wow_transmog_catalog_build.py (dev only: the real page will ship its own copy)
            data = (ROOT.parent.parent / "data" / "wow_transmog_catalog.json").read_bytes()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            return
        if path.startswith("/modelviewer/"):
            local = ROOT / path.lstrip("/")
            if not local.exists():
                try:
                    req = urllib.request.Request(CDN + path, headers={"User-Agent": "Mozilla/5.0"})
                    data = urllib.request.urlopen(req, timeout=60).read()
                    local.parent.mkdir(parents=True, exist_ok=True)
                    local.write_bytes(data)
                    print("fetched", path, len(data))
                except urllib.error.HTTPError as e:
                    self.send_error(e.code, "cdn")
                    print("MISS", path, e.code)
                    return
        super().do_GET()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8952
    ThreadingHTTPServer(("", port), H).serve_forever()
