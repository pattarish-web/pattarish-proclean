"""
ดึงข้อมูล Google Ads ทั้งหมดของ HFT เก็บในเครื่อง (CSV + JSON)

Usage:
  python run_ads_export.py
  python run_ads_export.py --years 3
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from google_ads.client import get_client
from google_ads.config import EXPORT_DIR, REFRESH_TOKEN, SOURCE_CUSTOMER_ID
from google_ads.queries import build_queries

HFT_ID = "3597521395"
HFT_LABEL = "HFT"


def _check_ready() -> None:
    if not REFRESH_TOKEN:
        raise SystemExit(
            "Missing REFRESH_TOKEN in .env. Run: python run_ads_auth.py"
        )


def _probe_api_access(client, customer_id: str) -> None:
    service = client.get_service("GoogleAdsService")
    query = "SELECT customer.id FROM customer LIMIT 1"
    try:
        list(service.search(customer_id=customer_id, query=query))
    except Exception as exc:
        msg = str(exc)
        if "DEVELOPER_TOKEN_NOT_APPROVED" in msg or "only approved for use with test accounts" in msg:
            raise SystemExit(
                "Developer Token is TEST access only (cannot read production HFT).\n"
                "MCC 791-572-9299 > Tools > Setup > API Center > Apply for Basic Access.\n"
                "Until approved, download CSV from Google Ads UI instead."
            ) from exc
        raise


def _serialize(value: Any) -> Any:
    if hasattr(value, "name"):
        return value.name
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        try:
            return [_serialize(v) for v in value]
        except TypeError:
            pass
    return value


def _row_to_dict(row: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for field, value in row._pb.ListFields():
        key = field.name
        if hasattr(value, "ListFields"):
            nested = {}
            for sub_field, sub_value in value.ListFields():
                nested[sub_field.name] = _serialize(sub_value)
            data[key] = nested
        else:
            data[key] = _serialize(value)
    return data


def run_query(client, customer_id: str, query: str) -> list[dict[str, Any]]:
    service = client.get_service("GoogleAdsService")
    rows: list[dict[str, Any]] = []
    stream = service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            rows.append(_row_to_dict(row))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(row[k], ensure_ascii=False)
                    if isinstance(row.get(k), (dict, list))
                    else row.get(k, "")
                    for k in keys
                }
            )


def date_clause_years(years: int) -> str:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=365 * years)
    return f"BETWEEN '{start.isoformat()}' AND '{end.isoformat()}'"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export all HFT Google Ads data locally")
    parser.add_argument("--customer-id", default=SOURCE_CUSTOMER_ID, help="HFT customer ID")
    parser.add_argument("--years", type=int, default=3, help="Years of performance history")
    args = parser.parse_args()

    _check_ready()
    client = get_client(target_customer_id=args.customer_id)
    _probe_api_access(client, args.customer_id)

    clause = date_clause_years(args.years)
    queries = build_queries(clause)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = EXPORT_DIR / f"{HFT_LABEL}_{args.customer_id}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "account": HFT_LABEL,
        "customer_id": args.customer_id,
        "exported_at": stamp,
        "date_range": clause,
        "output_dir": str(out_dir),
        "files": {},
    }

    total = len(queries)
    for i, (name, query) in enumerate(queries.items(), 1):
        print(f"[{i}/{total}] {name} ...", flush=True)
        try:
            rows = run_query(client, args.customer_id, query)
            csv_path = out_dir / f"{name}.csv"
            json_path = out_dir / f"{name}.json"
            write_csv(csv_path, rows)
            json_path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            manifest["files"][name] = {"rows": len(rows), "csv": csv_path.name}
            print(f"       OK — {len(rows)} rows", flush=True)
        except Exception as exc:
            manifest["files"][name] = {"error": str(exc)}
            print(f"       SKIP — {exc}", flush=True)

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Keep console output ASCII-safe for Windows default encodings.
    print(f"\nDONE. Output folder:\n{out_dir}")


if __name__ == "__main__":
    main()
