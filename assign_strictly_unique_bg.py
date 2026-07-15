import json
import os
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "posts.json"

# Available backgrounds in images/blog/bg/ for each category
CATEGORY_BGS = {
    "factory": [f"bg-factory-{i:02d}.jpg" for i in range(1, 7)],
    "warehouse": [f"bg-warehouse-{i:02d}.jpg" for i in range(1, 6)],
    "hotel": [f"bg-hotel-{i:02d}.jpg" for i in range(1, 9)],
    "hospital": [f"bg-hospital-{i:02d}.jpg" for i in range(1, 8)],
    "school": [f"bg-school-{i:02d}.jpg" for i in range(1, 8)],
    "mall": [f"bg-mall-{i:02d}.jpg" for i in range(1, 8)],
    "restaurant": [f"bg-restaurant-{i:02d}.jpg" for i in range(1, 7)],
    "showroom": [f"bg-showroom-{i:02d}.jpg" for i in range(1, 5)],
    "highrise": [f"bg-highrise-{i:02d}.jpg" for i in range(1, 5)],
    "gym": [f"bg-gym-{i:02d}.jpg" for i in range(1, 5)],
    "home": [f"bg-home-{i:02d}.jpg" for i in range(1, 11)],
    "office": [f"bg-office-{i:02d}.jpg" for i in range(1, 13)]
}

TOPIC_MAPPING = [
    (("โรงงาน",), "factory"),
    (("โกดัง",), "warehouse"),
    (("โรงแรม", "รีสอร์ท"), "hotel"),
    (("โรงพยาบาล", "คลินิก"), "hospital"),
    (("โรงเรียน", "มหาวิทยาลัย"), "school"),
    (("ห้าง", "ศูนย์การค้า"), "mall"),
    (("ร้านอาหาร", "คาเฟ่"), "restaurant"),
    (("โชว์รูม",), "showroom"),
    (("ตึกสูง", "กระจก"), "highrise"),
    (("ฟิตเนส",), "gym"),
    (("คอนโด", "บ้าน", "ห้องน้ำ", "ครัว", "โซฟา", "พรม", "กลิ่นอับ"), "home"),
    (("ออฟฟิศ", "สำนักงาน", "อาคาร", "ธุรกิจ", "B2B", "QC"), "office"),
]

from site_config import SITE_URL

def pick_category(title, description, category):
    text = f"{title} {description} {category}".lower()
    for keywords, cat_name in TOPIC_MAPPING:
        if any(k.lower() in text for k in keywords):
            return cat_name
    # Fallback based on category name
    if "คู่มือ" in category or "ธุรกิจ" in category:
        return "office"
    return "home"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)
        
    print(f"Assigning strictly unique cycling covers for {len(posts)} posts...")
    
    # We will track indices for cycling per category to guarantee distribution
    cycle_indices = {cat: 0 for cat in CATEGORY_BGS}
    
    for i, post in enumerate(posts):
        # We preserve the custom DALL-E 3 generated image if there is one (like khacat-khrab-ho.jpg)
        img_url = post.get("image", "")
        if "images/blog/bg/" in img_url or "blog-office.jpg" in img_url or "blog-home.jpg" in img_url or not img_url:
            # Re-assign using unique cycle
            cat = pick_category(post.get("title", ""), post.get("description", ""), post.get("category", ""))
            bg_list = CATEGORY_BGS[cat]
            idx = cycle_indices[cat]
            selected_bg = bg_list[idx % len(bg_list)]
            
            # Move to next index for this category
            cycle_indices[cat] += 1
            
            post["image"] = f"{SITE_URL}/images/blog/bg/{selected_bg}"
            print(f"Post {i} [{cat}]: '{post.get('title')[:30]}' -> {selected_bg}")
            
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print("Rebuilding site files...")
    try:
        import build_blogs
        import build_listings
        import update_sitemap
        build_blogs.build_blogs()
        build_listings.build_listings()
        update_sitemap.update_sitemap()
        print("Rebuild successful.")
    except Exception as exc:
        print(f"Rebuild failed: {exc}")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
