"""Deep comparison: Big Clean Search เก่า vs Big Clean Search."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ADS_DIR = Path(r"C:\Users\HygieneTH\OneDrive\เดสก์ท็อป\ADS")
OLD = "Big Clean Search เก่า"
NEW = "Big Clean Search"


def parse_csv(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = 0
    for i, line in enumerate(lines):
        if "," in line and not line.startswith("รายงาน") and not line.startswith("ตั้งแต่"):
            start = i
            break
    return list(csv.DictReader(lines[start:]))


def num(v: str) -> float:
    if not v or v.strip() in ("--", "-", ""):
        return 0.0
    try:
        return float(v.replace(",", "").replace("฿", "").replace("%", "").strip())
    except ValueError:
        return 0.0


def pct(v: str) -> str:
    n = num(v)
    return f"{n:.2f}%" if n else "--"


def filter_camp(rows: list[dict], camp_col: str, name: str) -> list[dict]:
    return [r for r in rows if r.get(camp_col, "").strip() == name]


def kw_stats(rows: list[dict]) -> dict:
    items = []
    for r in rows:
        kw = r.get("คีย์เวิร์ด", "").strip().strip('"')
        if not kw:
            continue
        cost = num(r.get("ค่าใช้จ่าย", ""))
        clicks = int(num(r.get("คลิก", "")))
        conv = num(r.get("Conversion", ""))
        imp = int(num(r.get("การแสดงผล", "")))
        if cost == 0 and clicks == 0 and conv == 0:
            continue
        items.append({
            "keyword": kw,
            "match": r.get("ประเภทการทำงานของคีย์เวิร์ด", ""),
            "cost": cost, "clicks": clicks, "conv": conv, "imp": imp,
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "cpc": num(r.get("CPC เฉลี่ย", "")),
            "ctr": num(r.get("CTR", "")),
            "qs": r.get("คะแนนคุณภาพ", ""),
            "status": r.get("สถานะ", ""),
        })
    total_cost = sum(i["cost"] for i in items)
    total_conv = sum(i["conv"] for i in items)
    total_clicks = sum(i["clicks"] for i in items)
    with_conv = [i for i in items if i["conv"] > 0]
    no_conv = [i for i in items if i["conv"] == 0 and i["cost"] > 0]
    qs_vals = [int(i["qs"]) for i in items if i["qs"] not in ("--", "", " ") and i["qs"].isdigit()]
    return {
        "count_active": len(items),
        "count_with_conv": len(with_conv),
        "count_no_conv_spend": len(no_conv),
        "total_cost": total_cost,
        "total_conv": total_conv,
        "total_clicks": total_clicks,
        "avg_cpa": total_cost / total_conv if total_conv else 0,
        "avg_cpc": total_cost / total_clicks if total_clicks else 0,
        "conv_rate": total_conv / total_clicks * 100 if total_clicks else 0,
        "avg_qs": sum(qs_vals) / len(qs_vals) if qs_vals else 0,
        "wasted": sum(i["cost"] for i in no_conv),
        "top_kw": sorted(items, key=lambda x: x["conv"], reverse=True)[:15],
        "worst_kw": sorted([i for i in items if i["conv"] == 0 and i["cost"] > 50],
                           key=lambda x: x["cost"], reverse=True)[:10],
        "expensive_kw": sorted(items, key=lambda x: x["cost"], reverse=True)[:10],
        "match_types": dict(defaultdict(float, {m: 0 for m in set(i["match"] for i in items)})),
    }


def st_stats(rows: list[dict]) -> dict:
    items = []
    for r in rows:
        term = r.get("ข้อความค้นหา", "").strip()
        if not term:
            continue
        cost = num(r.get("ค่าใช้จ่าย", ""))
        clicks = int(num(r.get("คลิก", "")))
        conv = num(r.get("Conversion", ""))
        items.append({
            "term": term, "cost": cost, "clicks": clicks, "conv": conv,
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "match": r.get("ประเภทการทำงานของคีย์เวิร์ด", ""),
            "keyword": r.get("คีย์เวิร์ด", ""),
        })
    total_conv = sum(i["conv"] for i in items)
    return {
        "count": len(items),
        "total_conv": total_conv,
        "top_terms": sorted(items, key=lambda x: x["conv"], reverse=True)[:15],
        "unique_terms": len(set(i["term"] for i in items)),
    }


def ad_stats(rows: list[dict]) -> dict:
    items = []
    for r in rows:
        headlines = [r.get(f"บรรทัดแรก {i}", "") for i in range(1, 16) if r.get(f"บรรทัดแรก {i}", "")]
        descs = [r.get(f"คำอธิบาย {i}", "") for i in range(1, 6) if r.get(f"คำอธิบาย {i}", "")]
        items.append({
            "headlines": headlines,
            "descriptions": descs,
            "url": r.get("URL สุดท้าย", ""),
            "status": r.get("สถานะ", ""),
            "quality": r.get("คุณภาพของโฆษณา", ""),
            "cost": num(r.get("ค่าใช้จ่าย", "")),
            "clicks": int(num(r.get("คลิก", ""))),
            "conv": num(r.get("Conversion", "")),
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "ctr": num(r.get("อัตราการโต้ตอบ", "")),
            "ad_group": r.get("กลุ่มโฆษณา", ""),
            "improvements": r.get("การปรับปรุงคุณภาพของโฆษณา", ""),
        })
    return {
        "count": len(items),
        "ads": sorted(items, key=lambda x: x["cost"], reverse=True),
        "total_cost": sum(i["cost"] for i in items),
        "total_conv": sum(i["conv"] for i in items),
    }


def ag_stats(rows: list[dict]) -> dict:
    items = []
    for r in rows:
        items.append({
            "name": r.get("กลุ่มโฆษณา", ""),
            "cost": num(r.get("ค่าใช้จ่าย", "")),
            "clicks": int(num(r.get("คลิก", ""))),
            "conv": num(r.get("Conversion", "")),
            "cpa": num(r.get("ราคา/1 Conv.", "")),
            "cpc": num(r.get("CPC เฉลี่ย", "")),
            "status": r.get("สถานะ", ""),
            "cpa_target": r.get("CPA ที่ตั้งไว้", ""),
        })
    return {"groups": items}


def main():
    campaigns = parse_csv(ADS_DIR / "แคมเปญ.csv")
    keywords = parse_csv(ADS_DIR / "คีย์เวิร์ด.csv")
    search_terms = parse_csv(ADS_DIR / "รายงานข้อความค้นหา.csv")
    ads = parse_csv(ADS_DIR / "รายงานโฆษณา.csv")
    ad_groups = parse_csv(ADS_DIR / "กลุ่มโฆษณา 2.csv")

    camp_old = next((r for r in campaigns if r.get("แคมเปญ") == OLD), {})
    camp_new = next((r for r in campaigns if r.get("แคมเปญ") == NEW), {})

    kw_old = kw_stats(filter_camp(keywords, "แคมเปญ", OLD))
    kw_new = kw_stats(filter_camp(keywords, "แคมเปญ", NEW))
    st_old = st_stats(filter_camp(search_terms, "แคมเปญ", OLD))
    st_new = st_stats(filter_camp(search_terms, "แคมเปญ", NEW))
    ad_old = ad_stats(filter_camp(ads, "แคมเปญ", OLD))
    ad_new = ad_stats(filter_camp(ads, "แคมเปญ", NEW))
    ag_old = ag_stats(filter_camp(ad_groups, "แคมเปญ", OLD))
    ag_new = ag_stats(filter_camp(ad_groups, "แคมเปญ", NEW))

    # Keyword overlap
    old_kws = {r.get("คีย์เวิร์ด", "").strip().strip('"')
               for r in filter_camp(keywords, "แคมเปญ", OLD)}
    new_kws = {r.get("คีย์เวิร์ด", "").strip().strip('"')
               for r in filter_camp(keywords, "แคมเปญ", NEW)}
    shared = old_kws & new_kws

    # Compare shared keywords performance
    shared_compare = []
    for kw in shared:
        if not kw:
            continue
        o = next((i for i in kw_old["top_kw"] + kw_old["expensive_kw"]
                  if i["keyword"] == kw), None)
        # re-scan all
        o_rows = [r for r in filter_camp(keywords, "แคมเปญ", OLD)
                  if r.get("คีย์เวิร์ด", "").strip().strip('"') == kw]
        n_rows = [r for r in filter_camp(keywords, "แคมเปญ", NEW)
                  if r.get("คีย์เวิร์ด", "").strip().strip('"') == kw]
        if o_rows and n_rows:
            oc = num(o_rows[0].get("ค่าใช้จ่าย", ""))
            nc = num(n_rows[0].get("ค่าใช้จ่าย", ""))
            ocv = num(o_rows[0].get("Conversion", ""))
            ncv = num(n_rows[0].get("Conversion", ""))
            if oc > 100 or nc > 100:
                shared_compare.append({
                    "keyword": kw,
                    "old_cost": oc, "new_cost": nc,
                    "old_conv": ocv, "new_conv": ncv,
                    "old_cpa": oc / ocv if ocv else 0,
                    "new_cpa": nc / ncv if ncv else 0,
                    "old_cpc": num(o_rows[0].get("CPC เฉลี่ย", "")),
                    "new_cpc": num(n_rows[0].get("CPC เฉลี่ย", "")),
                })
    shared_compare.sort(key=lambda x: x["old_cost"] + x["new_cost"], reverse=True)

    report = {
        "campaign_level": {
            "old": {k: camp_old.get(k, "") for k in [
                "แคมเปญ", "งบประมาณ", "สถานะ", "เหตุผลของสถานะ",
                "ค่าใช้จ่าย", "คลิก", "การแสดงผล", "Conversion",
                "CPC เฉลี่ย", "ราคา/1 Conv.", "อัตรา Conv.",
                "ประเภทกลยุทธ์การเสนอราคา", "คะแนนการเพิ่มประสิทธิภาพ",
            ]},
            "new": {k: camp_new.get(k, "") for k in [
                "แคมเปญ", "งบประมาณ", "สถานะ", "เหตุผลของสถานะ",
                "ค่าใช้จ่าย", "คลิก", "การแสดงผล", "Conversion",
                "CPC เฉลี่ย", "ราคา/1 Conv.", "อัตรา Conv.",
                "ประเภทกลยุทธ์การเสนอราคา", "คะแนนการเพิ่มประสิทธิภาพ",
            ]},
        },
        "keywords": {"old": kw_old, "new": kw_new},
        "search_terms": {"old": st_old, "new": st_new},
        "ads": {"old": ad_old, "new": ad_new},
        "ad_groups": {"old": ag_old, "new": ag_new},
        "keyword_overlap": {
            "old_only": len(old_kws - new_kws),
            "new_only": len(new_kws - old_kws),
            "shared": len(shared),
            "shared_compare": shared_compare[:20],
        },
    }

    out = Path(__file__).parent / "analysis" / "bigclean_comparison.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
