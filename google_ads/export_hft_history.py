"""
Export HFT Google Ads history for AI analysis.

Usage:
  python google_ads/export_hft_history.py
  python google_ads/export_hft_history.py --days 90
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from google_ads.client import get_client
from google_ads.config import EXPORT_DIR, SOURCE_CUSTOMER_ID
from google_ads.queries import QUERIES


def _serialize(value: Any) -> Any:
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
        try:
            return [_serialize(v) for v in value]
        except TypeError:
            pass
    if hasattr(value, "name"):
        return value.name
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
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
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row[k], ensure_ascii=False) if isinstance(row.get(k), (dict, list)) else row.get(k, "") for k in keys})


def main() -> None:
    parser = argparse.ArgumentParser(description="Export HFT ads history")
    parser.add_argument("--customer-id", default=SOURCE_CUSTOMER_ID, help="HFT customer ID")
    parser.add_argument("--days", type=int, default=30, help="Reserved for future date filters")
    args = parser.parse_args()

    client = get_client()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = EXPORT_DIR / f"hft_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "exported_at": stamp,
        "source_customer_id": args.customer_id,
        "files": {},
    }

    for name, query in QUERIES.items():
        print(f"Fetching {name}...")
        try:
            rows = run_query(client, args.customer_id, query)
            csv_path = out_dir / f"{name}.csv"
            json_path = out_dir / f"{name}.json"
            write_csv(csv_path, rows)
            json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            manifest["files"][name] = {"rows": len(rows), "csv": str(csv_path.name)}
            print(f"  -> {len(rows)} rows")
        except Exception as exc:
            manifest["files"][name] = {"error": str(exc)}
            print(f"  !! {exc}")

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nExport complete: {out_dir}")
    print("Next: python google_ads/analyze_hft.py", out_dir)


if __name__ == "__main__":
    main()
