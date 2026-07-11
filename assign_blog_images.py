"""Assign varied first-party blog images by post topic keywords."""

import json
from datetime import date

from site_config import SITE_URL

# Ordered keyword -> image filename (first match wins)
TOPIC_IMAGES = [
    (("โรงงาน",), "blog-factory.jpg"),
    (("โกดัง",), "blog-warehouse.jpg"),
    (("โรงแรม", "รีสอร์ท"), "blog-hotel.jpg"),
    (("โรงพยาบาล", "คลินิก"), "blog-hospital.jpg"),
    (("โรงเรียน", "มหาวิทยาลัย"), "blog-school.jpg"),
    (("ห้าง", "ศูนย์การค้า"), "blog-mall.jpg"),
    (("ร้านอาหาร", "คาเฟ่"), "blog-restaurant.jpg"),
    (("โชว์รูม",), "blog-showroom.jpg"),
    (("ตึกสูง", "กระจก"), "blog-highrise.jpg"),
    (("ฟิตเนส",), "blog-gym.jpg"),
    (("คอนโด", "บ้าน"), "blog-home.jpg"),
    (("ออฟฟิศ", "สำนักงาน", "อาคาร"), "blog-office.jpg"),
]

DEFAULT_IMAGE = "blog-office.jpg"


def pick_image(post):
    text = f"{post.get('title', '')} {post.get('slug', '')} {post.get('description', '')}"
    for keywords, filename in TOPIC_IMAGES:
        if any(k in text for k in keywords):
            return filename
    return DEFAULT_IMAGE


def main():
    with open("posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    today = date.today().isoformat()
    counts = {}
    for post in posts:
        filename = pick_image(post)
        post["image"] = f"{SITE_URL}/images/blog/{filename}"
        post["dateModified"] = today
        counts[filename] = counts.get(filename, 0) + 1

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Assigned images for {len(posts)} posts:")
    for name, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: {n}")


if __name__ == "__main__":
    main()
