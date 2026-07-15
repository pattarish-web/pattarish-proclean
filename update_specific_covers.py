import json
import os
import time
from pathlib import Path
from generate_blog import _fallback_image_url

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "posts.json"

TARGET_TITLES = [
    "ประเมินราคาทำความสะอาดเบื้องต้น: คู่มือคิดค่าใช้จ่ายยังไงให้เป๊ะ ไม่มีกังวล!",
    "KPI ทีมแม่บ้านออฟฟิศ: วัดผลยังไงให้ทีมแฮปปี้ ออฟฟิศสะอาดปิ๊ง",
    "เช็ดพื้นไม้ให้สวยนาน ไม่กลัวพัง! เคล็ดลับจากผู้เชี่ยวชาญที่คุณต้องรู้"
]

def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        return 1
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)
        
    updated_count = 0
    for post in posts:
        title = post.get("title", "")
        if title in TARGET_TITLES:
            category = post.get("category")
            print(f"Updating: '{title}' [{category}]")
            
            # Select cover using OpenAI Multimodal
            new_url = _fallback_image_url(title, category, title)
            print(f"  Old URL: {post.get('image')}")
            print(f"  New URL: {new_url}")
            post["image"] = new_url
            updated_count += 1
            
            # Sleep 15 seconds to prevent OpenAI Rate Limits
            print("  Sleeping 15 seconds...")
            time.sleep(15)
            
    if updated_count == 0:
        print("No matching posts found to update.")
        return 0
        
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully updated {updated_count} posts in posts.json.")
    
    # Rebuild the site files
    try:
        import build_blogs
        import build_listings
        import update_sitemap
        build_blogs.build_blogs()
        build_listings.build_listings()
        update_sitemap.update_sitemap()
        print("Rebuild of site files successful.")
    except Exception as exc:
        print(f"Error rebuilding site files: {exc}")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
