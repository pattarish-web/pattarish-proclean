"""Art-directed brochure ads: premium photo + minimal typography."""

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
    fill = TEAL if on_dark else TEAL
    write(draw, (x, y), "Sangkan Office", fnt(22, "semibold"), fill)
    draw.rectangle([x, y + 30, x + 48, y + 33], fill=AMBER if on_dark else TEAL)


def small_cta(draw, x, y, text, dark_bg=True):
    font = fnt(20, "semibold")
    w, h = tw(draw, text, font)
    pad_x, pad_y = 18, 10
    # Quiet print label, not a loud app button
    if dark_bg:
        draw.rectangle([x, y, x + w + pad_x * 2, y + h + pad_y * 2], fill=WHITE)
        write(draw, (x + pad_x, y + pad_y - 1), text, font, DARK)
    else:
        draw.rectangle([x, y, x + w + pad_x * 2, y + h + pad_y * 2], fill=TEAL)
        write(draw, (x + pad_x, y + pad_y - 1), text, font, WHITE)
    return y + h + pad_y * 2


# ── A: editorial cover — one idea ─────────────────────────


def creative_a(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw)

    # Single powerful statement, bottom-left breathing room
    y = int(h * 0.58)
    for line in ("ไม่ต้องจ้าง", "แม่บ้านประจำ"):
        font = fnt(56, "bold")
        write(draw, (48, y), line, font, WHITE, shadow=True)
        y += 64
    y += 10
    write(draw, (48, y), "เรียกใช้ได้ตามต้องการ · อุดมสุข", fnt(22, "medium"), SOFT, shadow=True)
    y += 44
    small_cta(draw, 48, y, "LINE @sangkanclean")
    save(img, rel)


# ── B: printed rate card on desk ───────────────────────────


