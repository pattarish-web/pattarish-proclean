import json
import os

from site_config import (
    ORGANIZATION_ID,
    SERVICE_AREAS,
    SERVICE_LANDINGS,
    SITE_URL,
    analytics_script_tag,
    area_served_schema,
    organization_schema,
)


def _breadcrumb_schema_json(title, canonical):
    return json.dumps(
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "หน้าแรก", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "บริการ", "item": f"{SITE_URL}/#services"},
                {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
            ],
        },
        ensure_ascii=False,
    )


def build_service_landings():
    with open("service_landing_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    for svc in SERVICE_LANDINGS:
        html = template
        for key, value in svc.items():
            html = html.replace("{{" + key + "}}", value)
        canonical = f"{SITE_URL}/{svc['file']}.html"
        html = html.replace("{{site_url}}", SITE_URL)
        html = html.replace("{{canonical}}", canonical)
        html = html.replace("{{organization_schema}}", json.dumps(organization_schema(), ensure_ascii=False))
        html = html.replace("{{organization_id}}", ORGANIZATION_ID)
        html = html.replace("{{area_served_schema}}", json.dumps(area_served_schema(SERVICE_AREAS), ensure_ascii=False))
        html = html.replace("{{breadcrumb_schema}}", _breadcrumb_schema_json(svc["title"], canonical))
        html = html.replace("{{prefix}}", "")
        html = html.replace("{{analytics_script}}", analytics_script_tag(""))

        path = f"{svc['file']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"Generated {len(SERVICE_LANDINGS)} service landing pages.")


if __name__ == "__main__":
    build_service_landings()
