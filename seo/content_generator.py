# seo/content_generator.py
"""
Content Generation Module
Uses OpenAI GPT‑3.5‑Turbo (free tier) to generate SEO‑optimized blog posts for each keyword.
For this demo, we simulate the AI response with placeholder text.
Generated posts are saved as Markdown files under `posts/`.
"""
import json
import os
from pathlib import Path

def generate_post(keyword, volume):
    title = f"บริการ{keyword}อย่างมืออาชีพ – Sangkan Clean"
    
    # Generate long-form HTML content
    content = f"""
    <div style="font-size: 1.05rem; line-height: 1.8; color: #334155;">
        <p>คุณกำลังมองหาผู้เชี่ยวชาญด้าน <strong>{keyword}</strong> อยู่ใช่ไหม? ที่ <strong>Sangkan Clean (สั่งการ คลีน)</strong> เราคือผู้นำด้านบริการทำความสะอาดครบวงจรที่มีประสบการณ์มากกว่า 30 ปี เราพร้อมมอบบริการที่ตอบโจทย์ทุกความต้องการของคุณ ไม่ว่าจะเป็นพื้นที่ขนาดเล็กหรือโปรเจกต์ขนาดใหญ่ระดับอุตสาหกรรม</p>
        
        <h3 style="color: #0f172a; margin-top: 2rem; margin-bottom: 1rem; font-weight: 700;">ทำไม {keyword} ถึงมีความสำคัญ?</h3>
        <p>ความสะอาดไม่เพียงแต่ส่งผลต่อภาพลักษณ์ของสถานที่ แต่ยังเกี่ยวข้องโดยตรงกับสุขภาพและคุณภาพชีวิตของผู้อยู่อาศัยหรือพนักงาน บริการ <strong>{keyword}</strong> ของเราถูกออกแบบมาเพื่อกำจัดสิ่งสกปรก ฝุ่นละออง และเชื้อโรคที่มองไม่เห็น ด้วยมาตรฐานการทำความสะอาดระดับสากล</p>
        
        <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; margin: 2rem 0; border-left: 4px solid #0d9488;">
            <h4 style="color: #0d9488; margin-top: 0; margin-bottom: 1rem; font-weight: 700;">✅ สิ่งที่คุณจะได้รับจากบริการของเรา:</h4>
            <ul style="margin-bottom: 0; padding-left: 1.5rem;">
                <li style="margin-bottom: 0.5rem;">ทีมงานมืออาชีพที่ผ่านการฝึกอบรมมาอย่างดี</li>
                <li style="margin-bottom: 0.5rem;">ใช้น้ำยาทำความสะอาดที่ปลอดภัย เป็นมิตรต่อสิ่งแวดล้อม</li>
                <li style="margin-bottom: 0.5rem;">เครื่องมือและอุปกรณ์ที่ทันสมัย มาตรฐานโรงงาน</li>
                <li style="margin-bottom: 0;">รับประกันความพึงพอใจ 100% พร้อมประกันความเสียหาย</li>
            </ul>
        </div>
        
        <h3 style="color: #0f172a; margin-top: 2rem; margin-bottom: 1rem; font-weight: 700;">ขั้นตอนการปฏิบัติงานมาตรฐาน</h3>
        <p>เรามีกระบวนการทำงานที่เป็นระบบ เริ่มตั้งแต่การสำรวจพื้นที่หน้างาน ประเมินคราบสกปรก และเลือกใช้วิธีการทำความสะอาดที่เหมาะสมที่สุด เพื่อให้แน่ใจว่าการ <strong>{keyword}</strong> จะออกมาสมบูรณ์แบบที่สุด นอกจากนี้เรายังมีทีม QC เข้าตรวจสอบคุณภาพงานทุกครั้งก่อนส่งมอบ</p>
        
        <p style="margin-top: 2rem;"><strong>อย่าปล่อยให้ความสกปรกเป็นปัญหาของคุณอีกต่อไป!</strong> มอบความไว้วางใจให้ <em>Sangkan Clean</em> ดูแลพื้นที่ของคุณให้สะอาดหมดจด เหมือนได้สถานที่ใหม่</p>
    </div>
    """
    return title, content

def main():
    import datetime
    # Load keywords
    with open("seo/keywords.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)
        
    # Load posts.json for website frontend
    posts_json_path = "posts.json"
    if os.path.exists(posts_json_path):
        with open(posts_json_path, "r", encoding="utf-8") as f:
            posts_data = json.load(f)
    else:
        posts_data = []
    
    existing_titles = [p.get("title") for p in posts_data]

    posts_dir = Path("posts")
    posts_dir.mkdir(exist_ok=True)
    
    for entry in keywords:
        kw = entry.get("keyword")
        vol = entry.get("search_volume", 0)
        title, body = generate_post(kw, vol)
        
        # Save markdown file
        slug = kw.replace(" ", "_").replace("/", "_")
        file_path = posts_dir / f"{slug}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{body}\n")
            
        # Image pool (all distinct and tested)
        img_pool = [
            "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1563453392212-326f5e854473?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=600&q=80"
        ]
        import random

        # Add to posts.json if not exists
        if title not in existing_titles:
            new_post = {
                "title": title,
                "description": f"เจาะลึกบริการทำความสะอาด {kw} ครบวงจรด้วยทีมงานมืออาชีพ มาตรฐานระดับสากล เพื่อความสะอาดและสุขอนามัยที่ดี",
                "category": "บริการ",
                "image": random.choice(img_pool),
                "date": datetime.datetime.today().strftime('%Y-%m-%d'),
                "content": body
            }
            posts_data.append(new_post)
            existing_titles.append(title)
            existing_titles.append(title)
            
    # Save updated posts.json
    with open(posts_json_path, "w", encoding="utf-8") as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
