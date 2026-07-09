"""One-time OAuth flow to obtain GOOGLE_ADS_REFRESH_TOKEN."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from google_auth_oauthlib.flow import InstalledAppFlow

from google_ads.config import ROOT

SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main() -> None:
    client_secrets = ROOT / "google_ads" / "client_secret.json"
    if not client_secrets.exists():
        raise SystemExit(
            "Place OAuth client JSON at google_ads/client_secret.json\n"
            "Download from Google Cloud Console > Credentials > OAuth 2.0 Client IDs"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    env_path = ROOT / ".env"
    token = creds.refresh_token or ""
    if not token:
        raise SystemExit("No refresh token returned. Remove prior app access and retry.")

    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    key = "GOOGLE_ADS_REFRESH_TOKEN="
    updated = False
    for idx, line in enumerate(lines):
        if line.startswith(key):
            lines[idx] = key + token
            updated = True
            break
    if not updated:
        lines.append(key + token)

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Saved GOOGLE_ADS_REFRESH_TOKEN to .env")


if __name__ == "__main__":
    main()
