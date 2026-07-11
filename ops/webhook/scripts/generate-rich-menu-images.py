#!/usr/bin/env python3
"""Generate branded Rich Menu PNGs (2500x1686) with Thai labels + icons."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2] / "modules"
W, H = 2500, 1686
TEAL = (13, 148, 136)
TEAL_DARK = (15, 118, 110)
BG = (15, 23, 42)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
LINE = (30, 41, 59)

FONT_PATHS = [
    Path(r"C:\Windows\Fonts\LeelawUI.ttf"),
    Path(r"C:\Windows\Fonts\leelawad.ttf"),
    Path(r"C:\Windows\Fonts\tahomabd.ttf"),
    Path(r"C:\Windows\Fonts\tahoma.ttf"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in FONT_PATHS:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def draw_icon(draw: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, color=WHITE):
    s = 54
    if kind == "package":
        draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s // 3], radius=12, outline=color, width=6)
        draw.line([(cx - s, cy - s // 3), (cx + s, cy - s // 3)], fill=color, width=6)
        draw.line([(cx, cy - s), (cx, cy + s // 3)], fill=color, width=6)
    elif kind == "book":
        draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=14, outline=color, width=6)
        draw.line([(cx - s // 2, cy - 10), (cx + s // 2, cy - 10)], fill=color, width=6)
        draw.line([(cx - s // 2, cy + 16), (cx + s // 3, cy + 16)], fill=color, width=6)
    elif kind == "queue":
        for i, dy in enumerate((-40, 0, 40)):
            draw.ellipse([cx - 50, cy + dy - 14, cx - 22, cy + dy + 14], outline=color, width=5)
            draw.line([(cx - 10, cy + dy), (cx + 50, cy + dy)], fill=color, width=6)
    elif kind == "camera":
        draw.rounded_rectangle([cx - s, cy - 34, cx + s, cy + 42], radius=14, outline=color, width=6)
        draw.ellipse([cx - 28, cy - 14, cx + 28, cy + 42], outline=color, width=6)
        draw.rectangle([cx + 18, cy - 52, cx + 48, cy - 34], outline=color, width=5)
    elif kind == "share":
        pts = [(cx - 40, cy + 30), (cx, cy - 50), (cx + 40, cy + 30)]
        draw.line([pts[0], pts[1], pts[2]], fill=color, width=6)
        for px, py in pts:
            draw.ellipse([px - 14, py - 14, px + 14, py + 14], outline=color, width=5)
    elif kind == "help":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=6)
        draw.arc([cx - 28, cy - 36, cx + 28, cy + 8], start=200, end=0, fill=color, width=6)
        draw.ellipse([cx - 7, cy + 28, cx + 7, cy + 42], fill=color)
    elif kind == "checkin":
        draw.ellipse([cx - 20, cy - 55, cx + 20, cy - 15], outline=color, width=6)
        draw.polygon([(cx, cy + 55), (cx - 42, cy - 5), (cx + 42, cy - 5)], outline=color)
        draw.line([(cx - 42, cy - 5), (cx, cy + 55), (cx + 42, cy - 5)], fill=color, width=6)
    elif kind == "issue":
        draw.polygon([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)], outline=color)
        draw.line([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s), (cx, cy - s)], fill=color, width=6)
        draw.line([(cx, cy - 18), (cx, cy + 18)], fill=color, width=6)
        draw.ellipse([cx - 6, cy + 28, cx + 6, cy + 40], fill=color)
    elif kind == "guide":
        draw.rounded_rectangle([cx - 48, cy - s, cx + 48, cy + s], radius=10, outline=color, width=6)
        for dy in (-28, 0, 28):
            draw.line([(cx - 28, cy + dy), (cx + 28, cy + dy)], fill=color, width=5)
    elif kind == "money":
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=6)
        draw.text((cx, cy), "฿", fill=color, font=load_font(70), anchor="mm")
    elif kind == "today":
        draw.rounded_rectangle([cx - s, cy - 48, cx + s, cy + 52], radius=12, outline=color, width=6)
        draw.line([(cx - s, cy - 18), (cx + s, cy - 18)], fill=color, width=6)
        draw.line([(cx - 28, cy - 62), (cx - 28, cy - 38)], fill=color, width=6)
        draw.line([(cx + 28, cy - 62), (cx + 28, cy - 38)], fill=color, width=6)
        for i in range(2):
            for j in range(3):
                x = cx - 30 + j * 30
                y = cy + i * 30
                draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=color)
    elif kind == "warning":
        draw.polygon([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)], outline=color)
        draw.line([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s), (cx, cy - s)], fill=color, width=6)
        draw.line([(cx, cy - 10), (cx, cy + 22)], fill=color, width=7)
        draw.ellipse([cx - 7, cy + 32, cx + 7, cy + 46], fill=color)
    elif kind == "user":
        draw.ellipse([cx - 28, cy - 55, cx + 28, cy - 5], outline=color, width=6)
        draw.arc([cx - 55, cy + 5, cx + 55, cy + 70], start=200, end=340, fill=color, width=6)
    elif kind == "staff":
        draw.ellipse([cx - 28, cy - 50, cx + 28, cy], outline=color, width=6)
        draw.rounded_rectangle([cx - 50, cy + 8, cx + 50, cy + 55], radius=18, outline=color, width=6)
    elif kind == "bell":
        draw.arc([cx - 40, cy - 40, cx + 40, cy + 30], start=200, end=340, fill=color, width=6)
        draw.line([(cx - 40, cy + 10), (cx + 40, cy + 10)], fill=color, width=6)
        draw.ellipse([cx - 10, cy + 28, cx + 10, cy + 48], outline=color, width=5)
    else:
        draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=color, width=6)


ICON_BY_ITEM = {
    "packages": "package",
    "book": "book",
    "next_job": "queue",
    "pow": "camera",
    "affiliate": "share",
    "help": "help",
    "today": "today",
    "checkin": "checkin",
    "issue": "issue",
    "guide": "guide",
    "threshold": "money",
    "warning": "warning",
    "new_customers": "user",
    "staff": "staff",
    "test_warn": "bell",
}


def cell_bg(i: int) -> tuple[int, int, int]:
    return TEAL if i % 2 == 0 else TEAL_DARK


def wrap_label(label: str) -> list[str]:
    if len(label) <= 8:
        return [label]
    if " " in label:
        parts = label.split(" ", 1)
        return [parts[0], parts[1]]
    if len(label) > 12:
        return [label[:8], label[8:]]
    return [label]


def render_menu(role: str) -> Path:
    meta = json.loads((ROOT / role / "rich-menu.json").read_text(encoding="utf-8"))
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    title_font = load_font(72 if role == "staff" else 56)
    sub_font = load_font(56 if role == "staff" else 42)

    for i, area in enumerate(meta["areas"]):
        b = area["bounds"]
        x0, y0, w, h = b["x"], b["y"], b["width"], b["height"]
        x1, y1 = x0 + w - 1, y0 + h - 1
        pad = 18
        draw.rounded_rectangle(
            [x0 + pad, y0 + pad, x1 - pad, y1 - pad],
            radius=36,
            fill=cell_bg(i),
            outline=LINE,
            width=4,
        )
        data = area["action"].get("data", "")
        item = ""
        for part in data.split("&"):
            if part.startswith("item="):
                item = part.split("=", 1)[1]
        label = area["action"].get("displayText", item)
        cx = x0 + w // 2
        cy = y0 + int(h * 0.38)
        draw_icon(draw, ICON_BY_ITEM.get(item, "help"), cx, cy)

        lines = wrap_label(label)
        text_y = y0 + int(h * 0.72)
        for li, line in enumerate(lines):
            font = title_font if len(lines) == 1 else sub_font
            draw.text((cx, text_y + li * 58), line, fill=WHITE, font=font, anchor="mm")

    out = ROOT / role / "rich-menu.png"
    img.save(out, format="PNG", optimize=True)
    return out


def main():
    for role in ("customer", "staff", "admin"):
        out = render_menu(role)
        print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
