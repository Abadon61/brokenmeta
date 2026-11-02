"""Recompress the textures of the transmog simulator for hosting.

    py -3.11 recompress_textures.py <ids.json> [more ids.json ...] [--max 1024] [--quality 78]

For every texture id of the lists: reads ../transmog_proto/modelviewer/classicplus/textures/<id>.webp (the dev cache) and writes
../transmog_assets/textures/<id>.webp, smaller:
  * images wider than --max are halved until they fit (the 2048x1024 skin atlases: the viewer draws at about 600 px, so 1024x512 is plenty),
  * re-encoded as WebP at --quality (alpha kept, method 6).
The original bytes are copied when the result would not be smaller. Prints the totals before / after.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "transmog_proto" / "modelviewer" / "classicplus" / "textures"
OUT = ROOT.parent / "transmog_assets" / "textures"


def main() -> None:
    args = sys.argv[1:]
    mx, q = 1024, 78
    lists = []
    i = 0
    while i < len(args):
        if args[i] == "--max":
            mx = int(args[i + 1]); i += 2
        elif args[i] == "--quality":
            q = int(args[i + 1]); i += 2
        else:
            lists.append(args[i]); i += 1
    ids = sorted({int(x) for f in lists for x in json.loads(Path(f).read_text(encoding="utf-8"))})
    OUT.mkdir(parents=True, exist_ok=True)
    before = after = n = missing = 0
    for tid in ids:
        src = SRC / f"{tid}.webp"
        if not src.exists():
            missing += 1
            continue
        raw = src.read_bytes()
        before += len(raw)
        try:
            im = Image.open(io.BytesIO(raw))
            im.load()
            while im.width > mx:
                im = im.resize((im.width // 2, max(1, im.height // 2)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=q, method=6)
            out = buf.getvalue()
            if len(out) >= len(raw) and im.width == Image.open(io.BytesIO(raw)).width:
                out = raw
        except Exception as e:           # an odd file: keep it as it is
            print(f"  texture {tid}: {e}")
            out = raw
        (OUT / f"{tid}.webp").write_bytes(out)
        after += len(out)
        n += 1
    print(f"{n} textures: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB ({missing} not downloaded yet)")


if __name__ == "__main__":
    main()
