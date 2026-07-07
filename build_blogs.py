import json
import os
import random
import re

from site_config import SITE_URL


def slugify(text):
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"[^\w\u0E00-\u0E7F\-]", "", text)
    return text.lower()


def build_related_posts_html(posts, current_idx, count=3):
    current = posts[current_idx]
    category = current.get("category", "")
    pool = [
        p
        for i, p in enumerate(posts)
        if i != current_idx and p.get("slug")
    ]
    same_cat = [p for p in pool if p.get("category") == category]
    picks = random.sample(same_cat, min(count, len(same_cat))) if same_cat else []
    if len(picks) < count:
        remaining = [p for p in pool if p not in picks]
        picks.extend(random.sample(remaining, min(count - len(picks), len(remaining))))

    if not picks:
        return ""

    cards = []
    for post in picks:
        cards.append(
            f'<a href="{post["slug"]}.html" class="related-card">'
            f'<img src="{post["image"]}" alt="{post["title"]}" loading="lazy" width="120" height="80">'
            f"<div><h4>{post['title']}</h4><span>{post['date']}</span></div></a>"
        )

    return (
        '<aside class="related-posts"><h3>บทความที่เกี่ยวข้อง</h3>'
        f'<div class="related-grid">{"".join(cards)}</div></aside>'
    )


def build_blogs():
    if not os.path.exists("blog"):
        os.makedirs("blog")

    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    with open("blog_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    updated_posts = []

    for i, post in enumerate(posts):
        slug = post.get("slug") or slugify(post["title"]) or f"post-{i}"
        post["slug"] = slug

        content = post.get("content", "")
        if not content:
            content = f"""<p>{post['description']}</p>
                   <p>บทความนี้กำลังอยู่ในระหว่างการจัดทำเนื้อหาเพิ่มเติม โปรดติดตามอัปเดตจากเราได้เร็วๆ นี้ครับ</p>
                   <p>สนใจสอบถามบริการทำความสะอาดเพิ่มเติม ติดต่อทีมงาน Sangkan Clean ได้เลยครับ</p>"""

        related = build_related_posts_html(posts, i)
        canonical = f"{SITE_URL}/blog/{slug}.html"

        html = template
        replacements = {
            "{{title}}": post["title"],
            "{{description}}": post["description"],
            "{{image}}": post["image"],
            "{{category}}": post.get("category", "บทความ"),
            "{{date}}": post.get("date", ""),
            "{{slug}}": slug,
            "{{content}}": content,
            "{{canonical}}": canonical,
            "{{related_posts}}": related,
        }
        for key, value in replacements.items():
            html = html.replace(key, value)

        filepath = os.path.join("blog", f"{slug}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        updated_posts.append(post)

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(updated_posts, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(updated_posts)} static blog posts in blog/ directory.")


if __name__ == "__main__":
    build_blogs()
