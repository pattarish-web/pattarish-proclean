"""Generate shared JS assets from site_config."""

import re

from site_config import ADS_CONVERSION_ID, ADS_LEAD_CONVERSION_LABEL, GA4_MEASUREMENT_ID, analytics_script_tag


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
    ads_label = ADS_LEAD_CONVERSION_LABEL.replace("'", "")
    ga4_config = (
        f"gtag('config','{GA4_MEASUREMENT_ID}');"
        if _has_ga4()
        else ""
    )
    content = f"""(function(){{
  var ads='{ADS_CONVERSION_ID}';
  var adsLeadLabel='{ads_label}';
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
  window.adsLeadSendTo=adsLeadLabel?ads+'/'+adsLeadLabel:'';
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
    ]
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
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
