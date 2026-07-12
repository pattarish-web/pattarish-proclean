import json
import os

from site_config import (
    LOCAL_AREAS,
    ORGANIZATION_ID,
    SITE_URL,
    analytics_script_tag,
    area_served_schema,
    organization_schema,
)


def _faq_html(faq_items):
    parts = []
    for q, a in faq_items:
        parts.append(f"<details><summary>{q}</summary><p>{a}</p></details>")
    return "\n".join(parts)


def _faq_schema_json(faq_items):
    entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faq_items
    ]
    return json.dumps(
        {"@type": "FAQPage", "mainEntity": entities},
        ensure_ascii=False,
    )


def _breadcrumb_schema_json(title, canonical):
    return json.dumps(
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "หน้าแรก", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "พื้นที่ให้บริการ", "item": f"{SITE_URL}/#areas"},
                {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
            ],
        },
        ensure_ascii=False,
    )


def _related_posts_html(posts, area_slug, count=3):
    keywords = area_slug.replace("-", " ").split()
    scored = []
    for post in posts:
        text = (post.get("title", "") + post.get("description", "")).lower()
        score = sum(1 for k in keywords if k in text)
        if score:
            scored.append((score, post))
    scored.sort(key=lambda x: -x[0])
    picks = [p for _, p in scored[:count]]
    if len(picks) < count:
        for post in reversed(posts):
            if post not in picks:
                picks.append(post)
            if len(picks) >= count:
                break
    links = [
        f'<a href="../blog/{p["slug"]}.html">{p["title"]}</a>'
        for p in picks
        if p.get("slug")
    ]
    return "\n".join(links) if links else '<a href="../blog.html">ดูบทความทั้งหมด</a>'


def build_local_pages():
    os.makedirs("areas", exist_ok=True)

    with open("local_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    for area in LOCAL_AREAS:
        faq_items = area.get("faq", [])
        faq_html = _faq_html(faq_items)
        faq_schema = _faq_schema_json(faq_items) if faq_items else '{"@type":"WebPage"}'
        related = _related_posts_html(posts, area["slug"])
        canonical = f"{SITE_URL}/areas/{area['file']}.html"

        html = template
        for key, value in area.items():
            if key == "faq":
                continue
            html = html.replace("{{" + key + "}}", value)
        html = html.replace("{{site_url}}", SITE_URL)
        html = html.replace("{{canonical}}", canonical)
        html = html.replace("{{faq_html}}", faq_html)
        html = html.replace("{{faq_schema}}", faq_schema)
        html = html.replace("{{organization_schema}}", json.dumps(organization_schema(), ensure_ascii=False))
        html = html.replace("{{organization_id}}", ORGANIZATION_ID)
        html = html.replace("{{area_served_schema}}", json.dumps(area_served_schema([area["slug"]]), ensure_ascii=False))
        html = html.replace("{{breadcrumb_schema}}", _breadcrumb_schema_json(area["title"], canonical))
        html = html.replace("{{related_posts}}", related)
        html = html.replace("{{analytics_script}}", analytics_script_tag("../"))

        path = os.path.join("areas", f"{area['file']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"Generated {len(LOCAL_AREAS)} local SEO pages in areas/")


if __name__ == "__main__":
    build_local_pages()
