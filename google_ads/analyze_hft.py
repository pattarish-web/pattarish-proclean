"""
Analyze exported HFT ads data and produce SangkanClean campaign recommendations.

Usage:
  python google_ads/analyze_hft.py google_ads/exports/hft_YYYYMMDD_HHMMSS
  python google_ads/analyze_hft.py google_ads/exports/hft_YYYYMMDD_HHMMSS --openai
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from google_ads.config import ANALYSIS_DIR


def load_export(export_dir: Path) -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {}
    for json_file in sorted(export_dir.glob("*.json")):
        if json_file.name == "manifest.json":
            continue
        data[json_file.stem] = json.loads(json_file.read_text(encoding="utf-8"))
    return data


def _micros_to_thb(micros: Any) -> float:
    try:
        return round(int(micros) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def summarize(data: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    campaigns = data.get("campaigns_all_time", data.get("campaigns_30d", []))
    keywords = data.get("keywords_30d", [])
    search_terms = data.get("search_terms_30d", [])

    campaign_rows = []
    for row in campaigns:
        camp = row.get("campaign", {})
        metrics = row.get("metrics", {})
        budget = row.get("campaign_budget", {})
        campaign_rows.append(
            {
                "name": camp.get("name"),
                "status": camp.get("status"),
                "channel": camp.get("advertising_channel_type"),
                "bidding": camp.get("bidding_strategy_type"),
                "daily_budget_thb": _micros_to_thb(budget.get("amount_micros")),
                "impressions": metrics.get("impressions", 0),
                "clicks": metrics.get("clicks", 0),
                "cost_thb": _micros_to_thb(metrics.get("cost_micros")),
                "conversions": metrics.get("conversions", 0),
                "cpa_thb": _micros_to_thb(metrics.get("cost_per_conversion")),
            }
        )

    top_keywords = []
    for row in sorted(
        keywords,
        key=lambda r: float(r.get("metrics", {}).get("cost_micros") or 0),
        reverse=True,
    )[:30]:
        crit = row.get("ad_group_criterion", {}).get("keyword", {})
        metrics = row.get("metrics", {})
        top_keywords.append(
            {
                "keyword": crit.get("text"),
                "match_type": crit.get("match_type"),
                "quality_score": row.get("ad_group_criterion", {}).get("quality_info", {}).get("quality_score"),
                "clicks": metrics.get("clicks", 0),
                "cost_thb": _micros_to_thb(metrics.get("cost_micros")),
                "conversions": metrics.get("conversions", 0),
            }
        )

    top_search_terms = []
    for row in sorted(
        search_terms,
        key=lambda r: float(r.get("metrics", {}).get("impressions") or 0),
        reverse=True,
    )[:30]:
        st = row.get("search_term_view", {})
        metrics = row.get("metrics", {})
        top_search_terms.append(
            {
                "search_term": st.get("search_term"),
                "status": st.get("status"),
                "impressions": metrics.get("impressions", 0),
                "clicks": metrics.get("clicks", 0),
                "cost_thb": _micros_to_thb(metrics.get("cost_micros")),
                "conversions": metrics.get("conversions", 0),
            }
        )

    return {
        "campaigns": campaign_rows,
        "top_keywords_by_spend": top_keywords,
        "top_search_terms_by_impressions": top_search_terms,
    }


def build_prompt(summary: dict[str, Any]) -> str:
    return f"""คุณเป็นผู้เชี่ยวชาญ Google Ads สำหรับธุรกิจทำความสะอาดในไทย (Big Cleaning, แม่บ้าน, ออฟฟิศ)

วิเคราะห์ข้อมูลประวัติการยิง ads จากบัญชี HFT (ธุรกิจเดียวกับ SangkanClean) แล้วออกแบบแคมเปญ Search สำหรับ SangkanClean

ข้อมูลสรุปจาก HFT:
{json.dumps(summary, ensure_ascii=False, indent=2)}

ให้ตอบเป็นภาษาไทย โครงสร้างดังนี้:
1. สรุปสิ่งที่ HFT ทำได้ดี / ไม่ดี
2. โครงสร้างแคมเปญแนะนำสำหรับ SangkanClean (ชื่อแคมเปญ, งบ/วัน, กลยุทธ์เสนอราคา)
3. คีย์เวิร์ดหลัก 20 คำ (พร้อม match type)
4. Negative keywords 15 คำ
5. ตัวอย่าง RSA headline 10 ข้อ + description 4 ข้อ
6. Landing page ที่ควรใช้ (เช่น landing-bigcleaning.html)
7. ขั้นตอนเปิดใช้งาน 7 วันแรก
"""


def maybe_openai(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a Google Ads strategist for Thai cleaning services."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return f"[OpenAI error: {exc}]"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze HFT export for SangkanClean")
    parser.add_argument("export_dir", type=Path, help="Path to export folder")
    parser.add_argument("--openai", action="store_true", help="Send summary to OpenAI")
    args = parser.parse_args()

    if not args.export_dir.exists():
        raise SystemExit(f"Export folder not found: {args.export_dir}")

    data = load_export(args.export_dir)
    summary = summarize(data)
    prompt = build_prompt(summary)

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = args.export_dir.name.replace("hft_", "")
    summary_path = ANALYSIS_DIR / f"summary_{stamp}.json"
    prompt_path = ANALYSIS_DIR / f"prompt_{stamp}.md"

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"Summary: {summary_path}")
    print(f"Prompt:  {prompt_path}")

    if args.openai:
        result = maybe_openai(prompt)
        if result:
            out = ANALYSIS_DIR / f"recommendations_{stamp}.md"
            out.write_text(result, encoding="utf-8")
            print(f"AI report: {out}")
        else:
            print("Set OPENAI_API_KEY in .env to generate AI recommendations.")


if __name__ == "__main__":
    main()
