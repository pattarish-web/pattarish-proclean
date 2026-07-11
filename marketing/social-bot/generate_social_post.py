"""Daily social content orchestrator — image + short video mix."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
for p in (str(ROOT), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from compose_image import save_feed, save_stories  # noqa: E402
from render_video import (  # noqa: E402
    has_ffmpeg,
    render_feed_clip,
    render_stories_clip,
)
from topics import pick_topic  # noqa: E402

LOG_PATH = ROOT / "log.json"
OUT_DIR = ROOT / "out"

SITE = "https://www.sangkanclean.com"
LINE_OA = "@sangkanclean"
PHONE = "063-686-5134"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _channels() -> set[str]:
    raw = os.environ.get("CHANNELS", "facebook,instagram,tiktok,line").strip()
    return {c.strip().lower() for c in raw.split(",") if c.strip()}


def _load_log() -> dict:
    if not LOG_PATH.exists():
        return {"last_topic": None, "posts": []}
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_topic": None, "posts": []}


def _save_log(data: dict) -> None:
    LOG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _fallback_captions(topic: dict) -> dict:
    hl = topic["headline"]
    angle = topic["angle"]
    cta = f"ทัก LINE {LINE_OA} หรือดูรายละเอียดที่ {SITE}"
    return {
        "fb_ig": (
            f"{hl}\n\n{angle}\n\n"
            f"Sangkan Clean — คลีนออฟฟิศให้ทีมวัยใหม่ เอเจนซี่ และเทค\n"
            f"{cta}\nโทร {PHONE}"
        ),
        "tiktok": f"{hl}\n{angle}\nLINE {LINE_OA}",
        "line": f"{hl}\n\n{angle}\n\nทักไลน์ {LINE_OA} ได้เลย",
        "image_subline": angle[:36],
        "hashtags": ["#SangkanClean", "#แม่บ้านออฟฟิศ", "#BigCleaning"],
    }


def _generate_captions(topic: dict) -> dict:
    try:
        from gemini_api import call_gemini_json, get_api_keys
    except ImportError:
        return _fallback_captions(topic)

    keys = get_api_keys()
    if not keys:
        print("No GEMINI_API_KEY — using fallback captions")
        return _fallback_captions(topic)

    prompt = f"""คุณเขียนคอนเทนต์โซเชียลภาษาไทยให้แบรนด์ Sangkan Clean (สั่งการคลีน)
โทน: สบายๆ มั่นใจ แม่นยำ — คุยกับทีมวัยใหม่ / เอเจนซี่ / สตาร์ทอัพ
ห้ามสำนวนราชการ ห้ามขายแข็ง ห้ามยาวเยิ่น
emoji ได้ไม่เกิน 1 ตัว และห้ามใส่ hashtag ในเนื้อหาหลัก

หัวข้อวันนี้: {topic["label"]}
มุม: {topic["angle"]}
หัวข้อกราฟิก: {topic["headline"]}
CTA ที่ต้องมี: LINE {LINE_OA} และเว็บ {SITE}
โทรศัพท์ (ใส่ได้ถ้าเหมาะสม): {PHONE}

