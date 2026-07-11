"""Generate Facebook Page cover + profile — agency/tech youth vibe."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
ADS = ROOT.parent / "ads-office-ondemand"
FONTS_DIR = ADS / "fonts"

TEAL = (13, 148, 136)
TEAL_BRIGHT = (20, 184, 166)
TEAL_DEEP = (15, 118, 110)
DARK = (15, 23, 42)
INK = (30, 41, 59)
WHITE = (255, 255, 255)
OFFWHITE = (248, 250, 252)
MUTED = (100, 116, 139)
AMBER = (245, 158, 11)
LINE = (226, 232, 240)

COVER_SIZE = (1640, 856)
PROFILE_SIZE = (800, 800)

_PROMPT = {
    "bold": FONTS_DIR / "Prompt-Bold.ttf",
    "semibold": FONTS_DIR / "Prompt-SemiBold.ttf",
    "medium": FONTS_DIR / "Prompt-Medium.ttf",
    "regular": FONTS_DIR / "Prompt-Regular.ttf",
}
_FALLBACK = [
    Path(r"C:\Windows\Fonts\LeelawUI.ttf"),
    Path(r"C:\Windows\Fonts\leelawdb.ttf"),
]


def _load(path: Path, size: int) -> ImageFont.ImageFont | None:
    if not path.exists():
        return None
    try:
        return ImageFont.truetype(str(path), size=size)
    except OSError:
        return None


def font(size: int, weight: str = "semibold") -> ImageFont.ImageFont:
    order = [weight, "semibold", "bold", "medium", "regular"]
    seen: set[str] = set()
    for key in order:
        if key in seen or key not in _PROMPT:
            continue
        seen.add(key)
        loaded = _load(_PROMPT[key], size)
        if loaded:
            return loaded
    for path in _FALLBACK:
        loaded = _load(path, size)
        if loaded:
            return loaded
    return ImageFont.load_default()


def text_wh(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def polish(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Sharpness(img).enhance(1.18)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    return img


def agency_cover_bg(size: tuple[int, int]) -> Image.Image:
    """Bright editorial canvas — agency/tech, not dark corporate."""
    w, h = size
    img = Image.new("RGB", size, OFFWHITE)
    draw = ImageDraw.Draw(img)

    # Soft cool wash left → slight teal hint right
    for x in range(0, w, 3):
        t = x / max(w - 1, 1)
        fill = (
            int(OFFWHITE[0] * (1 - t * 0.08) + 204 * t * 0.12),
            int(OFFWHITE[1] * (1 - t * 0.05) + 251 * t * 0.08),
            int(OFFWHITE[2] * (1 - t * 0.02) + 241 * t * 0.06),
        )
        draw.rectangle([x, 0, x + 3, h], fill=fill)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Bold teal diagonal panel on right
    od.polygon(
        [
            (int(w * 0.58), 0),
            (w, 0),
            (w, h),
            (int(w * 0.42), h),
        ],
        fill=(*TEAL, 255),
    )
    # Lighter teal slash overlay
    od.polygon(
        [
            (int(w * 0.78), 0),
            (w, 0),
            (w, h),
            (int(w * 0.62), h),
        ],
        fill=(*TEAL_BRIGHT, 90),
    )
    # White hairline on the cut
    od.line(
        [(int(w * 0.58), 0), (int(w * 0.42), h)],
        fill=(255, 255, 255, 200),
        width=2,
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Minimal mesh on teal side only
    mesh = Image.new("RGBA", size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mesh)
    for i in range(5):
        x = int(w * 0.62) + i * 64
        md.line([(x, 40), (x, h - 40)], fill=(255, 255, 255, 28), width=1)
    for i in range(4):
        y = 100 + i * 160
        md.line([(int(w * 0.55), y), (w - 40, y)], fill=(255, 255, 255, 22), width=1)
    # Corner ticks on teal
    md.line([(w - 48, 28), (w - 28, 28)], fill=(255, 255, 255, 200), width=2)
    md.line([(w - 28, 28), (w - 28, 48)], fill=(255, 255, 255, 200), width=2)

    return Image.alpha_composite(img.convert("RGBA"), mesh).convert("RGB")


def make_cover() -> Image.Image:
    img = agency_cover_bg(COVER_SIZE)
    draw = ImageDraw.Draw(img)
    w, h = COVER_SIZE
    x = 96
    y = int(h * 0.20)

    label_f = font(22, "semibold")
    draw.text((x, y), "OFFICE  ·  AGENCY  ·  TECH", fill=TEAL_DEEP, font=label_f)
    y += 46

    brand_f = font(78, "bold")
    draw.text((x, y), "Sangkan Clean", fill=DARK, font=brand_f)
    y += 96

    tag_f = font(40, "semibold")
    draw.text((x, y), "ออฟฟิศสะอาด พร้อมโฟกัสงาน", fill=INK, font=tag_f)
    y += 58

    sub_f = font(28, "medium")
    draw.text(
        (x, y),
        "แม่บ้าน On-Demand สำหรับเอเจนซี่และทีมเทค",
        fill=MUTED,
        font=sub_f,
    )
    y += 70

    url_f = font(26, "regular")
    url = "www.sangkanclean.com"
    draw.text((x, y), url, fill=MUTED, font=url_f)
    tw, _ = text_wh(draw, url, url_f)
    draw.rectangle([x, y + 38, x + tw, y + 41], fill=AMBER)

    # Thin bottom rail
    rail = Image.new("RGBA", COVER_SIZE, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rail)
    rd.rectangle([0, h - 5, w, h], fill=(*TEAL, 255))
    img = Image.alpha_composite(img.convert("RGBA"), rail).convert("RGB")
    return polish(img)


def make_profile() -> Image.Image:
    """Bright monogram — white field, teal SC, sharp frame."""
    w, h = PROFILE_SIZE
    img = Image.new("RGB", PROFILE_SIZE, OFFWHITE)
    draw = ImageDraw.Draw(img)

    # Teal rounded square fill
    pad = 56
    panel = Image.new("RGBA", PROFILE_SIZE, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle(
        [pad, pad, w - pad, h - pad],
        radius=52,
        fill=(*TEAL, 255),
    )
    img = Image.alpha_composite(img.convert("RGBA"), panel).convert("RGB")
    draw = ImageDraw.Draw(img)

    mono = font(168, "bold")
    sc = "SC"
    tw, th = text_wh(draw, sc, mono)
    draw.text(((w - tw) // 2, (h - th) // 2 - 36), sc, fill=WHITE, font=mono)

    name_f = font(34, "semibold")
    name = "Sangkan Clean"
    nw, _ = text_wh(draw, name, name_f)
    draw.text(((w - nw) // 2, (h - th) // 2 + th - 4), name, fill=(204, 251, 241), font=name_f)

    return polish(img)


def main() -> None:
    cover = make_cover()
    profile = make_profile()
    cover_path = ROOT / "cover.png"
    profile_path = ROOT / "profile.png"
    cover.save(cover_path, "PNG", optimize=True)
    profile.save(profile_path, "PNG", optimize=True)
    print("wrote", cover_path)
    print("wrote", profile_path)


if __name__ == "__main__":
    main()
