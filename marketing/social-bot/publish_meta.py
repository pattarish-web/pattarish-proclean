"""Publish to Facebook Page + Instagram via Meta Graph API."""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests

GRAPH = "https://graph.facebook.com/v21.0"


def _token() -> str:
    return os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()


def _page_id() -> str:
    return os.environ.get("FACEBOOK_PAGE_ID", "").strip()


def _ig_id() -> str:
    return os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "").strip()


def _graph_error(resp: requests.Response) -> str:
    try:
        payload = resp.json()
        err = payload.get("error") or payload
        if isinstance(err, dict):
            code = err.get("code")
            sub = err.get("error_subcode")
            msg = err.get("message") or resp.text[:300]
            return f"HTTP {resp.status_code} code={code} sub={sub} msg={msg}"
        return f"HTTP {resp.status_code}: {resp.text[:400]}"
    except Exception:
        return f"HTTP {resp.status_code}: {resp.text[:400]}"


def _post_photo(page_id: str, token: str, caption: str, image_path: Path) -> dict:
    with image_path.open("rb") as fh:
        r = requests.post(
            f"{GRAPH}/{page_id}/photos",
            data={"caption": caption, "access_token": token, "published": "true"},
            files={"source": ("feed.png", fh, "image/png")},
            timeout=120,
        )
    if r.status_code >= 400:
        return {"ok": False, "mode": "photo", "error": _graph_error(r)}
    data = r.json()
    return {"ok": True, "mode": "photo", "id": data.get("id") or data.get("post_id")}


def _post_video(page_id: str, token: str, caption: str, video_path: Path) -> dict:
    with video_path.open("rb") as fh:
        r = requests.post(
            f"{GRAPH}/{page_id}/videos",
            data={
                "description": caption,
                "access_token": token,
                "published": "true",
            },
            files={"source": ("feed.mp4", fh, "video/mp4")},
            timeout=180,
        )
    if r.status_code >= 400:
        return {"ok": False, "mode": "video", "error": _graph_error(r)}
    data = r.json()
    return {"ok": True, "mode": "video", "id": data.get("id")}


def publish_facebook(
    *,
    caption: str,
    image_path: Path | None,
    video_path: Path | None = None,
    dry_run: bool = False,
) -> dict:
    page_id = _page_id()
    token = _token()
    if dry_run:
        mode = "video" if video_path and video_path.exists() else "photo"
        return {
            "ok": True,
            "dry_run": True,
            "mode": mode,
            "page_id": page_id or None,
        }
    if not page_id or not token:
        return {"ok": False, "skipped": True, "reason": "missing FACEBOOK_PAGE_ID or token"}

    # Quick auth probe (no secret printed)
    try:
        who = requests.get(
            f"{GRAPH}/me",
            params={"fields": "id,name", "access_token": token},
            timeout=30,
        )
        if who.status_code >= 400:
            return {"ok": False, "error": f"token invalid: {_graph_error(who)}"}
        print(f"Facebook token ok as: {who.json()}")
    except Exception as exc:
        return {"ok": False, "error": f"token probe failed: {exc}"}

    # Prefer video when provided; fall back to photo so the day still posts.
    if video_path and video_path.exists():
        video_result = _post_video(page_id, token, caption, video_path)
        if video_result.get("ok"):
            return video_result
        print(f"Facebook video failed → {video_result.get('error')}; trying photo")
        if image_path and image_path.exists():
            photo_result = _post_photo(page_id, token, caption, image_path)
            if photo_result.get("ok"):
                photo_result["video_error"] = video_result.get("error")
                return photo_result
            return {
                "ok": False,
                "error": photo_result.get("error"),
                "video_error": video_result.get("error"),
            }
        return video_result

    if not image_path or not image_path.exists():
        return {"ok": False, "reason": "missing feed image"}
    return _post_photo(page_id, token, caption, image_path)


def _ig_publish_container(ig_user_id: str, token: str, creation_id: str) -> dict:
    # Poll until finished
    for _ in range(30):
        st = requests.get(
            f"{GRAPH}/{creation_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        st.raise_for_status()
        code = (st.json() or {}).get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            return {"ok": False, "error": f"IG container error: {st.json()}"}
        time.sleep(2)

    pub = requests.post(
        f"{GRAPH}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
        timeout=60,
    )
    pub.raise_for_status()
    return {"ok": True, "id": pub.json().get("id")}


def publish_instagram(
    *,
    caption: str,
    image_path: Path | None,
    video_path: Path | None = None,
    use_reels: bool = False,
    dry_run: bool = False,
) -> dict:
    """IG Content Publishing needs a publicly reachable media URL.

    Set SOCIAL_ASSET_BASE_URL to a CDN/raw GitHub URL prefix that serves
    marketing/social-bot/out/... files, OR set SOCIAL_FEED_IMAGE_URL /
    SOCIAL_REELS_VIDEO_URL for an explicit override.
    """
    ig_id = _ig_id()
    token = _token()
    if dry_run:
        mode = "reels" if use_reels and video_path else "image"
        return {"ok": True, "dry_run": True, "mode": mode, "ig_id": ig_id or None}
    if not ig_id or not token:
        return {
            "ok": False,
            "skipped": True,
            "reason": "missing INSTAGRAM_BUSINESS_ACCOUNT_ID or token",
        }

    base = os.environ.get("SOCIAL_ASSET_BASE_URL", "").rstrip("/")
    override_img = os.environ.get("SOCIAL_FEED_IMAGE_URL", "").strip()
    override_vid = os.environ.get("SOCIAL_REELS_VIDEO_URL", "").strip()

    try:
        if use_reels and video_path and video_path.exists():
            video_url = override_vid
            if not video_url and base:
                # Expect assets relative like out/YYYYMMDD/stories.mp4
                rel = str(video_path).replace("\\", "/")
                idx = rel.find("out/")
                if idx >= 0:
                    video_url = f"{base}/{rel[idx:]}"
            if not video_url:
                return {
                    "ok": False,
                    "skipped": True,
                    "reason": "IG Reels need public video URL (SOCIAL_ASSET_BASE_URL)",
                }
            create = requests.post(
                f"{GRAPH}/{ig_id}/media",
                data={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "access_token": token,
                },
                timeout=60,
            )
            create.raise_for_status()
            creation_id = create.json().get("id")
            result = _ig_publish_container(ig_id, token, creation_id)
            result["mode"] = "reels"
            return result

        image_url = override_img
        if not image_url and base and image_path:
            rel = str(image_path).replace("\\", "/")
            idx = rel.find("out/")
            if idx >= 0:
                image_url = f"{base}/{rel[idx:]}"
        if not image_url:
            return {
                "ok": False,
                "skipped": True,
                "reason": "IG image needs public URL (SOCIAL_ASSET_BASE_URL)",
            }
        create = requests.post(
            f"{GRAPH}/{ig_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": token,
            },
            timeout=60,
        )
        create.raise_for_status()
        creation_id = create.json().get("id")
        result = _ig_publish_container(ig_id, token, creation_id)
        result["mode"] = "image"
        return result
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
