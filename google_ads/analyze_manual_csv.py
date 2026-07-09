"""Analyze manual Google Ads CSV exports from Thai UI."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ADS_DIR = Path(r"C:\Users\HygieneTH\OneDrive\เดสก์ท็อป\ADS")
OUT_DIR = Path(__file__).resolve().parent / "analysis"


def parse_thai_csv(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    # Skip title rows until header row found
    start = 0
    for i, line in enumerate(lines):
        if "," in line and not line.startswith("รายงาน") and not line.startswith("ตั้งแต่"):
            start = i
            break
    reader = csv.DictReader(lines[start:])
    return [row for row in reader if row.get(next(iter(row), ""), "").strip()]


def num(val: str) -> float:
    if not val or val.strip() in ("--", "-", ""):
        return 0.0
    val = val.replace(",", "").replace("฿", "").replace("%", "").strip()
    try:
        return float(val)
    except ValueError:
        return 0.0


def analyze_campaigns(rows: list[dict]) -> list[dict]:
    results = []
    for r in rows:
        name = r.get("แคมเปญ", "")
        if not name or name.startswith("ทั้งหมด"):
            continue
        results.append({
            "name": name,
            "status": r.get("สถานะ", ""),
            "type": r.get("ประเภทแคมเปญ", ""),
            "budget": num(r.get("งบประมาณ", "")),
            "cost": num(r.get("ค่าใช้จ่าย", "")),
            "clicks": int(num(r.get("คลิก", ""))),
            "impressions": int(num(r.get("การแสดงผล", ""))),
            "conversions": num(r.get("Conversion", "")),
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "cpc": num(r.get("CPC เฉลี่ย", "")),
            "conv_rate": num(r.get("อัตรา Conv.", "")),
            "bidding": r.get("ประเภทกลยุทธ์การเสนอราคา", ""),
        })
    return sorted(results, key=lambda x: x["cost"], reverse=True)


def analyze_search_terms(rows: list[dict]) -> dict:
    terms = []
    for r in rows:
        term = r.get("ข้อความค้นหา", "").strip()
        if not term or term.startswith("ทั้งหมด"):
            continue
        cost = num(r.get("ค่าใช้จ่าย", ""))
        clicks = int(num(r.get("คลิก", "")))
        conv = num(r.get("Conversion", ""))
        terms.append({
            "term": term,
            "campaign": r.get("แคมเปญ", ""),
            "keyword": r.get("คีย์เวิร์ด", ""),
            "match": r.get("ประเภทการทำงานของคีย์เวิร์ด", ""),
            "cost": cost,
            "clicks": clicks,
            "conversions": conv,
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "cpc": num(r.get("CPC เฉลี่ย", "")),
            "added": r.get("เพิ่ม/ยกเว้น", ""),
        })

    with_conv = [t for t in terms if t["conversions"] > 0]
    high_spend_no_conv = sorted(
        [t for t in terms if t["conversions"] == 0 and t["cost"] > 100],
        key=lambda x: x["cost"], reverse=True,
    )
    top_conv = sorted(with_conv, key=lambda x: x["conversions"], reverse=True)[:30]
    top_spend = sorted(terms, key=lambda x: x["cost"], reverse=True)[:30]

    return {
        "total_terms": len(terms),
        "terms_with_conversions": len(with_conv),
        "top_by_conversions": top_conv,
        "top_by_spend": top_spend,
        "wasted_spend": high_spend_no_conv[:20],
        "total_wasted": sum(t["cost"] for t in high_spend_no_conv),
    }


def analyze_keywords(rows: list[dict]) -> dict:
    kws = []
    for r in rows:
        kw = r.get("คีย์เวิร์ด", "").strip().strip('"')
        if not kw or kw.startswith("ทั้งหมด"):
            continue
        cost = num(r.get("ค่าใช้จ่าย", ""))
        clicks = int(num(r.get("คลิก", "")))
        conv = num(r.get("Conversion", ""))
        if cost == 0 and clicks == 0:
            continue
        kws.append({
            "keyword": kw,
            "match": r.get("ประเภทการทำงานของคีย์เวิร์ด", ""),
            "campaign": r.get("แคมเปญ", ""),
            "cost": cost,
            "clicks": clicks,
            "conversions": conv,
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "cpc": num(r.get("CPC เฉลี่ย", "")),
            "quality": r.get("คะแนนคุณภาพ", ""),
            "ctr": num(r.get("CTR", "")),
        })

    top_cost = sorted(kws, key=lambda x: x["cost"], reverse=True)[:30]
    top_conv = sorted([k for k in kws if k["conversions"] > 0], key=lambda x: x["conversions"], reverse=True)[:20]
    low_qs = [k for k in kws if k["quality"] in ("ต่ำกว่าค่าเฉลี่ย", "แย่") and k["cost"] > 50]

    return {"top_by_cost": top_cost, "top_by_conversions": top_conv, "low_quality": low_qs[:15]}


def analyze_ads(rows: list[dict]) -> list[dict]:
    ads = []
    for r in rows:
        camp = r.get("แคมเปญ", "")
        if not camp or camp.startswith("ทั้งหมด"):
            continue
        headlines = [r.get(f"บรรทัดแรก {i}", "") for i in range(1, 16) if r.get(f"บรรทัดแรก {i}", "")]
        descs = [r.get(f"คำอธิบาย {i}", "") for i in range(1, 6) if r.get(f"คำอธิบาย {i}", "")]
        ads.append({
            "campaign": camp,
            "ad_group": r.get("กลุ่มโฆษณา", ""),
            "status": r.get("สถานะ", ""),
            "url": r.get("URL สุดท้าย", ""),
            "headlines": headlines,
            "descriptions": descs,
            "cost": num(r.get("ค่าใช้จ่าย", "")),
            "clicks": int(num(r.get("คลิก", ""))),
            "conversions": num(r.get("Conversion", "")),
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "quality": r.get("คุณภาพของโฆษณา", ""),
        })
    return sorted(ads, key=lambda x: x["cost"], reverse=True)


def build_recommendations(campaigns, search_terms, keywords, ads) -> dict:
    # Focus on Search campaigns with good performance
    search_camps = [c for c in campaigns if c["type"] == "การค้นหา" and c["cost"] > 1000]

    big_clean = [c for c in search_camps if "big clean" in c["name"].lower() or "bigclean" in c["name"].lower()]
    maid = [c for c in search_camps if "แม่บ้าน" in c["name"]]

    # Best performing search terms for Big Clean
    bc_terms = [t for t in search_terms["top_by_conversions"]
                if "big clean" in t["campaign"].lower() or "bigclean" in t["campaign"].lower()]

    # Best keywords for Big Clean
    bc_kws = [k for k in keywords["top_by_cost"]
              if "big clean" in k["campaign"].lower()]

    # Winning ads
    winning_ads = [a for a in ads if a["conversions"] > 5 and a["cost"] > 1000]

    return {
        "priority_campaigns": [
            {
                "name": "SangKanClean - Big Clean Search",
                "type": "Search",
                "daily_budget_thb": 800,
                "bidding": "Target CPA ฿200-250",
                "rationale": "Big Clean Search มี CPA ~฿242, conv rate 16% — แคมเปญที่ทำกำไรดีที่สุด",
                "source_campaigns": [c["name"] for c in big_clean],
            },
            {
                "name": "SangKanClean - แม่บ้านประจำ Search",
                "type": "Search",
                "daily_budget_thb": 500,
                "bidding": "Target CPA ฿200",
                "rationale": "แม่บ้านประจำ เก่า CPA ฿193 ดีกว่าแคมเปญใหม่ (CPA ฿2,366) — ใช้โครงสร้างจากแคมเปญเก่า",
                "source_campaigns": [c["name"] for c in maid if "เก่า" in c["name"] or c["status"] == "มีสิทธิ์"],
            },
        ],
        "recommended_keywords": {
            "big_clean_phrase": [
                k["keyword"] for k in bc_kws[:15] if k["conversions"] > 0
            ],
            "big_clean_from_search_terms": [
                t["term"] for t in bc_terms[:15]
            ],
            "maid_phrase": [
                k["keyword"] for k in keywords["top_by_conversions"]
                if "แม่บ้าน" in k["campaign"] and k["conversions"] > 0
            ][:15],
        },
        "negative_keywords": [
            t["term"] for t in search_terms["wasted_spend"][:15]
        ],
        "winning_ad_copy": [
            {
                "campaign": a["campaign"],
                "headlines": a["headlines"][:5],
                "descriptions": a["descriptions"][:3],
                "cpa": a["cpa"],
                "conversions": a["conversions"],
            }
            for a in winning_ads[:5]
        ],
        "avoid": {
            "campaigns": [c["name"] for c in campaigns if c["type"] == "ดิสเพลย์"],
            "reason": "Display/GDN CPA สูงมาก (฿306-450) conv rate ต่ำ — ไม่แนะนำสำหรับ SangkanClean ช่วงแรก",
            "wasted_search_spend": f"฿{search_terms['total_wasted']:,.0f} จาก search terms ที่ไม่ convert",
        },
    }


def main():
    campaigns = analyze_campaigns(parse_thai_csv(ADS_DIR / "แคมเปญ.csv"))
    search_terms = analyze_search_terms(parse_thai_csv(ADS_DIR / "รายงานข้อความค้นหา.csv"))
    keywords = analyze_keywords(parse_thai_csv(ADS_DIR / "คีย์เวิร์ด.csv"))
    ads = analyze_ads(parse_thai_csv(ADS_DIR / "รายงานโฆษณา.csv"))
    recs = build_recommendations(campaigns, search_terms, keywords, ads)

    report = {
        "summary": {
            "total_spend_thb": sum(c["cost"] for c in campaigns),
            "total_conversions": sum(c["conversions"] for c in campaigns),
            "avg_cpa": round(sum(c["cost"] for c in campaigns) / max(sum(c["conversions"] for c in campaigns), 1), 2),
            "search_spend": sum(c["cost"] for c in campaigns if c["type"] == "การค้นหา"),
            "search_conversions": sum(c["conversions"] for c in campaigns if c["type"] == "การค้นหา"),
        },
        "campaigns": campaigns,
        "search_terms": search_terms,
        "keywords": keywords,
        "ads": ads,
        "recommendations": recs,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "sangkanclean_recommendations.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    return report


if __name__ == "__main__":
    r = main()
    s = r["summary"]
    print(f"\n=== HFT SUMMARY ===")
    print(f"Spend: ฿{s['total_spend_thb']:,.0f} | Conv: {s['total_conversions']:.0f} | CPA: ฿{s['avg_cpa']:.0f}")
    print(f"Search only: ฿{s['search_spend']:,.0f} | {s['search_conversions']:.0f} conv")

    print(f"\n=== TOP CAMPAIGNS ===")
    for c in r["campaigns"][:6]:
        if c["type"] == "การค้นหา":
            print(f"  {c['name']}: ฿{c['cost']:,.0f} | {c['conversions']:.0f} conv | CPA ฿{c['cpa']:.0f} | {c['status']}")

    print(f"\n=== TOP SEARCH TERMS (by conversions) ===")
    for t in r["search_terms"]["top_by_conversions"][:10]:
        print(f"  \"{t['term']}\" | {t['campaign']} | {t['conversions']:.0f} conv | ฿{t['cost']:,.0f}")

    print(f"\n=== WASTED SPEND (no conversion, >฿100) ===")
    for t in r["search_terms"]["wasted_spend"][:8]:
        print(f"  \"{t['term']}\" | ฿{t['cost']:,.0f} | {t['clicks']} clicks | 0 conv")

    print(f"\n=== RECOMMENDATIONS ===")
    for camp in r["recommendations"]["priority_campaigns"]:
        print(f"\n  [{camp['name']}]")
        print(f"  Budget: ฿{camp['daily_budget_thb']}/day | {camp['bidding']}")
        print(f"  {camp['rationale']}")

    kws = r["recommendations"]["recommended_keywords"]
    print(f"\n  Big Clean keywords ({len(kws['big_clean_phrase'])} winners):")
    for kw in kws["big_clean_phrase"][:8]:
        print(f"    - {kw}")

    print(f"\n  Negative keywords ({len(r['recommendations']['negative_keywords'])}):")
    for nk in r["recommendations"]["negative_keywords"][:8]:
        print(f"    - {nk}")
