"""Mark GA4 key events via Admin API (run once after gcloud auth).

Prerequisites:
  pip install google-analytics-admin google-auth
  gcloud auth application-default login
  # or set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON

Env (one of):
  GA4_PROPERTY_ID — numeric property ID (Admin → Property settings)
  GA4_MEASUREMENT_ID — e.g. G-MJG0VZPFKS (auto lookup when credentials exist)
"""

import os
import sys

KEY_EVENTS = [
    "click_phone",
    "click_line",
    "click_messenger",
    "generate_lead",
    "quote_form_success",
]

PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "544613303").strip()
MEASUREMENT_ID = os.environ.get("GA4_MEASUREMENT_ID", "G-MJG0VZPFKS").strip()


def _resolve_property_id(client):
    global PROPERTY_ID
    if PROPERTY_ID.isdigit():
        return PROPERTY_ID
    if not MEASUREMENT_ID:
        return ""
    for summary in client.list_account_summaries():
        for prop in summary.property_summaries:
            parent = prop.property
            for stream in client.list_data_streams(parent=parent):
                web = getattr(stream, "web_stream_data", None)
                if web and web.measurement_id == MEASUREMENT_ID:
                    PROPERTY_ID = parent.rsplit("/", 1)[-1]
                    print(f"Resolved {MEASUREMENT_ID} → property {PROPERTY_ID}")
                    return PROPERTY_ID
    return ""


def main():
    try:
        from google.analytics.admin import AnalyticsAdminServiceClient
        from google.analytics.admin_v1alpha.types import KeyEvent
    except ImportError:
        print("Install: pip install google-analytics-admin google-auth", file=sys.stderr)
        sys.exit(1)

    client = AnalyticsAdminServiceClient()
    prop_id = _resolve_property_id(client)
    if not prop_id:
        print(
            "Set GA4_PROPERTY_ID (numeric) or GA4_MEASUREMENT_ID with valid ADC credentials.\n"
            "Example: GA4_MEASUREMENT_ID=G-MJG0VZPFKS python setup_ga4_key_events.py",
            file=sys.stderr,
        )
        sys.exit(1)

    parent = f"properties/{prop_id}"
    created = 0
    skipped = 0

    existing = {e.event_name for e in client.list_key_events(parent=parent)}

    for name in KEY_EVENTS:
        if name in existing:
            print(f"skip (exists): {name}")
            skipped += 1
            continue
        client.create_key_event(
            parent=parent,
            key_event=KeyEvent(event_name=name),
        )
        print(f"created key event: {name}")
        created += 1

    print(f"Done. created={created} skipped={skipped} total_target={len(KEY_EVENTS)}")


if __name__ == "__main__":
    main()
