"""Install Gen-Z venue arts → blog JPGs + ad art pool, then render 100 ads."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[2]  # repo root if run from ads-office-ondemand... 
# Actually this file is in marketing/ads-office-ondemand/
ADS = Path(__file__).resolve().parent
REPO = ADS.parents[1]
ASSETS = Path(
    r"C:\Users\HygieneTH\.cursor\projects\c-Users-HygieneTH-gemini-antigravity-scratch-cleaning-seo-website\assets"
)

BLOG_DIR = REPO / "images" / "blog"
ART_DIR = ADS / "genz" / "batch" / "art"
FEED_DIR = ADS / "genz" / "batch" / "feed"
FONTS = ADS / "fonts"

# source asset → (blog jpg name, art key for ads)
MAP = [
    ("blog-office-genz.png", "blog-office.jpg", "art-office"),
    ("blog-factory-genz.png", "blog-factory.jpg", "art-factory"),
    ("blog-warehouse-genz.png", "blog-warehouse.jpg", "art-warehouse"),
    ("blog-hotel-genz.png", "blog-hotel.jpg", "art-hotel"),
    ("blog-hospital-genz.png", "blog-hospital.jpg", "art-hospital"),
    ("blog-school-genz.png", "blog-school.jpg", "art-school"),
    ("blog-mall-genz.png", "blog-mall.jpg", "art-mall"),
    ("blog-cafe-genz.png", "blog-restaurant.jpg", "art-cafe"),
    ("blog-showroom-genz.png", "blog-showroom.jpg", "art-showroom"),
    ("blog-highrise-genz.png", "blog-highrise.jpg", "art-highrise"),
    ("blog-gym-genz.png", "blog-gym.jpg", "art-gym"),
    ("blog-condo-genz.png", "blog-home.jpg", "art-condo"),
]

TEAL = (13, 148, 136)
CORAL = (251, 113, 133)
DARK = (15, 23, 42)
WHITE = (255, 255, 255)
SOFT = (241, 245, 249)
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
    f = font(22, "semibold")
    w, h = tw(draw, text, f)
    draw.rounded_rectangle([x, y, x + w + 32, y + h + 18], radius=20, fill=bg)
    draw.text((x + 16, y + 7), text, font=f, fill=fg)


def cta(draw, x, y, text):
    f = font(26, "bold")
    w, h = tw(draw, text, f)
    draw.rounded_rectangle([x, y, x + w + 44, y + h + 26], radius=28, fill=TEAL)
    draw.text((x + 22, y + 11), text, font=f, fill=WHITE)


def wash_bottom(img: Image.Image, start_ratio=0.42) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    start = int(h * start_ratio)
    for y in range(start, h):
        t = (y - start) / max(h - start, 1)
        d.line([(0, y), (w, y)], fill=(15, 23, 42, int(205 * t**1.25)))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def install_assets() -> dict[str, Path]:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    art_map: dict[str, Path] = {}

    # Base venue arts (+ blog JPG refresh)
    for src_name, blog_name, art_key in MAP:
        src = ASSETS / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        blog_img = cover(src, (1200, 675))
        blog_img = ImageEnhance.Color(blog_img).enhance(1.06)
        blog_path = BLOG_DIR / blog_name
        blog_img.save(blog_path, "JPEG", quality=88, optimize=True)
        print("blog", blog_path.name)

        art_path = ART_DIR / f"{art_key}.png"
        cover(src, (1080, 1080)).save(art_path, "PNG", optimize=True)
        art_map[art_key] = art_path
        print("art", art_path.name)

    # Extra diversity variants: art-*-v2.png / art-*-v3.png from assets
    for src in sorted(ASSETS.glob("art-*-v*.png")):
        key = src.stem  # e.g. art-office-v2
        art_path = ART_DIR / f"{key}.png"
        cover(src, (1080, 1080)).save(art_path, "PNG", optimize=True)
        art_map[key] = art_path
        print("art", art_path.name)

    print(f"art pool size: {len(art_map)}")
    return art_map


def render_one(item: dict, art_map: dict[str, Path], size=(1080, 1080)) -> Image.Image:
    art_key = item["art"]
    art_path = art_map.get(art_key) or ART_DIR / f"{art_key}.png"
    if not art_path.exists():
        art_path = art_map["art-office"]
    img = wash_bottom(cover(art_path, size), 0.40)
    draw = ImageDraw.Draw(img)
    # brand
    ink(draw, (40, 32), "Sangkan Clean", font(26, "semibold"), TEAL)
    draw.rounded_rectangle([40, 66, 112, 72], radius=3, fill=CORAL)

    chip(draw, 40, 96, item.get("chip", "Sangkan Clean"), CORAL, DARK)

    y = int(size[1] * 0.40)
    for line in item.get("headline", [])[:2]:
        # Fit long lines
        fsize = 64 if len(line) < 16 else 48 if len(line) < 24 else 36
        ink(draw, (40, y), line, font(fsize, "bold"), WHITE)
        y += int(fsize * 1.15)
    y += 8
    ink(draw, (40, y), item.get("sub", ""), font(22, "medium"), SOFT)
    y += 44
    cta(draw, 40, y, item.get("cta", "ทัก LINE @sangkanclean"))
    return ImageEnhance.Color(img).enhance(1.05)


def render_batch(art_map: dict[str, Path]) -> None:
    catalog_path = ADS / "genz" / "batch" / "catalog.json"
    if not catalog_path.exists():
        raise FileNotFoundError(catalog_path)
    items = json.loads(catalog_path.read_text(encoding="utf-8"))
    FEED_DIR.mkdir(parents=True, exist_ok=True)
    for i, item in enumerate(items, 1):
        out = FEED_DIR / f"{item['id']}.png"
        render_one(item, art_map).save(out, "PNG", optimize=True)
        if i % 20 == 0 or i == len(items):
            print(f"rendered {i}/{len(items)}")


def main() -> None:
    art_map = install_assets()
    # Ensure catalog exists
    cat = ADS / "genz" / "batch" / "catalog.json"
    if not cat.exists():
        import subprocess
        import sys

        subprocess.check_call([sys.executable, str(ADS / "build_ad_catalog.py")])
    render_batch(art_map)
    print("done: blog images +", len(list(FEED_DIR.glob('*.png'))), "ads")


if __name__ == "__main__":
    main()
