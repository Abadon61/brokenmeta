"""Build the WoW: Forever class banners used to illustrate the news articles (logo/wow_class_art/<class>.jpg).

Source: the official class pages of worldofwarcraft.blizzard.com (en-us/game/classes/<class>): each page has a large
background painting and a character illustration on a transparent background. Both are downloaded once into
logo/wow_class_art/src/ and composed into one 1200x630 banner per class (the size social networks and Google
Discover use): background cover-cropped and darkened toward the left for text, the character on the right.
The images belong to Blizzard Entertainment and are credited on every page that shows them (fan-site use, the
user's choice on 2026-10-04: an illustration represents the class, whatever race the official art shows).

Run: py wow_class_art_build.py   (needs the network the first time; the banners are committed, the site build only copies them)
"""
import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "logo" / "wow_class_art"
SRC = OUT / "src"
CLASSES = ["warrior", "paladin", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"]
UA = {"User-Agent": "Mozilla/5.0"}
W, H = 1200, 630


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()


def art_urls(cls):
    html = fetch(f"https://worldofwarcraft.blizzard.com/en-us/game/classes/{cls}").decode("utf-8", "replace")
    urls = list(dict.fromkeys(re.findall(r"https://blz-contentstack-images\.akamaized\.net/v3/assets/[^\"'\s)\\]+?\.(?:png|jpg)", html)))
    # page order: [0] small class crest, [1] background painting (2400x1400 jpg), [2] character illustration (png)
    return urls[1], urls[2]


def banner(bg, ch):
    bg = bg.convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(1.2))
    # darken toward the left (room for the title on cards / social previews) and slightly overall
    shade = Image.new("L", (W, H))
    shade.putdata([int(150 - 110 * (x / W)) for y in range(H) for x in range(W)])
    canvas = Image.composite(Image.new("RGB", (W, H), (16, 11, 38)), bg, shade)
    ch = ch.convert("RGBA")
    # the official renders fade to an opaque light grey at the bottom: turn near-white pixels transparent
    px = ch.load()
    for y in range(ch.height):
        for x in range(ch.width):
            r, g, b, a = px[x, y]
            light = min(r, g, b)
            if light > 205 and max(r, g, b) - light < 18:
                px[x, y] = (r, g, b, int(a * max(0, (250 - light)) / 45))
    hs = (H * 1.02) / ch.height
    ch = ch.resize((round(ch.width * hs), round(ch.height * hs)), Image.LANCZOS)
    x = W - ch.width - 30 if ch.width < W * 0.6 else W - ch.width
    canvas.paste(ch, (max(x, W // 3), H - ch.height + 8), ch)
    return canvas


def generic():
    """Banner for articles and headlines that concern no single class: the nine class characters side by side
    on a dark background, with the site's "WoW: Forever" wordmark (Cal Sans, the site's display font)."""
    from PIL import ImageDraw, ImageFont
    canvas = banner(Image.open(SRC / "shaman-bg.jpg"), Image.new("RGBA", (10, 10), (0, 0, 0, 0)))
    order = ["rogue", "mage", "paladin", "warrior", "druid", "hunter", "priest", "shaman", "warlock"]
    step = W // (len(order) + 1)
    for i, cls in enumerate(order):
        ch = Image.open(SRC / f"{cls}-art.png").convert("RGBA")
        px = ch.load()
        for y in range(ch.height):
            for x in range(ch.width):
                r, g, b, a = px[x, y]
                light = min(r, g, b)
                if light > 205 and max(r, g, b) - light < 18:
                    px[x, y] = (r, g, b, int(a * max(0, (250 - light)) / 45))
        hs = (H * 0.62) / ch.height
        ch = ch.resize((round(ch.width * hs), round(ch.height * hs)), Image.LANCZOS)
        canvas.paste(ch, (step * (i + 1) - ch.width // 2, H - ch.height + 6), ch)
    shade = Image.new("L", (W, H))
    shade.putdata([int(max(0, 200 - y * 0.55)) if y < 300 else 0 for y in range(H) for x in range(W)])
    canvas = Image.composite(Image.new("RGB", (W, H), (16, 11, 38)), canvas, shade)
    # text-free copy for the news tiles, whose own title is written over the image
    canvas.save(OUT / "forever-plain.jpg", quality=84, optimize=True, progressive=True)
    # Same lettering as the site: Cal Sans in capitals (titles), the BROKEN / META(.GG) wordmark colours.
    d = ImageDraw.Draw(canvas)
    fonts = ROOT / "site_build" / "assets_src" / "fonts"
    big = ImageFont.truetype(str(fonts / "CalSans-Regular.ttf"), 92)
    mark = ImageFont.truetype(str(fonts / "CalSans-Regular.ttf"), 40)
    mono = ImageFont.truetype(str(fonts / "SpaceMono-Bold.ttf"), 24)
    cream, magenta, faint = (240, 231, 216), (215, 38, 56), (160, 150, 190)
    d.text((W // 2, 96), "WOW: FOREVER", font=big, fill=cream, anchor="mm", stroke_width=2, stroke_fill=cream)
    parts = [("BROKEN", mark, cream, 1), ("META", mark, magenta, 1), (".GG", mono, faint, 0)]
    widths = [d.textlength(t, font=f) + sw * 2 for t, f, _, sw in parts]
    x = W // 2 - sum(widths) / 2
    for (t, f, col, sw), w_ in zip(parts, widths):
        d.text((x, 172), t, font=f, fill=col, anchor="lm", stroke_width=sw, stroke_fill=col)
        x += w_
    canvas.save(OUT / "forever.jpg", quality=84, optimize=True, progressive=True)
    print("forever ->", (OUT / "forever.jpg").stat().st_size // 1024, "KB")


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    for cls in CLASSES:
        bg_p, ch_p = SRC / f"{cls}-bg.jpg", SRC / f"{cls}-art.png"
        if not (bg_p.exists() and ch_p.exists()):
            bg_u, ch_u = art_urls(cls)
            bg_p.write_bytes(fetch(bg_u))
            ch_p.write_bytes(fetch(ch_u))
            print(cls, "downloaded", bg_u, ch_u)
        img = banner(Image.open(bg_p), Image.open(ch_p))
        img.save(OUT / f"{cls}.jpg", quality=84, optimize=True, progressive=True)
        print(cls, "->", OUT / f"{cls}.jpg", (OUT / f"{cls}.jpg").stat().st_size // 1024, "KB")
    generic()


if __name__ == "__main__":
    main()