def creative_b(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size

    # Brand tiny top-left on photo edge
    brand_mark(draw, 40, 36, on_dark=True)

    # Typeset onto the blank cream paper of the mockup (approx center-left page)
    # Paper region roughly: x 80–520, y 180–780 on 1080 square (tuned)
    px, py = int(w * 0.10), int(h * 0.20)
    paper_w = int(w * 0.42)

    write(draw, (px, py), "Sangkan Office", fnt(16, "semibold"), TEAL)
    write(draw, (px, py + 36), "แม่บ้านออฟฟิศ", fnt(28, "bold"), INK)
    write(draw, (px, py + 72), "On-Demand", fnt(22, "medium"), MUTED_LT)
    draw.rectangle([px, py + 110, px + 64, py + 113], fill=TEAL)

    # Two prices — clean print columns
    y = py + 140
    write(draw, (px, y), "S", fnt(18, "semibold"), TEAL)
    write(draw, (px, y + 28), "฿2,900", fnt(36, "bold"), INK)
    write(draw, (px, y + 74), "4 ครั้ง / เดือน", fnt(16, "regular"), MUTED_LT)

    write(draw, (px + int(paper_w * 0.48), y), "M", fnt(18, "semibold"), TEAL)
    write(draw, (px + int(paper_w * 0.48), y + 22), "แนะนำ", fnt(14, "semibold"), AMBER)
    write(draw, (px + int(paper_w * 0.48), y + 44), "฿6,900", fnt(36, "bold"), INK)
    write(draw, (px + int(paper_w * 0.48), y + 90), "8 ครั้ง / เดือน", fnt(16, "regular"), MUTED_LT)

    y2 = y + 140
    draw.rectangle([px, y2, px + paper_w - 20, y2 + 1], fill=(203, 213, 225))
    write(
        draw,
        (px, y2 + 16),
        "ชวนเพื่อนในโซน · เครดิตคืน 10%",
        fnt(14, "medium"),
        MUTED_LT,
    )
    write(draw, (px, y2 + 42), "สะสมถึงสิ้นปี · ใช้จนกว่าจะหมด", fnt(13, "regular"), MUTED_LT)

    small_cta(draw, px, y2 + 78, "เลือกแพ็คใน LINE", dark_bg=False)
    save(img, rel)


# ── C: cinematic trust ────────────────────────────────────


def creative_c(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw)

    y = int(h * 0.62)
    write(draw, (48, y), "เช็คอิน GPS", fnt(44, "bold"), WHITE, shadow=True)
    y += 54
    write(draw, (48, y), "ส่งรูปก่อน–หลัง", fnt(44, "bold"), WHITE, shadow=True)
    y += 58
    write(draw, (48, y), "เริ่ม ฿2,900/เดือน · ไม่ต้องมีผู้จัดการ", fnt(20, "medium"), SOFT, shadow=True)
    y += 42
    small_cta(draw, 48, y, "ดูแพ็ค S / M")
    save(img, rel)


# ── D: early bird sunrise ─────────────────────────────────


def creative_d(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw, on_dark=True)

    # Right-side editorial block in negative space
    x = int(w * 0.48)
    y = int(h * 0.28)
    write(draw, (x, y), "EARLY BIRD", fnt(16, "semibold"), AMBER, shadow=True)
    y += 36
    write(draw, (x, y), "ล็อกสัญญา", fnt(48, "bold"), WHITE, shadow=True)
    y += 58
    write(draw, (x, y), "เริ่มเดือนหน้า", fnt(48, "bold"), WHITE, shadow=True)
    y += 64
    write(draw, (x, y), "อุดมสุข–บางนา · S / M", fnt(20, "medium"), SOFT, shadow=True)
    y += 44
    small_cta(draw, x, y, "จองผ่าน LINE")
    save(img, rel)


# ── E: referral corridor ──────────────────────────────────


def creative_e(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand_mark(draw)

    # Centered on the lit wall — sparse, poster-like
    lines = [
        ("ชวนเพื่อนในโซน", fnt(36, "bold"), WHITE),
        ("เครดิตคืน 10%", fnt(52, "bold"), AMBER),
        ("สะสมถึงสิ้นปี · ใช้จนกว่าจะหมด", fnt(18, "medium"), SOFT),
    ]
    y = int(h * 0.38)
    for text, font, color in lines:
        ww, hh = tw(draw, text, font)
        write(draw, ((w - ww) // 2, y), text, font, color, shadow=True)
        y += hh + 18

    y += 12
    # Centered quiet CTA
    font = fnt(20, "semibold")
    text = "ขอโค้ดที่ LINE"
    ww, hh = tw(draw, text, font)
    x = (w - ww) // 2 - 18
    draw.rectangle([x, y, x + ww + 36, y + hh + 20], fill=WHITE)
    write(draw, (x + 18, y + 8), text, font, DARK)
    save(img, rel)


def main():
    feed = (1080, 1080)
    stories = (1080, 1920)

    creative_a(feed, ART / "art-A-editorial.png", "feed/A-hook-no-permanent.png")
    creative_b(feed, ART / "art-B-print-mockup.png", "feed/B-price-sm.png")
    creative_c(feed, ART / "art-C-cinematic.png", "feed/C-trust-gps.png")
    creative_d(feed, ART / "art-D-sunrise.png", "feed/D-early-bird.png")
    creative_e(feed, ART / "art-E-corridor.png", "feed/E-affiliate-credit.png")

    # Stories: same art, taller crop — keep typography scale readable
    creative_a(stories, ART / "art-A-editorial.png", "stories/A-hook-no-permanent.png")
    creative_b(stories, ART / "art-B-print-mockup.png", "stories/B-price-sm.png")
    creative_d(stories, ART / "art-D-sunrise.png", "stories/D-early-bird.png")
    creative_e(stories, ART / "art-E-corridor.png", "stories/E-affiliate-credit.png")

    for name in ("A-hook-no-permanent.png", "B-price-sm.png", "E-affiliate-credit.png"):
        cover(ROOT / "feed" / name, (1040, 1040)).save(ROOT / "line" / name, "PNG", optimize=True)
        print("wrote line/" + name)

    print("done art-directed set")


if __name__ == "__main__":
    main()
