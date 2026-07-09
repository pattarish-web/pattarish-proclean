"""List conversion actions and tag snippets for SangkanClean."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from google_ads.client import get_client
from google_ads.config import TARGET_CUSTOMER_ID


def main() -> int:
    client = get_client(target_customer_id=TARGET_CUSTOMER_ID)
    ga = client.get_service("GoogleAdsService")
    query = """
        SELECT
          conversion_action.id,
          conversion_action.name,
          conversion_action.status,
          conversion_action.type,
          conversion_action.category,
          conversion_action.origin,
          conversion_action.tag_snippets
        FROM conversion_action
        WHERE conversion_action.status != 'REMOVED'
    """
    cid = TARGET_CUSTOMER_ID.replace("-", "")
    rows = list(ga.search(customer_id=cid, query=query))
    if not rows:
        print("No conversion actions found.")
        return 1

    out = []
    for row in rows:
        ca = row.conversion_action
        labels = []
        for snippet in ca.tag_snippets:
            if snippet.conversion_id:
                labels.append(
                    {
                        "type": snippet.type_.name if snippet.type_ else "",
                        "page_format": snippet.page_format.name if snippet.page_format else "",
                        "global_site_tag": snippet.global_site_tag[:80] + "..." if snippet.global_site_tag else "",
                        "event_snippet": snippet.event_snippet,
                    }
                )
        out.append(
            {
                "id": ca.id,
                "name": ca.name,
                "status": ca.status.name,
                "type": ca.type_.name,
                "category": ca.category.name,
                "tag_snippets": labels,
            }
        )

    path = Path(__file__).parent / "analysis" / "conversion_actions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(out)} conversion actions to {path}")
    for item in out:
        print(f"  - {item['name']} ({item['status']}) id={item['id']}")
        for sn in item.get("tag_snippets", []):
            if sn.get("event_snippet"):
                print(f"      event: {sn['event_snippet'][:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