คืน JSON เท่านั้น:
{{
  "fb_ig": "แคปชัน Facebook/Instagram ภาษาไทย 60-140 คำ มี CTA",
  "tiktok": "แคปชัน TikTok สั้น 30-70 คำ",
  "line": "ข้อความ LINE broadcast 40-100 คำ",
  "image_subline": "ประโยครองใต้หัวข้อบนกราฟิก ภาษาไทย สั้นมาก ไม่เกิน 36 ตัวอักษร",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
}}
"""
    data = call_gemini_json(keys[0], prompt, key_label="social-bot")
    if not data or not isinstance(data, dict):
        print("Gemini failed — using fallback captions")
        return _fallback_captions(topic)

    base = _fallback_captions(topic)
    for key in ("fb_ig", "tiktok", "line", "image_subline", "hashtags"):
        if key in data and data[key]:
            base[key] = data[key]
    if isinstance(base.get("image_subline"), str):
        base["image_subline"] = base["image_subline"][:36]
    return base


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


# Scene one-liners only — shared Instagram lifestyle brief is in _background_prompt.
SCENE_BY_TOPIC: dict[str, str] = {
    "office_ondemand": (
        "open Bangkok coworking floor, young professionals working casually at desks, "
        "floor-to-ceiling windows, indoor plants"
    ),
    "agency_focus": (
        "creative agency studio with soft moodboard wall, tidy open plan, "
        "casual-smart team collaborating in soft focus"
    ),
    "tech_team": (
        "bright startup office with clean desks and monitors, "
        "energetic but uncluttered, glass meeting room soft background"
    ),
    "big_cleaning": (
        "freshly deep-cleaned modern office after hours, polished floors catching daylight, "
        "subtle cleaning tools softly blurred in background"
    ),
    "maid_backup": (
        "bright clean office interior with a discreet professional cleaning cart "
        "softly out of focus — not a stiff utility room"
    ),
    "service_area": (
        "airy Bangkok office interior with soft city light through windows, "
        "clean desks and plants in foreground"
    ),
    "price_pack": (
        "premium small home-office / boutique agency desk lifestyle shot, "
        "notebook plant morning light, left third kept simple"
    ),
    "affiliate": (
        "two young colleagues chatting casually in a café-style office lounge, "
        "friendly daylight, clean modern space"
    ),
    "after_construction": (
        "newly finished bright commercial space being detailed, "
        "dust cleanup nearly done, airy unfinished-to-clean transition"
    ),
    "soft_cleaning": (
        "gentle daily tidy of a modern condo living area / soft surfaces, "
        "microfiber cloths subtle, calm natural light"
    ),
}


def _background_prompt(topic: dict) -> str:
    scene = SCENE_BY_TOPIC.get(
        topic["id"],
        "modern Bangkok coworking office, young professionals, bright airy lifestyle photo",
    )
    return (
        "Commercial lifestyle photography for Instagram ads, 1080x1080 square. "
        "Gen-Z / young startup agency vibe — bright, airy, energetic, not corporate stiff. "
        "Color palette cues in set dressing only: teal (#0d9488), coral/pink accents, "
        "soft yellow accents, clean whites. "
        "Leave clear negative space on the LEFT third for Thai text overlay "
        "(no text, letters, logos, watermarks, or UI in the image). "
        "Photorealistic, shallow depth of field, natural daylight, "
        "modern Bangkok office / cowork aesthetic. "
        "Young East/Southeast Asian professionals, casual-smart attire. "
        "Indoor plants, clean desks, no cluttered UI mockups. "
        f"Topic mood: {topic.get('label', topic['id'])}. "
        f"Scene: {scene}."
    )


def _generate_background(topic: dict, out_dir: Path) -> Path | None:
    """Generate a fresh bg via Gemini; return path or None on failure."""
    try:
        from gemini_api import call_gemini_image, get_api_keys
    except ImportError:
        print("gemini_api unavailable — gradient fallback for background")
        return None

    keys = get_api_keys()
    if not keys:
        print("No GEMINI_API_KEY — gradient fallback for background")
        return None

    prompt = _background_prompt(topic)
    raw = None
    for i, key in enumerate(keys):
        label = f"social-bot-bg-{i + 1}"
        raw = call_gemini_image(key, prompt, key_label=label)
        if raw:
            break
        print(f"Gemini image failed on key {i + 1}/{len(keys)}")

    if not raw:
        print("Gemini image failed on all keys — gradient fallback for background")
        return None

    ext = "png" if raw[:8].startswith(b"\x89PNG") else "jpg"
    path = out_dir / f"bg.{ext}"
    path.write_bytes(raw)
    print(f"Background saved → {path.name} ({len(raw)} bytes)")
    return path


def build_assets(topic: dict, captions: dict) -> dict[str, str]:
    """Create PNG (+ MP4 as needed). Returns relative paths under social-bot/."""
    day = _stamp()
    out = OUT_DIR / day
    out.mkdir(parents=True, exist_ok=True)

    headline = topic["headline"]
    sub = str(captions.get("image_subline") or topic["angle"])[:36]

    bg_path = _generate_background(topic, out)

    feed_png = out / "feed.png"
    stories_png = out / "stories.png"
    save_feed(headline, sub, feed_png, topic_id=topic["id"], background=bg_path)
    save_stories(headline, sub, stories_png, topic_id=topic["id"], background=bg_path)

    assets: dict[str, str] = {
        "feed_png": str(feed_png.relative_to(ROOT)).replace("\\", "/"),
        "stories_png": str(stories_png.relative_to(ROOT)).replace("\\", "/"),
    }
    if bg_path and bg_path.exists():
        assets["bg"] = str(bg_path.relative_to(ROOT)).replace("\\", "/")

    fmt = topic.get("format", "image")
    need_stories_video = True  # TikTok always
    need_feed_video = fmt == "video"

    if (need_stories_video or need_feed_video) and not has_ffmpeg():
        print("WARNING: ffmpeg not found — skipping video render")
        return assets

    if need_stories_video:
        stories_mp4 = out / "stories.mp4"
        render_stories_clip(stories_png, stories_mp4, duration=10.0)
        assets["stories_mp4"] = str(stories_mp4.relative_to(ROOT)).replace("\\", "/")

    if need_feed_video:
        feed_mp4 = out / "feed.mp4"
        render_feed_clip(feed_png, feed_mp4, duration=10.0)
        assets["feed_mp4"] = str(feed_mp4.relative_to(ROOT)).replace("\\", "/")

    return assets


def publish_all(
    topic: dict,
    captions: dict,
    assets: dict[str, str],
    channels: set[str],
    dry_run: bool,
) -> dict[str, dict]:
    results: dict[str, dict] = {}
    fmt = topic.get("format", "image")
    tags = captions.get("hashtags") or []
    tag_str = " ".join(tags) if isinstance(tags, list) else str(tags)

    fb_caption = f"{captions['fb_ig']}\n\n{tag_str}".strip()
    tt_caption = f"{captions['tiktok']}\n\n{tag_str}".strip()

    def abs_asset(key: str) -> Path | None:
        rel = assets.get(key)
        if not rel:
            return None
        return ROOT / rel

    if "facebook" in channels:
        from publish_meta import publish_facebook

        results["facebook"] = publish_facebook(
            caption=fb_caption,
            image_path=abs_asset("feed_png"),
            video_path=abs_asset("feed_mp4") if fmt == "video" else None,
            dry_run=dry_run,
        )

    if "instagram" in channels:
        from publish_meta import publish_instagram

        results["instagram"] = publish_instagram(
            caption=fb_caption,
            image_path=abs_asset("feed_png"),
            video_path=abs_asset("stories_mp4") if fmt == "video" else None,
            use_reels=fmt == "video",
            dry_run=dry_run,
        )

    if "tiktok" in channels:
        from publish_tiktok import publish_tiktok

        results["tiktok"] = publish_tiktok(
            caption=tt_caption,
            video_path=abs_asset("stories_mp4"),
            dry_run=dry_run,
        )

    if "line" in channels:
        from publish_line import publish_line

        results["line"] = publish_line(
            text=captions["line"],
            image_path=abs_asset("feed_png"),
            headline=topic["headline"],
            dry_run=dry_run,
        )

    return results


def main() -> int:
    dry_run = _env_bool("DRY_RUN", default=False)
    channels = _channels()
    log = _load_log()
    topic = pick_topic(log.get("last_topic"))
    fmt = topic.get("format", "image")

    print(f"Topic: {topic['id']} ({fmt}) dry_run={dry_run} channels={sorted(channels)}")

    captions = _generate_captions(topic)
    assets = build_assets(topic, captions)
    print("Assets:", json.dumps(assets, ensure_ascii=False))

    results = publish_all(topic, captions, assets, channels, dry_run)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "topic_id": topic["id"],
        "format": fmt,
        "dry_run": dry_run,
        "assets": assets,
        "captions": {
            "fb_ig": captions.get("fb_ig", "")[:200],
            "tiktok": captions.get("tiktok", "")[:120],
            "line": captions.get("line", "")[:120],
        },
        "results": results,
    }
    posts = log.get("posts") or []
    posts.append(entry)
    log["posts"] = posts[-60:]  # keep last ~2 months
    log["last_topic"] = topic["id"]
    _save_log(log)

    # Also dump full captions for dry-run review
    if dry_run:
        day = _stamp()
        cap_path = OUT_DIR / day / "captions.json"
        cap_path.write_text(
            json.dumps(captions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {cap_path}")

    print("Results:", json.dumps(results, ensure_ascii=False))
    failed = [
        name
        for name, res in results.items()
        if not res.get("ok") and not dry_run and res.get("skipped") is not True
    ]
    if failed:
        print("Publish failures:", failed)
        for name in failed:
            print(f"  {name}: {json.dumps(results.get(name), ensure_ascii=False)}")
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
