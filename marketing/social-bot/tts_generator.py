"""Generate Thai Text-to-Speech audio and synced SRT subtitles using edge-tts."""

from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

try:
    import edge_tts
    from edge_tts import SubMaker
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False


def prepare_thai_text_for_tts(text: str) -> str:
    """Prepare Thai text for TTS: fix pronunciation, strip emojis, and split into short lines."""
    # 1. Correct pronunciation of Sangkan Clean to สั่งการ คลีน
    text = text.replace("Sangkan Clean", "สั่งการ คลีน").replace("Sangkan", "สั่งการ")
    
    # 2. Strip emojis to avoid rendering issues
    text = re.sub(
        r'[\u2600-\u27BF]|[\u2000-\u32FF]|[\u2190-\u21FF]|[\u2b00-\u2bff]|[\u2c60-\u2c7f]|[\U0001f000-\U0001f9FF]',
        '',
        text
    )
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 3. Split into short lines (max 18 characters) to force separate SentenceBoundary events
    parts = re.split(r'([ \.\,\?\!\;])', text)
    lines = []
    current_line = ""
    for part in parts:
        if not part:
            continue
        
        # If the part itself is longer than 22 characters (e.g. no spaces in Thai), split it into sub-chunks of 18 characters
        if len(part) > 22:
            sub_parts = [part[i:i+18] for i in range(0, len(part), 18)]
            for sp in sub_parts:
                if len(current_line) + len(sp) > 22:
                    if current_line:
                        lines.append(current_line.strip())
                    lines.append(sp.strip())
                    current_line = ""
                else:
                    current_line += sp
        else:
            if len(current_line) + len(part) > 22:
                if current_line:
                    lines.append(current_line.strip())
                current_line = part
            else:
                current_line += part
            
    if current_line:
        lines.append(current_line.strip())
        
    return "\n".join(line for line in lines if line)


async def generate_tts_and_srt_async(
    text: str,
    out_mp3: Path,
    out_srt: Path,
    voice: str = "th-TH-PremwadeeNeural",
) -> bool:
    """Async generator for TTS audio and SRT subtitle files."""
    if not HAS_EDGE_TTS:
        print("WARNING: edge-tts is not installed. Skipping TTS generation.")
        return False

    out_mp3 = Path(out_mp3)
    out_srt = Path(out_srt)
    out_mp3.parent.mkdir(parents=True, exist_ok=True)

    cleaned_text = prepare_thai_text_for_tts(text)
    # Slow down rate slightly (-6%) to sound more natural and less robotic/rushed
    communicate = edge_tts.Communicate(cleaned_text, voice, rate="-6%")
    submaker = SubMaker()

    with out_mp3.open("wb") as fh:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] in ["WordBoundary", "SentenceBoundary"]:
                submaker.feed(chunk)

    # Save subtitles with leading '>' characters stripped
    srt_content = submaker.get_srt()
    srt_content = re.sub(r'^>\s*', '', srt_content, flags=re.MULTILINE)
    out_srt.write_text(srt_content, encoding="utf-8")
    print(f"Generated TTS: {out_mp3.name} and SRT: {out_srt.name}")
    return True


def split_long_srt_lines(srt_content: str, max_chars: int = 22) -> str:
    """Split long subtitle lines in SRT format to prevent overflow."""
    blocks = srt_content.strip().split("\n\n")
    new_blocks = []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 3:
            new_blocks.append(block)
            continue
        idx = lines[0]
        timing = lines[1]
        text_lines = lines[2:]
        new_text_lines = []
        for line in text_lines:
            if len(line) > max_chars:
                parts = line.split(" ")
                current = ""
                for part in parts:
                    if len(current) + len(part) > max_chars:
                        if current:
                            new_text_lines.append(current.strip())
                        current = part
                    else:
                        current += (" " if current else "") + part
                if current:
                    new_text_lines.append(current.strip())
            else:
                new_text_lines.append(line)
        new_blocks.append(f"{idx}\n{timing}\n" + "\n".join(new_text_lines))
    return "\n\n".join(new_blocks) + "\n\n"


