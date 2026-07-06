import re

def update_generator():
    with open('generate_blog.py', 'r', encoding='utf-8') as f:
        content = f.read()

    old_prompt = """    คุณเป็นนักเขียนบทความและผู้เชี่ยวชาญด้านการทำความสะอาดและบริการจัดหาแม่บ้าน (SEO Content Creator)
    ช่วยเขียนบทความบล็อกสั้นภาษาไทยเกี่ยวกับหัวข้อ: "{keyword}"
    
    ข้อกำหนด:
    1. ชื่อบทความ (Title): น่าสนใจ ดึงดูดคลิก และมีคำค้นหาหลัก (SEO friendly) มีความยาวไม่เกิน 100 ตัวอักษร
    2. ย่อหน้าสรุป (Description): เป็นคำอธิบายสั้นๆ ดึงดูดความสนใจผู้อ่านเพื่อเป็นข้อความพรีวิวของบทความ ความยาวประมาณ 100-150 ตัวอักษร
    
    ส่งกลับมาในรูปแบบ JSON เท่านั้น ห้ามเขียนคำอธิบายอื่นนอกเหนือจาก JSON โครงสร้างดังนี้:
    {
      "title": "ชื่อบทความภาษาไทยที่น่าสนใจ",
      "description": "คำสรุปย่อหน้าพรีวิวภาษาไทย..."
    }"""
    
    new_prompt = """    คุณเป็นผู้เชี่ยวชาญด้านการทำความสะอาดและนักเขียนบทความ SEO/GEO (Generative Engine Optimization)
    ช่วยเขียนบทความบล็อกภาษาไทยแบบเจาะลึกเกี่ยวกับหัวข้อ: "{keyword}"
    
    ข้อกำหนด (สำคัญมากสำหรับการทำ GEO เพื่อให้ AI นำไปอ้างอิง):
    1. ชื่อบทความ (title): น่าสนใจ ดึงดูดคลิก มีคำค้นหาหลัก
    2. ย่อหน้าสรุป (description): อธิบายสั้นๆ ดึงดูดความสนใจผู้อ่าน
    3. เนื้อหาบทความ (content): ต้องเป็นโค้ด HTML semantic ล้วนๆ (ไม่ต้องมี <html> <body> ให้อยู่ใน tag <div> หรือ <article> ได้เลย) โดยบังคับให้มีโครงสร้างดังนี้:
       - <h2>สรุปประเด็นสำคัญ (Key Takeaways)</h2> ตามด้วย <ul><li> 3-4 ข้อสั้นๆ
       - <h2>เนื้อหาหลัก</h2> อธิบายเนื้อหาแบบเจาะลึก มีการใช้ <strong> เพื่อเน้นคำสำคัญ
       - <h2>ข้อมูลสถิติที่น่าสนใจ</h2> บังคับให้สร้างตัวเลขสถิติหรือข้อเท็จจริง (Facts) ที่อ้างอิงได้แบบสมจริง (เช่น "จากการศึกษาพบว่า...") เพื่อให้ AI นำไปอ้างอิงได้
       - <h2>คำถามที่พบบ่อย (FAQ)</h2> ถามตอบ 2-3 ข้อแบบสั้นๆ ตรงประเด็น
    
    ส่งกลับมาในรูปแบบ JSON เท่านั้น ห้ามมีข้อความอื่น โครงสร้างดังนี้:
    {
      "title": "ชื่อบทความภาษาไทย...",
      "description": "คำสรุปย่อหน้าพรีวิว...",
      "content": "<h2>สรุปประเด็นสำคัญ...</h2>..."
    }"""
    
    content = content.replace(old_prompt, new_prompt)
    
    # Update the JSON handling to include content
    old_json_handling = """        # นำมาประกอบเป็นข้อมูลบทความสมบูรณ์
        new_post = {
            "title": result["title"],
            "description": result["description"],
            "category": category,
            "image": random.choice(CLEANING_IMAGES),
            "date": datetime.today().strftime('%Y-%m-%d')
        }"""
    new_json_handling = """        # นำมาประกอบเป็นข้อมูลบทความสมบูรณ์
        new_post = {
            "title": result["title"],
            "description": result["description"],
            "content": result.get("content", ""),
            "category": category,
            "image": random.choice(CLEANING_IMAGES),
            "date": datetime.today().strftime('%Y-%m-%d')
        }"""
    content = content.replace(old_json_handling, new_json_handling)

    with open('generate_blog.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated generate_blog.py for GEO")

if __name__ == '__main__':
    update_generator()
