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
        
    if len(posts) < 9:
        print("Not enough posts to update.")
        return 0
        
    print(f"Updating the last 9 posts in posts.json using OpenAI Multimodal selection with rate limit protection...")
    # Loop over the last 9 posts
    for i in range(-9, 0):
        post = posts[i]
        title = post.get("title")
        category = post.get("category")
        
        # Determine a keyword from title
        keyword = title
        print(f"Post {i}: '{title}' [{category}]")
        
        # Call fallback selection
        new_url = _fallback_image_url(keyword, category, title)
        print(f"  Old URL: {post.get('image')}")
        print(f"  New URL: {new_url}")
        post["image"] = new_url
        
        # Wait 10 seconds to avoid hitting OpenAI TPM/RPM rate limits
        print("  Waiting 10 seconds before next call...")
        time.sleep(10)
        
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        
    print("Done updating posts.json.")
    
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
