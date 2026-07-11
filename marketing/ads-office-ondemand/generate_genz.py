"""Gen-Z / young agency set — keep classic feed/ untouched."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "genz"
ART = OUT / "art"
FONTS = ROOT / "fonts"

TEAL = (13, 148, 136)
CORAL = (251, 113, 133)  # youthful accent
DARK = (15, 23, 42)
WHITE = (255, 255, 255)
SOFT = (241, 245, 249)
INK = (15, 23, 42)
YELLOW = (250, 204, 21)


def font(size: int, weight: str = "bold") -> ImageFont.ImageFont:
    names = {
        "bold": "Prompt-Bold.ttf",
        "semibold": "Prompt-SemiBold.ttf",
        "medium": "Prompt-Medium.ttf",
        "regular": "Prompt-Regular.ttf",
    }
    p = FONTS / names.get(weight, "Prompt-Bold.ttf")
    if p.exists():
        return ImageFont.truetype(str(p), size=size)
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


def tw(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def ink(draw, xy, text, f, fill=WHITE, shadow=True):
    x, y = xy
    if shadow:
        draw.text((x + 1, y + 2), text, font=f, fill=(0, 0, 0))
    draw.text((x, y), text, font=f, fill=fill)


def chip(draw, x, y, text, bg=CORAL, fg=DARK):
    f = font(24, "semibold")
    w, h = tw(draw, text, f)
    draw.rounded_rectangle([x, y, x + w + 36, y + h + 20], radius=22, fill=bg)
    draw.text((x + 18, y + 8), text, font=f, fill=fg)
    return y + h + 20


def cta(draw, x, y, text, bg=TEAL):
    f = font(28, "bold")
    w, h = tw(draw, text, f)
    draw.rounded_rectangle([x, y, x + w + 48, y + h + 28], radius=30, fill=bg)
    draw.text((x + 24, y + 12), text, font=f, fill=WHITE)
    return y + h + 28


def brand(draw, x=40, y=32):
    ink(draw, (x, y), "Sangkan Office", font(28, "semibold"), TEAL)
    draw.rounded_rectangle([x, y + 36, x + 72, y + 42], radius=3, fill=CORAL)


def save(img: Image.Image, rel: str):
    out = OUT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    ImageEnhance.Color(img).enhance(1.08).save(out, "PNG", optimize=True)
    print("wrote genz/" + rel)


def wash_bottom(img: Image.Image, start_ratio=0.55) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    start = int(h * start_ratio)
    for y in range(start, h):
        t = (y - start) / max(h - start, 1)
        d.line([(0, y), (w, y)], fill=(15, 23, 42, int(200 * t**1.3)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def creative_a(size, art, rel):
    img = wash_bottom(cover(art, size), 0.42)
    draw = ImageDraw.Draw(img)
    brand(draw)
    chip(draw, 40, 100, "สำหรับทีมวัยใหม่", CORAL, DARK)
    # Start higher — less empty air
    y = int(size[1] * 0.42)
    for line in ("เลิกจ้างประจำ", "ได้แล้ว"):
        ink(draw, (40, y), line, font(72, "bold"), WHITE)
        y += 82
    ink(draw, (40, y), "เรียกแม่บ้านออฟฟิศเมื่อไหร่ก็ได้ · อุดมสุข", font(26, "medium"), SOFT)
    y += 48
    cta(draw, 40, y, "ทัก LINE @sangkanclean")
    save(img, rel)


def creative_b(size, art, rel):
    img = cover(art, size)
    draw = ImageDraw.Draw(img)
    w, h = size
    brand(draw)

    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([24, 100, int(w * 0.66), h - 28], radius=28, fill=(255, 255, 255, 240))
    img = Image.alpha_composite(img.convert("RGBA"), panel).convert("RGB")
    draw = ImageDraw.Draw(img)

    x, y = 48, 128
    ink(draw, (x, y), "แพ็คง่ายๆ", font(24, "semibold"), CORAL, shadow=False)
    ink(draw, (x, y + 40), "ออฟฟิศ On-Demand", font(40, "bold"), INK, shadow=False)

    y = y + 110
    gap = 24
    card_w = (int(w * 0.66) - 48 - 48 - gap) // 2
    for i, (code, price, detail, hot) in enumerate([
        ("S", "฿2,900", "4 ครั้ง/เดือน", False),
        ("M", "฿6,900", "8 ครั้ง/เดือน", True),
    ]):
        bx = x + i * (card_w + gap)
        bg = (255, 241, 242) if hot else (240, 253, 250)
        draw.rounded_rectangle([bx, y, bx + card_w, y + 170], radius=22, fill=bg)
        if hot:
            chip(draw, bx + 12, y + 12, "ฮิต", YELLOW, DARK)
        ty = y + (52 if hot else 22)
        ink(draw, (bx + 18, ty), code, font(24, "semibold"), TEAL, shadow=False)
        ink(draw, (bx + 18, ty + 36), price, font(36, "bold"), INK, shadow=False)
        ink(draw, (bx + 18, ty + 86), detail, font(18, "medium"), (100, 116, 139), shadow=False)

    y = y + 200
    ink(draw, (x, y), "ชวนเพื่อนในโซน ได้เครดิตคืน 10%", font(20, "semibold"), INK, shadow=False)
    ink(draw, (x, y + 34), "สะสมถึงสิ้นปี · ใช้ได้จนกว่าจะหมด", font(18, "regular"), (100, 116, 139), shadow=False)
    cta(draw, x, y + 72, "เลือกแพ็คใน LINE", TEAL)
    save(img, rel)


def creative_c(size, art, rel):
    img = wash_bottom(cover(art, size), 0.40)
    draw = ImageDraw.Draw(img)
    brand(draw)
    chip(draw, 40, 100, "โปร่งใส 100%", YELLOW, DARK)
    y = int(size[1] * 0.44)
    ink(draw, (40, y), "เช็คอิน GPS", font(60, "bold"), WHITE)
    y += 72
    ink(draw, (40, y), "+ ส่งรูปก่อน–หลัง", font(48, "bold"), WHITE)
    y += 64
    ink(draw, (40, y), "ไม่ต้องมีผู้จัดการคุม · เริ่ม ฿2,900", font(24, "medium"), SOFT)
    y += 48
    cta(draw, 40, y, "ดูแพ็ค S / M")
    save(img, rel)


def creative_d(size, art, rel):
    img = wash_bottom(cover(art, size), 0.38)
    draw = ImageDraw.Draw(img)
    brand(draw)
    chip(draw, 40, 100, "EARLY BIRD", CORAL, DARK)
    y = int(size[1] * 0.40)
    ink(draw, (40, y), "จองก่อน", font(68, "bold"), WHITE)
    y += 78
    ink(draw, (40, y), "เริ่มเดือนหน้า", font(68, "bold"), WHITE)
    y += 80
    ink(draw, (40, y), "สิทธิ์จำกัด · อุดมสุข–บางนา · S/M", font(24, "medium"), SOFT)
    y += 48
    cta(draw, 40, y, "ทัก LINE จองเลย")
    save(img, rel)


def creative_e(size, art, rel):
    img = wash_bottom(cover(art, size), 0.40)
    draw = ImageDraw.Draw(img)
    h = size[1]
    brand(draw)
    chip(draw, 40, 100, "ชวนเพื่อน = ได้ตังค์คืน", YELLOW, DARK)

    y = int(h * 0.40)
    ink(draw, (40, y), "เครดิตคืน", font(48, "bold"), WHITE)
    y += 60
    ink(draw, (40, y), "10%", font(96, "bold"), CORAL)
    y += 108
    ink(draw, (40, y), "ของยอดที่เพื่อนจ่าย · สะสมถึงสิ้นปี", font(24, "medium"), SOFT)
    y += 40
    ink(draw, (40, y), "เครดิตไม่หมดอายุ ใช้จนกว่าจะหมด", font(24, "medium"), SOFT)
    y += 52
    cta(draw, 40, y, "ขอโค้ดที่ LINE")
    save(img, rel)


def main():
    feed = (1080, 1080)
    stories = (1080, 1920)

    creative_a(feed, ART / "genz-A-cowork.png", "feed/A-hook.png")
    creative_b(feed, ART / "genz-B-flatlay.png", "feed/B-price.png")
    creative_c(feed, ART / "genz-C-phone.png", "feed/C-trust.png")
    creative_d(feed, ART / "genz-D-morning.png", "feed/D-earlybird.png")
    creative_e(feed, ART / "genz-E-friends.png", "feed/E-affiliate.png")

    creative_a(stories, ART / "genz-A-cowork.png", "stories/A-hook.png")
    creative_b(stories, ART / "genz-B-flatlay.png", "stories/B-price.png")
    creative_d(stories, ART / "genz-D-morning.png", "stories/D-earlybird.png")
    creative_e(stories, ART / "genz-E-friends.png", "stories/E-affiliate.png")

    (OUT / "line").mkdir(parents=True, exist_ok=True)
    for name in ("A-hook.png", "B-price.png", "E-affiliate.png"):
        cover(OUT / "feed" / name, (1040, 1040)).save(OUT / "line" / name, "PNG", optimize=True)
        print("wrote genz/line/" + name)

    # README
    (OUT / "README.md").write_text(
        """# Gen-Z / เด็กเจนใหม่ — Ad Set

ชุดแยกจาก `feed/` หลัก (เก็บของเดิมไว้)

โทน: สด ชัด เข้ากับเอเจนซี่ / สตาร์ทอัพวัยรุ่น  
สี: teal + coral + yellow chip  
ข้อความ: สบายๆ แต่ยังขายแพ็ค S/M + affiliate เดิม

## ไฟล์

- `feed/` — A–E (1080×1080)
- `stories/` — A, B, D, E
- `line/` — A, B, E

## รีเจน

```bash
python marketing/ads-office-ondemand/generate_genz.py
```
""",
        encoding="utf-8",
    )
    print("done genz set")


if __name__ == "__main__":
    main()
