import json
import os
import threading
import time

import requests

from geo_log import log

# July 2026: gemini-pro / gemini-2.0-* are shut down. Use current models on v1beta.
DEFAULT_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash",
]

_limiter_lock = threading.Lock()
_key_locks: dict[str, threading.Lock] = {}
_key_last_call: dict[str, float] = {}


def _min_interval() -> float:
    return float(os.environ.get("GEMINI_MIN_INTERVAL", "6"))


def wait_for_key(api_key: str) -> None:
    """Per-key throttle so parallel workers don't burst the same project quota."""
    with _limiter_lock:
        if api_key not in _key_locks:
            _key_locks[api_key] = threading.Lock()
            _key_last_call[api_key] = 0.0
        key_lock = _key_locks[api_key]

    with key_lock:
        now = time.monotonic()
        wait = _min_interval() - (now - _key_last_call[api_key])
        if wait > 0:
            time.sleep(wait)
        _key_last_call[api_key] = time.monotonic()


def get_models():
    override = os.environ.get("GEMINI_MODEL", "").strip()
    if override:
        return [override]
    return DEFAULT_MODELS


def build_generate_content_url(model: str, api_key: str) -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )


def _retry_wait(response: requests.Response | None, attempt: int, base_delay: float) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after), base_delay)
            except ValueError:
                pass
    return base_delay * (2**attempt)


def call_gemini_json(
    api_key: str,
    prompt: str,
    *,
    key_label: str = "",
    max_retries: int = 6,
    base_delay: float = 8,
    timeout: int = 60,
) -> dict | None:
    tag = key_label or f"{api_key[:8]}…"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    for model in get_models():
        url = build_generate_content_url(model, api_key)
        for attempt in range(max_retries):
            try:
                wait_for_key(api_key)
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)

                if response.status_code == 404:
                    log(
                        f"{tag} model '{model}' → 404 not found ({response.text[:120]})",
                        level="WARN",
                    )
                    break

                if response.status_code == 429 or (
                    response.status_code == 400 and "RESOURCE_EXHAUSTED" in response.text
                ):
                    wait_time = _retry_wait(response, attempt, base_delay)
                    log(
                        f"{tag} RATE LIMIT (429) → wait {wait_time:.0f}s "
                        f"[retry {attempt + 1}/{max_retries}]",
                        level="WARN",
                    )
                    time.sleep(wait_time)
                    continue

                if response.status_code != 200:
                    log(f"{tag} API error {response.status_code}: {response.text[:200]}", level="WARN")
                    if attempt < max_retries - 1:
                        wait_time = _retry_wait(response, attempt, base_delay)
                        log(f"{tag} retry in {wait_time:.0f}s")
                        time.sleep(wait_time)
                        continue
                    break

                result_json = response.json()
                text_response = result_json["candidates"][0]["content"]["parts"][0]["text"]
                log(f"{tag} model '{model}' → success")
                return json.loads(text_response)

            except requests.Timeout:
                log(f"{tag} timeout ({attempt + 1}/{max_retries})", level="WARN")
                if attempt < max_retries - 1:
                    time.sleep(base_delay)
            except Exception as exc:
                if attempt == max_retries - 1:
                    log(f"{tag} failed after {max_retries} retries: {exc}", level="ERROR")
                    break
                wait_time = base_delay * (2**attempt)
                log(f"{tag} error: {exc} → retry in {wait_time:.0f}s", level="WARN")
                time.sleep(wait_time)

    log(f"{tag} all models exhausted — giving up", level="ERROR")
