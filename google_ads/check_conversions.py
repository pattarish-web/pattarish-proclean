"""Print Google Ads conversion setup checklist for SangkanClean."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from site_config import (
    ADS_CONVERSION_ID,
    ADS_LEAD_CONVERSION_LABEL,
    ADS_LINE_CONVERSION_LABEL,
    ADS_PHONE_CONVERSION_LABEL,
    ads_conversion_send_to,
)


def main() -> int:
    print("=" * 60)
    print("SangkanClean — Pre-launch conversion checklist")
    print("=" * 60)
    print(f"Ads account ID: AW-18299765093")
    print(f"Customer ID:    615-120-8199")
    print()

    labels = {
        "phone (primary — Smart Bidding)": ADS_PHONE_CONVERSION_LABEL,
        "line (secondary)": ADS_LINE_CONVERSION_LABEL,
        "lead form (optional)": ADS_LEAD_CONVERSION_LABEL,
    }

    missing = []
    for name, label in labels.items():
        status = "OK" if label else "MISSING"
        send_to = ads_conversion_send_to(label) if label else "(not set)"
        print(f"  [{status}] {name}")
        print(f"         send_to: {send_to}")
        if not label:
            missing.append(name)

    print()
    if missing:
        print("ACTION REQUIRED before opening campaigns:")
        print("  1. Google Ads > Goals > Conversions > + New conversion action")
        print("  2. Create WEBSITE conversions:")
        print("     - 'Click to call' or 'Phone click' (primary)")
        print("     - 'Line click' (secondary)")
        print("  3. Tag setup: use Google tag AW-18299765093")
        print()
        print("  NOTE: SangkanClean already has GA4-imported conversions:")
        print("    - Sangkan Clean (web) click_phone  (Primary, account goal)")
        print("    - Sangkan Clean (web) click_line")
        print("    - Sangkan Clean (web) generate_lead")
        print("  If tracking.js fires click_phone/click_line on site, GA4 path works")
        print("  without ADS_*_CONVERSION_LABEL. Labels are optional (direct Ads tag).")
        print("  4. Copy labels into google_ads/conversion_labels.example.env")
        print("     then export:")
        print("       set ADS_PHONE_CONVERSION_LABEL=your_label")
        print("       set ADS_LINE_CONVERSION_LABEL=your_label")
        print("  5. Run: python build_assets.py")
        print("  6. Deploy site → test click phone/line on landing-bigcleaning.html")
        print()
        print("  Or add secrets to GitHub: ADS_PHONE_CONVERSION_LABEL, ADS_LINE_CONVERSION_LABEL")
        return 1

    print("All conversion labels configured.")
    print("Run: python build_assets.py  then deploy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
