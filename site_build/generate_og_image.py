"""One-off generator for the sitewide social-share image (og:image /
twitter:image) -- see base.html. Not part of build_site.py's per-build
pipeline: the output is a static PNG committed to logo/og-image.png, same
as the other hand-placed brand assets there (logo_epee_sans_fond.svg,
logo google.svg). Re-run this manually only when the brand or the headline
numbers change enough to be worth a refresh.

Run: py site_build/generate_og_image.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
FONTS = ROOT / "assets_src" / "fonts"
OUT = PROJECT / "logo" / "og-image.png"

W, H = 1200, 630

# Same palette as style_base.css's :root -- kept in sync by hand (this
# script runs standalone, not through Jinja/build_site.py's token setup).
BG = (11, 2, 33)
MAGENTA = (255, 45, 149)
CYAN = (5, 217, 232)
GOLD = (255, 194, 60)
TEAL = (45, 230, 196)
GRAY = (154, 143, 196)
CREAM = (243, 238, 255)
TEXT_DIM = (183, 169, 224)
TEXT_FAINT = (111, 95, 168)
RED = (255, 56, 100)


def lerp(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main() -> None:
    img = Image.new("RGB", (W, H), BG)

    # ---- Background: soft magenta glow top-center + faint cyan scanlines,
    # same idea as body's background in style_base.css. ----
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    cx, cy = W * 0.5, -40
    max_r = 720
    for r in range(max_r, 0, -4):
        t = 1 - (r / max_r)
        alpha = t * t * 0.55
        color = lerp(BG, MAGENTA, alpha)
        gd.ellipse([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], fill=color)
    img = Image.blend(img, glow, 1.0)
    draw = ImageDraw.Draw(img)
    for y in range(0, H, 26):
        draw.line([(0, y), (W, y)], fill=lerp(BG, CYAN, 0.05), width=1)

    # ---- Corner brackets, same motif as .corner on every comp-row card ----
    def bracket(x: int, y: int, dx: int, dy: int, size: int = 34, w: int = 3) -> None:
        draw.line([(x, y), (x + dx * size, y)], fill=CYAN, width=w)
        draw.line([(x, y), (x, y + dy * size)], fill=CYAN, width=w)

    m = 28
    bracket(m, m, 1, 1)
    bracket(W - m, m, -1, 1)
    bracket(m, H - m, 1, -1)
    bracket(W - m, H - m, -1, -1)

    # ---- Fonts ----
    cal_sans_72 = ImageFont.truetype(str(FONTS / "CalSans-Regular.ttf"), 72)
    cal_sans_48 = ImageFont.truetype(str(FONTS / "CalSans-Regular.ttf"), 46)
    mono_28 = ImageFont.truetype(str(FONTS / "SpaceMono-Regular.ttf"), 26)
    mono_22b = ImageFont.truetype(str(FONTS / "SpaceMono-Bold.ttf"), 22)

    left = 96
    y = 150

    # ---- Wordmark: "Broken" (cream) + "Meta" (magenta->cyan gradient) +
    # ".gg" (faint mono) -- exact same color split as .wordmark in
    # style_base.css. ----
    w_broken = draw.textlength("Broken", font=cal_sans_72)
    w_meta = draw.textlength("Meta", font=cal_sans_72)
    draw.text((left, y), "Broken", font=cal_sans_72, fill=CREAM)

    meta_x = left + w_broken
    meta_grad = Image.new("RGB", (round(w_meta) + 4, 90), BG)
    mgd = ImageDraw.Draw(meta_grad)
    for i in range(mgd.im.size[0]):
        t = i / max(1, mgd.im.size[0] - 1)
        mgd.line([(i, 0), (i, 90)], fill=lerp(MAGENTA, CYAN, t))
    mask = Image.new("L", meta_grad.size, 0)
    ImageDraw.Draw(mask).text((0, -6), "Meta", font=cal_sans_72, fill=255)
    img.paste(meta_grad, (round(meta_x), y - 6), mask)

    gg_x = meta_x + w_meta + 6
    draw.text((gg_x, y + 30), ".gg", font=mono_22b, fill=TEXT_FAINT)

    # ---- Tagline ----
    y2 = y + 110
    draw.text((left, y2), "TFT SET 18", font=cal_sans_48, fill=CYAN)
    w_tft = draw.textlength("TFT SET 18 ", font=cal_sans_48)
    draw.text((left + w_tft, y2), "TIER LIST", font=cal_sans_48, fill=CREAM)

    # ---- Divider ----
    y3 = y2 + 78
    draw.line([(left, y3), (left + 420, y3)], fill=TEXT_FAINT, width=2)

    # ---- Subtitle: real numbers, no invented stats ----
    y4 = y3 + 26
    draw.text((left, y4), "184 compositions réelles  ·  25 618 parties classées", font=mono_28, fill=TEXT_DIM)
    draw.text((left, y4 + 40), "Données Riot Match-V1 officielles, aucune stat inventée", font=mono_28, fill=TEXT_FAINT)

    # ---- Decorative tier-badge chips (S/A/B/C), same colors as the real
    # tier badges -- a little visual anchor to what the site actually is. ----
    chip_y = y4 + 108
    chip_w, chip_h, gap = 64, 64, 14
    chips = [("S", RED), ("A", GOLD), ("B", TEAL), ("C", GRAY)]
    cx0 = left
    for label, color in chips:
        draw.rectangle([cx0, chip_y, cx0 + chip_w, chip_y + chip_h], fill=color)
        tw = draw.textlength(label, font=cal_sans_48)
        draw.text((cx0 + chip_w / 2 - tw / 2, chip_y + 6), label, font=cal_sans_48, fill=BG)
        cx0 += chip_w + gap

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
