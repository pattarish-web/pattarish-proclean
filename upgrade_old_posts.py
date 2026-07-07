import json
import os
import time
import requests

def get_api_keys():
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    if not raw_key:
        return []
    if "," in raw_key:
        return [k.strip() for k in raw_key.split(",") if k.strip()]
    return [raw_key.strip()]

def generate_geo_content(api_key, title, description):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    คุณเป็นผู้เชี่ยวชาญด้านการทำความสะอาดและนักเขียนบทความ SEO/GEO (Generative Engine Optimization)
    ช่วยเขียนบทความบล็อกภาษาไทยแบบเจาะลึก
    
    ชื่อบทความ: "{title}"
    คำอธิบาย: "{description}"
    
    ข้อกำหนด (สำคัญมากสำหรับการทำ GEO เพื่อให้ AI นำไปอ้างอิง):
    เนื้อหาบทความ (content) ต้องเป็นโค้ด HTML semantic ล้วนๆ (ไม่ต้องมี <html> <body> ให้อยู่ใน tag <div> หรือ <article> ได้เลย) โดยบังคับให้มีโครงสร้างดังนี้:
    - <h2>สรุปประเด็นสำคัญ (Key Takeaways)</h2> ตามด้วย <ul><li> 3-4 ข้อสั้นๆ
    - <h2>เนื้อหาหลัก</h2> อธิบายเนื้อหาแบบเจาะลึก มีการใช้ <strong> เพื่อเน้นคำสำคัญ
    - <h2>ข้อมูลสถิติที่น่าสนใจ</h2> บังคับให้สร้างตัวเลขสถิติหรือข้อเท็จจริง (Facts) ที่อ้างอิงได้แบบสมจริง (เช่น "จากการศึกษาพบว่า...") เพื่อให้ AI นำไปอ้างอิงได้
    - <h2>คำถามที่พบบ่อย (FAQ)</h2> ถามตอบ 2-3 ข้อแบบสั้นๆ ตรงประเด็น
    
    ส่งกลับมาในรูปแบบ JSON เท่านั้น ห้ามมีข้อความอื่น โครงสร้างดังนี้:
    {{
      "content": "<h2>สรุปประเด็นสำคัญ...</h2>..."
    }}
    """
    
    data = {
        "contents": [{"parts":[{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    max_retries = 8
    base_delay = 15  # รอขั้นต่ำ 15 วินาทีหากชนลิมิต
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            
            # ถ้าชนลิมิต หรือโควตาหมดชั่วคราว
            if response.status_code == 429 or (response.status_code == 400 and "RESOURCE_EXHAUSTED" in response.text):
                wait_time = base_delay * (1.5 ** attempt)
                print(f"  -> Rate limit hit (RESOURCE_EXHAUSTED) for key {api_key[:10]}... Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
                
            if response.status_code != 200:
                print(f"Gemini API Error details: {response.text}")
            response.raise_for_status()
            result_json = response.json()
            
            text_response = result_json['candidates'][0]['content']['parts'][0]['text']
            parsed_result = json.loads(text_response)
            return parsed_result.get("content", "")
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error calling Gemini API for '{title}': {e}")
                return ""
            wait_time = base_delay * (1.5 ** attempt)
            print(f"  -> Request failed ({e}). Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
            
    return ""

def upgrade_posts():
    api_keys = get_api_keys()
    if not api_keys:
        print("Error: GEMINI_API_KEY environment variable not found.")
        return
    
    with open('posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    upgraded_count = 0
    key_index = 0
    
    for idx, post in enumerate(posts):
        content = post.get("content", "")
        # เช็คว่าถ้าเนื้อหาเดิมยังไม่มีคำว่า "สรุปประเด็นสำคัญ" แปลว่ายังไม่ใช่ GEO ให้เขียนทับใหม่
        if "สรุปประเด็นสำคัญ" not in content:
            print(f"[{idx+1}/{len(posts)}] Upgrading: {post['title']}")
            
            # สลับใช้คีย์แบบวนลูป (Round-Robin Key Rotation)
            current_key = api_keys[key_index % len(api_keys)]
            content = generate_geo_content(current_key, post['title'], post['description'])
            key_index += 1
            
            if content:
                post['content'] = content
                upgraded_count += 1
                
                # เซฟทุกครั้งที่เขียนเสร็จ 1 บทความ (Auto-save)
                with open('posts.json', 'w', encoding='utf-8') as f:
                    json.dump(posts, f, ensure_ascii=False, indent=2)
                    
                # ถ้ามีหลายคีย์ สลับคีย์แล้ว พักแค่ 4 วินาทีพอ / ถ้ามีคีย์เดียว พัก 12 วินาทีเพื่อความปลอดภัย
                sleep_time = 4 if len(api_keys) > 1 else 12
                print(f"  -> Success! Wait {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"  -> Failed to generate content.")
                time.sleep(5)
        else:
            print(f"[{idx+1}/{len(posts)}] Skip: Already has content.")

    print(f"Upgrade Complete! Total upgraded: {upgraded_count}")
    
    # สั่ง Build HTML ใหม่ทั้งหมด
    if upgraded_count > 0:
        try:
            import build_blogs
            build_blogs.build_blogs()
            import update_sitemap
            update_sitemap.update_sitemap()
            print("Successfully rebuilt HTML and Sitemap.")
        except Exception as e:
            print(f"Error rebuilding: {e}")

if __name__ == "__main__":
    upgrade_posts()
