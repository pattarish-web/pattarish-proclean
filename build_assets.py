"""Generate shared JS assets from site_config."""

import re
from pathlib import Path

from site_config import (
    ADS_CONVERSION_ID,
    GA4_MEASUREMENT_ID,
    ads_conversion_labels_js,
    analytics_script_tag,
)


def _has_ga4():
    return bool(GA4_MEASUREMENT_ID and GA4_MEASUREMENT_ID != "G-PLACEHOLDER")


GTAG_BLOCK = re.compile(
    r"<!-- Google tag \(gtag\.js\) -->.*?(?:<script[^>]*>.*?</script>\s*)+",
    re.DOTALL,
)
ORPHAN_GTAG_INLINE = re.compile(
    r"<script>\s*window\.dataLayer = window\.dataLayer \|\| \[\];\s*function gtag\(\).*?</script>\s*",
    re.DOTALL,
)


def write_analytics_js():
    """Keep analytics.js in sync for legacy references."""
    ga4_config = (
        f"gtag('config','{GA4_MEASUREMENT_ID}');"
        if _has_ga4()
        else ""
    )
    labels_json = ads_conversion_labels_js()
    content = f"""(function(){{
  var ads='{ADS_CONVERSION_ID}';
  var s=document.createElement('script');
  s.async=true;
  s.src='https://www.googletagmanager.com/gtag/js?id={ADS_CONVERSION_ID}';
  document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  function gtag(){{dataLayer.push(arguments);}}
  window.gtag=gtag;
  gtag('js',new Date());
  {ga4_config}
  gtag('config',ads);
  window.adsConversions={labels_json};
  window.adsLeadSendTo=window.adsConversions.phone||window.adsConversions.lead||window.adsConversions.line||'';
}})();
"""
    with open("analytics.js", "w", encoding="utf-8") as f:
        f.write(content)


def patch_root_html_files():
    """Refresh inline gtag snippet on hand-maintained root pages."""
    snippet = analytics_script_tag("")
    files = [
        "index.html",
        "blog.html",
        "privacy.html",
        "landing-bigcleaning.html",
        "landing-maid.html",
        "landing-sangkan-office.html",
        "landing-softcleaning.html",
        "landing-glass.html",
        "landing-carpet.html",
        "landing-ozone.html",
    ]
    tracking_tag = '<script src="tracking.js"></script>'
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        if GTAG_BLOCK.search(html):
            html = GTAG_BLOCK.sub(snippet + "\n", html, count=1)
        else:
            html = html.replace(
                '<script src="analytics.js" defer></script>',
                snippet,
                1,
            )
        while True:
            matches = list(ORPHAN_GTAG_INLINE.finditer(html))
            if len(matches) <= 1:
                break
            html = ORPHAN_GTAG_INLINE.sub("", html, count=1)
        if tracking_tag not in html and "</body>" in html:
            html = html.replace("</body>", f"    {tracking_tag}\n</body>", 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


def patch_gtag_directory(directory: str, prefix: str = "../") -> int:
    """Update inline gtag in all HTML files under a directory."""
    snippet = analytics_script_tag(prefix)
    count = 0
    for path in Path(directory).glob("*.html"):
        html = path.read_text(encoding="utf-8")
        if not GTAG_BLOCK.search(html):
            continue
        html = GTAG_BLOCK.sub(snippet + "\n", html, count=1)
        path.write_text(html, encoding="utf-8")
        count += 1
    return count


if __name__ == "__main__":
    write_analytics_js()
    patch_root_html_files()
    n_blog = patch_gtag_directory("blog", "../")
    n_areas = patch_gtag_directory("areas", "../")
    print(f"analytics.js + root HTML pages updated ({n_blog} blog, {n_areas} area pages).")
