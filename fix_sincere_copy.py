import os
import re

def fix_html_files():
    # Targets
    files_to_fix = ['index.html', 'blog_template.html']
    
    for filename in files_to_fix:
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix 1: Footer and sidebar text
        old_text_1 = "ผู้ให้สั่งการ คลีน บริการสะอาด สั่งได้ดั่งใจตั้งแต่ปี 2536 พร้อมส่งมอบความสะอาดและความสบายใจให้กับคุณ"
        new_text_1 = "Sangkan Clean เกิดจากการรวมตัวของทีมงานผู้เชี่ยวชาญหน้างานที่มีประสบการณ์กว่า 30 ปี พร้อมบริหารจัดการด้วยเทคโนโลยีใหม่ เพื่อส่งมอบความสะอาดและความสบายใจให้กับคุณ"
        
        # Fix 2: Badge in hero section (index.html)
        old_text_2 = "Sangkan Clean บริการสะอาด สั่งได้ดั่งใจตั้งแต่ปี 2536"
        new_text_2 = "Sangkan Clean บริหารงานยุคใหม่ โดยทีมงานประสบการณ์ 30 ปี"
        
        old_text_3 = "บริการสะอาด สั่งได้ดั่งใจตั้งแต่ปี 2536"
        new_text_3 = "รวมทีมผู้เชี่ยวชาญประสบการณ์กว่า 30 ปี"

        old_text_4 = "Sangkan Clean (สั่งการ คลีน) ให้บริการทำความสะอาดตั้งแต่ พ.ศ. 2536"
        new_text_4 = "Sangkan Clean (สั่งการ คลีน) คือการรวมทีมของผู้เชี่ยวชาญที่มีประสบการณ์กว่า 30 ปี"

        content = content.replace(old_text_1, new_text_1)
        content = content.replace(old_text_2, new_text_2)
        content = content.replace(old_text_3, new_text_3)
        content = content.replace(old_text_4, new_text_4)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {filename}")

if __name__ == '__main__':
    fix_html_files()