def generate_openai_tts_and_srt(
    text: str,
    out_mp3: Path,
    out_srt: Path,
    api_key: str,
    voice: str = "nova",
) -> bool:
    """Generate TTS and SRT using OpenAI's TTS and Whisper APIs."""
    import requests
    try:
        out_mp3 = Path(out_mp3)
        out_srt = Path(out_srt)
        out_mp3.parent.mkdir(parents=True, exist_ok=True)

        # 1. Correct pronunciation of Sangkan Clean to สั่งการ คลีน
        text = text.replace("Sangkan Clean", "สั่งการ คลีน").replace("Sangkan", "สั่งการ")

        # 2. Call OpenAI TTS
        tts_url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice
        }

        print(f"Calling OpenAI TTS (voice={voice})...")
        response = requests.post(tts_url, json=data, headers=headers)
        if response.status_code != 200:
            print(f"OpenAI TTS API Error ({response.status_code}): {response.text}")
            return False

        with out_mp3.open("wb") as f:
            f.write(response.content)

        # 3. Call OpenAI Whisper to transcribe audio into SRT
        transcribe_url = "https://api.openai.com/v1/audio/transcriptions"
        headers_whisper = {
            "Authorization": f"Bearer {api_key}"
        }

        print("Calling OpenAI Whisper for SRT generation...")
        with out_mp3.open("rb") as audio_file:
            files = {
                "file": (out_mp3.name, audio_file, "audio/mpeg"),
            }
            form_data = {
                "model": "whisper-1",
                "response_format": "srt",
                "language": "th"
            }
            response_whisper = requests.post(
                transcribe_url,
                headers=headers_whisper,
                files=files,
                data=form_data
            )

        if response_whisper.status_code != 200:
            print(f"OpenAI Whisper API Error ({response_whisper.status_code}): {response_whisper.text}")
            return False

        srt_content = response_whisper.text
        # Strip any leading '>' characters from subtitle text blocks
        srt_content = re.sub(r'^>\s*', '', srt_content, flags=re.MULTILINE)
        
        # Split any long lines to prevent overflow
        srt_content = split_long_srt_lines(srt_content)
        
        out_srt.write_text(srt_content, encoding="utf-8")
        print(f"Generated OpenAI TTS: {out_mp3.name} and Whisper SRT: {out_srt.name}")
        return True
    except Exception as e:
        print(f"ERROR in OpenAI TTS/Whisper: {e}")
        return False


def generate_tts_and_srt(
    text: str,
    out_mp3: Path,
    out_srt: Path,
    voice: str = "th-TH-PremwadeeNeural",
) -> bool:
    """Wrapper generating TTS and SRT files, routing to OpenAI if API key is present."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        # Determine voice (default to nova, onyx for male edge voice, or load from env)
        openai_voice = os.environ.get("OPENAI_TTS_VOICE")
        if not openai_voice:
            # Simple mapping if edge voice was male
            openai_voice = "onyx" if "Niwat" in voice else "nova"
        return generate_openai_tts_and_srt(text, out_mp3, out_srt, api_key, voice=openai_voice)

    # Fallback to Edge-TTS
    try:
        return asyncio.run(generate_tts_and_srt_async(text, out_mp3, out_srt, voice))
    except Exception as e:
        print(f"ERROR: Failed to generate Edge-TTS: {e}")
        return False


def get_srt_duration(srt_path: Path, default: float = 10.0) -> float:
    """Parse the generated SRT to find the total duration of the voiceover."""
    srt_path = Path(srt_path)
    if not srt_path.exists():
        return default
    try:
        content = srt_path.read_text(encoding="utf-8").strip()
        # Find all timestamps like 00:00:05,230 --> 00:00:07,450
        matches = re.findall(
            r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})",
            content,
        )
        if matches:
            last = matches[-1]
            h, m, s, ms = int(last[4]), int(last[5]), int(last[6]), int(last[7])
            duration = h * 3600 + m * 60 + s + ms / 1000.0
            # Pad with 1.0s buffer so the video doesn't cut off instantly
            return max(duration + 1.0, default)
    except Exception as e:
        print(f"Error parsing SRT duration: {e}")
    return default
