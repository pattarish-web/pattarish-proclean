import sys
import asyncio
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from tts_generator import generate_tts_and_srt, get_srt_duration
from render_video import render_reels_video_with_audio_and_subs

text = (
    "รู้ไหมคะว่า ตึกสะอาด เริ่มจากทุกออฟฟิศ? "
    "เพื่อสุขภาพ และ ความสะอาด ของออฟฟิศ สั่งการ คลีน. "
    "หากใคร กำลัง เจอปัญหานี้ อยู่ ทักไลน์ แอด สั่งการ คลีน ได้เลยค่ะ"
)

voices = {
    "premwadee": "th-TH-PremwadeeNeural",
    "achara": "th-TH-AcharaNeural",
    "niwat": "th-TH-NiwatNeural"
}

out_dir = ROOT / "out" / "voice_tests"
out_dir.mkdir(parents=True, exist_ok=True)

png_path = ROOT / "out" / "20260720" / "stories.png"
if not png_path.exists():
    png_path = next(ROOT.glob("out/**/*.png"), None)

if not png_path:
    print("ERROR: stories.png not found. Please run generate_social_post.py first to create frames.")
    sys.exit(1)

print(f"Using image source: {png_path}")

for name, voice_id in voices.items():
    print(f"Generating for voice: {name} ({voice_id})...")
    mp3_path = out_dir / f"{name}.mp3"
    srt_path = out_dir / f"{name}.srt"
    mp4_path = out_dir / f"test_{name}.mp4"
    
    ok = generate_tts_and_srt(text, mp3_path, srt_path, voice=voice_id)
    if not ok:
        print(f"Failed to generate TTS/SRT for {name}")
        continue
        
    duration = get_srt_duration(srt_path, default=10.0)
    
    render_reels_video_with_audio_and_subs(
        png_path=png_path,
        audio_path=mp3_path,
        srt_path=srt_path,
        mp4_path=mp4_path,
        duration=duration
    )
    print(f"Rendered: {mp4_path}")

print("All done! Voice tests generated in out/voice_tests/")
