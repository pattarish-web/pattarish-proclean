import os

from site_config import LOCAL_AREAS, SITE_URL


def build_local_pages():
    os.makedirs("areas", exist_ok=True)

    with open("local_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    for area in LOCAL_AREAS:
        html = template
        for key, value in area.items():
            html = html.replace("{{" + key + "}}", value)
        html = html.replace("{{site_url}}", SITE_URL)
        html = html.replace("{{canonical}}", f"{SITE_URL}/areas/{area['file']}.html")

        path = os.path.join("areas", f"{area['file']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"Generated {len(LOCAL_AREAS)} local SEO pages in areas/")


if __name__ == "__main__":
    build_local_pages()
