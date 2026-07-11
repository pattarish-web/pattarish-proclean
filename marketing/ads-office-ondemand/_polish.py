# -*- coding: utf-8 -*-
"""Polish feed/stories/line outputs from final campaign art + C/D overlays."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
ART = ROOT / "art"
FONTS = ROOT / "fonts"

TEAL = (13, 148, 136)
DARK = (15, 23, 42)
AMBER = (245, 158, 11)
WHITE = (255, 255, 255)
INK = (30, 41, 59)
SOFT = (226, 232, 240)
MUTED_LT = (100, 116, 139)


def fnt(size: int, weight: str = "bold") -> ImageFont.ImageFont:
    names = {
        "bold": "Prompt-Bold.ttf",
        "semibold": "Prompt-SemiBold.ttf",
        "medium": "Prompt-Medium.ttf",
        "regular": "Prompt-Regular.ttf",
    }
    path = FONTS / names.get(weight, names["bold"])
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def cover(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    tw, th = size
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def tw(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def write(draw, xy, text, font, fill, shadow=False):
    x, y = xy
    if shadow:
        draw.text((x + 1, y + 2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def save(img: Image.Image, rel: str):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    ImageEnhance.Contrast(img).enhance(1.04).save(out, "PNG", optimize=True)
    print("wrote", out.relative_to(ROOT))


def brand_mark(draw, x=48, y=44, on_dark=True):
    write(draw, (x, y), "Sangkan Office", fnt(22, "semibold"), TEAL)
    draw.rectangle([x, y + 30, x + 48, y + 33], fill=AMBER if on_dark else TEAL)


def small_cta(draw, x, y, text, dark_bg=True):
    font = fnt(20, "semibold")
    w, h = tw(draw, text, font)
    pad_x, pad_y = 18, 10
    if dark_bg:
        draw.rectangle([x, y, x + w + pad_x * 2, y + h + pad_y * 2], fill=WHITE)
        write(draw, (x + pad_x, y + pad_y - 1), text, font, DARK)
    else:
        draw.rectangle([x, y, x + w + pad_x * 2, y + h + pad_y * 2], fill=TEAL)
        write(draw, (x + pad_x, y + pad_y - 1), text, font, WHITE)
    return y + h + pad_y * 2


def feed_a(size, rel):
    """Final A campaign art — cover crop only."""
    save(cover(ART / "final-A-campaign.png", size), rel)


def feed_e(size, rel):
    """Final E campaign art — cover crop only."""
    save(cover(ART / "final-E-campaign.png", size), rel)


def feed_b(size, rel):
    """Typeset Thai onto cream brochure paper (art-B mockup, fallback final-B)."""
    art = ART / "art-B-print-mockup.png"
    if not art.exists():
        art = ART / "final-B-brochure-ad.png"
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size

    # Blank paper sits roughly in the center of the mockup
    cx = int(w * 0.42)
    cy = int(h * 0.28)
    if h > w * 1.2:  # stories taller — drop paper block into mid frame
        cy = int(h * 0.34)

    # Scale type slightly for stories
    scale = 1.0 if size[1] <= 1200 else 1.15
    def s(n):
        return int(n * scale)

    y = cy
    write(draw, (cx, y), "Sangkan Office", fnt(s(18), "semibold"), TEAL)
    y += s(34)
    write(draw, (cx, y), "\u0e41\u0e21\u0e48\u0e1a\u0e49\u0e32\u0e19\u0e2d\u0e2d\u0e1f\u0e1f\u0e34\u0e28 On-Demand", fnt(s(26), "bold"), INK)
    y += s(48)
    draw.rectangle([cx, y, cx + s(56), y + 3], fill=TEAL)
    y += s(28)

    write(draw, (cx, y), "S  \u0e3f2,900 / 4 \u0e04\u0e23\u0e31\u0e49\u0e07", fnt(s(28), "bold"), INK)
    y += s(44)
    write(draw, (cx, y), "M  \u0e3f6,900 / 8 \u0e04\u0e23\u0e31\u0e49\u0e07 (\u0e41\u0e19\u0e30\u0e19\u0e33)", fnt(s(28), "bold"), INK)
    y += s(52)
    write(
        draw,
        (cx, y),
        "\u0e0a\u0e27\u0e19\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e19\u0e43\u0e19\u0e42\u0e0b\u0e19 \xb7 \u0e40\u0e04\u0e23\u0e14\u0e34\u0e15\u0e04\u0e37\u0e19 10%",
        fnt(s(16), "medium"),
        MUTED_LT,
    )
    y += s(40)
    small_cta(draw, cx, y, "\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e41\u0e1e\u0e47\u0e04\u0e43\u0e19 LINE", dark_bg=False)
    save(img, rel)


def creative_c(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw)

    y = int(h * 0.62)
    write(draw, (48, y), "\u0e40\u0e0a\u0e47\u0e04\u0e2d\u0e34\u0e19 GPS", fnt(44, "bold"), WHITE, shadow=True)
    y += 54
    write(draw, (48, y), "\u0e2a\u0e48\u0e07\u0e23\u0e39\u0e1b\u0e01\u0e48\u0e2d\u0e19\u2013\u0e2b\u0e25\u0e31\u0e07", fnt(44, "bold"), WHITE, shadow=True)
    y += 58
    write(
        draw,
        (48, y),
        "\u0e40\u0e23\u0e34\u0e48\u0e21 \u0e3f2,900/\u0e40\u0e14\u0e37\u0e2d\u0e19 \xb7 \u0e44\u0e21\u0e48\u0e15\u0e49\u0e2d\u0e07\u0e21\u0e35\u0e1c\u0e39\u0e49\u0e08\u0e31\u0e14\u0e01\u0e32\u0e23",
        fnt(20, "medium"),
        SOFT,
        shadow=True,
    )
    y += 42
    small_cta(draw, 48, y, "\u0e14\u0e39\u0e41\u0e1e\u0e47\u0e04 S / M")
    save(img, rel)


def creative_d(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw, on_dark=True)

    x = int(w * 0.48)
    y = int(h * 0.28)
    write(draw, (x, y), "EARLY BIRD", fnt(16, "semibold"), AMBER, shadow=True)
    y += 36
    write(draw, (x, y), "\u0e25\u0e47\u0e2d\u0e01\u0e2a\u0e31\u0e0d\u0e0d\u0e32", fnt(48, "bold"), WHITE, shadow=True)
    y += 58
    write(draw, (x, y), "\u0e40\u0e23\u0e34\u0e48\u0e21\u0e40\u0e14\u0e37\u0e2d\u0e19\u0e2b\u0e19\u0e49\u0e32", fnt(48, "bold"), WHITE, shadow=True)
    y += 64
    write(
        draw,
        (x, y),
        "\u0e2d\u0e38\u0e14\u0e21\u0e2a\u0e38\u0e02\u2013\u0e1a\u0e32\u0e07\u0e19\u0e32 \xb7 S / M",
        fnt(20, "medium"),
        SOFT,
        shadow=True,
    )
    y += 44
    small_cta(draw, x, y, "\u0e08\u0e2d\u0e07\u0e1c\u0e48\u0e32\u0e19 LINE")
    save(img, rel)


def main():
    feed = (1080, 1080)
    stories = (1080, 1920)

    feed_a(feed, "feed/A-hook-no-permanent.png")
    feed_b(feed, "feed/B-price-sm.png")
    creative_c(feed, ART / "art-C-cinematic.png", "feed/C-trust-gps.png")
    creative_d(feed, ART / "art-D-sunrise.png", "feed/D-early-bird.png")
    feed_e(feed, "feed/E-affiliate-credit.png")

    feed_a(stories, "stories/A-hook-no-permanent.png")
    feed_b(stories, "stories/B-price-sm.png")
    creative_d(stories, ART / "art-D-sunrise.png", "stories/D-early-bird.png")
    feed_e(stories, "stories/E-affiliate-credit.png")

    for name in ("A-hook-no-permanent.png", "B-price-sm.png", "E-affiliate-credit.png"):
        cover(ROOT / "feed" / name, (1040, 1040)).save(ROOT / "line" / name, "PNG", optimize=True)
        print("wrote line/" + name)

    print("done polish")


if __name__ == "__main__":
    main()
