"""Generate shared JS assets from site_config."""

import html
import json
import re
from pathlib import Path

from site_config import (
    ADS_CONVERSION_ID,
    GA4_MEASUREMENT_ID,
    ORGANIZATION_ID,
    SITE_URL,
    ads_conversion_labels_js,
    analytics_script_tag,
    organization_schema,
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
JSON_LD_BLOCK = re.compile(
    r"\s*<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>.*?</script>",
    re.DOTALL | re.IGNORECASE,
)


def _meta_value(source: str, name: str) -> str:
    match = re.search(
        rf'<meta\b(?=[^>]*(?:name|property)=["\']{re.escape(name)}["\'])[^>]*\bcontent=["\']([^"\']*)["\']',
        source,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def _tag_value(source: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", source, flags=re.DOTALL | re.IGNORECASE)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def _canonical_value(source: str) -> str:
    match = re.search(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)["\']', source, flags=re.I)
    return match.group(1).strip() if match else ""


def _normalize_image_dimensions(source: str) -> str:
    def replace(match):
        tag = match.group(0)
        if re.search(r'\b(?:role=["\']presentation["\']|alt=["\']["\'])', tag, flags=re.I):
            return tag
        width, height = ("180", "80") if re.search(r'(?:^|["\'])[^"\']*logo\.png', tag, flags=re.I) else ("1200", "675")
        if not re.search(r'\bwidth=["\'][^"\']+["\']', tag, flags=re.I):
            tag = tag.replace("<img", f'<img width="{width}"', 1)
        if not re.search(r'\bheight=["\'][^"\']+["\']', tag, flags=re.I):
            tag = tag.replace("<img", f'<img height="{height}"', 1)
        return tag

    return re.sub(r'<img\b[^>]*>', replace, source, flags=re.I)


def _replace_visible_claims(source: str) -> str:
    replacements = {
        "5,000": "",
        "100%": "ตามขอบเขตที่ตกลง",
        "99.9%": "ตามขอบเขตงาน",
        "30 ปี": "อย่างต่อเนื่อง",
    }

    def replace_text(match):
        text = match.group(2)
        for old, new in replacements.items():
            text = text.replace(old, new)
        return match.group(1) + text + match.group(3)

    return re.sub(r'(>)([^<]+)(<)', replace_text, source)


def _safe_home_content(source: str) -> str:
    replacement = """<!-- E-E-A-T / About Us Section (GEO Optimized) -->
    <section id=\"service-approach\" class=\"section-padding\" style=\"background:#fff;border-top:1px solid #f1f5f9;border-bottom:1px solid #f1f5f9;\">
        <div class=\"container text-center\">
            <span class=\"sub-title\">SERVICE APPROACH</span>
            <h2>แนวทางการให้บริการของเรา</h2>
            <p class=\"section-desc\">ทีมงานช่วยสอบถามรายละเอียดพื้นที่ วางขอบเขตงาน และแจ้งแนวทางเตรียมความพร้อมก่อนเริ่มบริการ เพื่อให้การประเมินและการทำงานสอดคล้องกับหน้างาน</p>
            <div class=\"why-grid\">
                <div class=\"why-card\"><h3>สำรวจขอบเขตงาน</h3><p>พูดคุยรายละเอียดพื้นที่และสิ่งที่ต้องการดูแลก่อนเริ่มงาน</p></div>
                <div class=\"why-card\"><h3>เตรียมตามหน้างาน</h3><p>วางแผนอุปกรณ์และขั้นตอนให้เหมาะกับประเภทพื้นที่</p></div>
                <div class=\"why-card\"><h3>ตรวจสอบความเรียบร้อย</h3><p>ทบทวนขอบเขตงานร่วมกันหลังให้บริการ</p></div>
            </div>
        </div>
    </section>

    <!-- Interactive Pricing Calculator -->"""
    return re.sub(
        r'<!-- E-E-A-T / About Us Section \(GEO Optimized\) -->[\s\S]*?<!-- Interactive Pricing Calculator -->',
        replacement,
        source,
        count=1,
    )


def upgrade_public_html(source: str, filename: str) -> str:
    """Apply repeatable evidence-first metadata upgrades to root public pages."""
    title = _tag_value(source, "title") or "Sangkan Clean"
    description = _meta_value(source, "description") or "บริการทำความสะอาด Sangkan Clean"
    canonical = _canonical_value(source) or f"{SITE_URL}/{filename}"

    source = re.sub(r'\s*<meta\b(?=[^>]*\b(?:property=["\']og:[^"\']+["\']|name=["\']twitter:[^"\']+["\']))[^>]*>', "", source, flags=re.I)
    source = re.sub(r'\s*<meta\b(?=[^>]*\bname=["\'](?:geo\.[^"\']+|ICBM)["\'])[^>]*>', "", source, flags=re.I)

    def remove_unsafe_schema(match):
        block = match.group(0)
        return "" if (
            ORGANIZATION_ID in block
            or re.search(r'\b(?:GeoCoordinates|hasMap|LocalBusiness)\b', block)
        ) else block

    source = JSON_LD_BLOCK.sub(remove_unsafe_schema, source)
    if filename == "index.html":
        source = _safe_home_content(source)
        source = source.replace(
            "องค์กรชั้นนำและลูกค้ากว่า 5,000 โปรเจกต์ทั่วประเทศไทยที่ไว้วางใจให้เราดูแลความสะอาด",
            "เราพร้อมให้ข้อมูลบริการและแนวทางประเมินงานสำหรับพื้นที่ที่ต้องการดูแล",
        )
        if 'rel="preload" as="image" href="images/hero-cleaning.jpg"' not in source:
            source = source.replace(
                "</head>",
                '    <link rel="preload" as="image" href="images/hero-cleaning.jpg" fetchpriority="high">\n</head>',
                1,
            )

    source = _replace_visible_claims(source)
    source = _normalize_image_dimensions(source)

    page_type = "WebSite" if filename == "index.html" else "WebPage"
    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "หน้าแรก", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": canonical},
        ],
    }
    page = {"@type": page_type, "@id": canonical, "name": title, "url": canonical}
    schema = {"@context": "https://schema.org", "@graph": [organization_schema(), page, breadcrumb]}
    social = "\n".join(
        [
            f'    <meta property="og:type" content="website">',
            f'    <meta property="og:title" content="{html.escape(title, quote=True)}">',
            f'    <meta property="og:description" content="{html.escape(description, quote=True)}">',
            f'    <meta property="og:url" content="{html.escape(canonical, quote=True)}">',
            f'    <meta property="og:image" content="{SITE_URL}/og-image.png">',
            f'    <meta name="twitter:card" content="summary_large_image">',
            f'    <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
            f'    <meta name="twitter:description" content="{html.escape(description, quote=True)}">',
            f'    <meta name="twitter:image" content="{SITE_URL}/og-image.png">',
            '    <script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False) + '</script>',
        ]
    )
    return source.replace("</head>", social + "\n</head>", 1)


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
        html = upgrade_public_html(html, path)
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
