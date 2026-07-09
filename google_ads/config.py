"""Shared Google Ads API configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

LOGIN_CUSTOMER_ID = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "7915729299")
SOURCE_CUSTOMER_ID = os.getenv("GOOGLE_ADS_SOURCE_CUSTOMER_ID", "3597521395")
TARGET_CUSTOMER_ID = os.getenv("GOOGLE_ADS_TARGET_CUSTOMER_ID", "6151208199")

DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")

EXPORT_DIR = ROOT / "google_ads" / "exports"
ANALYSIS_DIR = ROOT / "google_ads" / "analysis"


def require_credentials() -> None:
    missing = [
        name
        for name, value in {
            "GOOGLE_ADS_DEVELOPER_TOKEN": DEVELOPER_TOKEN,
            "GOOGLE_ADS_CLIENT_ID": CLIENT_ID,
            "GOOGLE_ADS_CLIENT_SECRET": CLIENT_SECRET,
            "GOOGLE_ADS_REFRESH_TOKEN": REFRESH_TOKEN,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing credentials in .env: "
            + ", ".join(missing)
            + "\nCopy .env.example to .env and run: python google_ads/auth.py"
        )
