import json
import os
import time
from pathlib import Path
from generate_blog import _fallback_image_url

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "posts.json"

def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        return 1
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)
        
    print(f"Original posts count: {len(posts)}")
    
    # 1. Deduplicate posts by title (keeping the first occurrence from the end to keep newer/better ones, or vice versa)
    seen_titles = set()
    deduped_posts = []
    # Reverse to keep the latest posts
    for post in reversed(posts):
        title = post.get("title", "").strip()
        if title in seen_titles:
            print(f"Removing duplicate post: '{title}'")
            continue
            
        # Also handle very similar titles if needed, but strict title matching is safer first
        seen_titles.add(title)
        deduped_posts.append(post)
        
    # Restore original chronological order
    deduped_posts.reverse()
    print(f"Deduplicated posts count: {len(deduped_posts)}")
    
    # 2. Find any posts in the last 15 posts that still use the default stock images (blog-office.jpg or blog-home.jpg)
    # and update them to use unique background images using OpenAI Multimodal
    updated_count = 0
    for i in range(max(0, len(deduped_posts) - 15), len(deduped_posts)):
        post = deduped_posts[i]
        title = post.get("title", "")
        img = post.get("image", "")
        
        # Check if it uses the default cover
        if "blog-office.jpg" in img or "blog-home.jpg" in img:
            category = post.get("category")
            print(f"Assigning unique cover for index {i}: '{title}' [{category}]")
            
            # Select cover using OpenAI Multimodal
            new_url = _fallback_image_url(title, category, title)
            print(f"  Old URL: {img}")
            print(f"  New URL: {new_url}")
            post["image"] = new_url
            updated_count += 1
            
            # Sleep 15 seconds to prevent OpenAI Rate Limits
            print("  Sleeping 15 seconds...")
            time.sleep(15)
            
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(deduped_posts, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully deduplicated and updated {updated_count} default covers.")
    
    # 3. Rebuild all site files
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
