"""Run all site build steps."""

import json
from pathlib import Path

import build_blogs
import build_listings
import build_local_pages
import build_service_landings
import update_sitemap
from build_assets import patch_root_html_files, write_analytics_js
from seo.cannibalization import write_redirect_files


def build_all():
    write_analytics_js()
    patch_root_html_files()
    build_blogs.build_blogs()
    redirects_path = Path("seo/redirects.json")
    if redirects_path.exists():
        write_redirect_files(json.loads(redirects_path.read_text(encoding="utf-8")))
    build_listings.build_listings()
    build_local_pages.build_local_pages()
    build_service_landings.build_service_landings()
    update_sitemap.update_sitemap()
    print("Site build complete.")


if __name__ == "__main__":
    build_all()
