import os

def align_stats():
    # 1. Fix landing-maid.html
    maid_file = 'landing-maid.html'
    if os.path.exists(maid_file):
        with open(maid_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replacements for landing-maid.html
        content = content.replace(
            '<h2 class="section-title animate-on-scroll">กว่า 500 องค์กรไว้วางใจ</h2>',
            '<h2 class="section-title animate-on-scroll">บริการที่รวมความอบอุ่นและฝีมือจากหัวใจ</h2>'
        )
        content = content.replace(
            '<p class="section-subtitle animate-on-scroll">บริษัทชั้นนำและอาคารสำนักงานทั่วกรุงเทพฯ เลือกใช้บริการของเรา</p>',
            '<p class="section-subtitle animate-on-scroll">การผนึกกำลังของคนรุ่นใหม่และคุณป้ามือเก๋า เพื่อความสะอาดและสุขอนามัยที่ดีที่สุด</p>'
        )
        content = content.replace(
            '<div class="number">30+</div>\n                    <div class="label">ปีประสบการณ์</div>',
            '<div class="number">30+</div>\n                    <div class="label">ปี ประสบการณ์ของทีมงานหลัก</div>'
        )
        content = content.replace(
            '<div class="number">500+</div>\n                    <div class="label">องค์กรที่ไว้วางใจ</div>',
            '<div class="number">5,000+</div>\n                    <div class="label">บ้านและโครงการที่เคยดูแล</div>'
        )
        content = content.replace(
            '<div class="number">2,000+</div>\n                    <div class="label">บุคลากรพร้อมบริการ</div>',
            '<div class="number">100%</div>\n                    <div class="label">ความละเอียดและตรวจสอบคุณภาพ</div>'
        )
        content = content.replace(
            '<div class="number">98%</div>\n                    <div class="label">ลูกค้าต่อสัญญา</div>',
            '<div class="number">99%</div>\n                    <div class="label">ลูกค้าพึงพอใจและบอกต่อ</div>'
        )
        
        with open(maid_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully aligned stats in {maid_file}")

    # 2. Fix landing-bigcleaning.html
    big_file = 'landing-bigcleaning.html'
    if os.path.exists(big_file):
        with open(big_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replacements for landing-bigcleaning.html
        content = content.replace(
            '<span>ดูแลมากกว่า 500+ โครงการ</span>',
            '<span>ดูแลมากกว่า 5,000+ บ้านและโครงการ</span>'
        )
        content = content.replace(
            '<div class="stat-number">30+</div>\n                    <div class="stat-label">ปีประสบการณ์</div>',
            '<div class="stat-number">30+</div>\n                    <div class="stat-label">ปี ประสบการณ์ของทีมงานหลัก</div>'
        )
        content = content.replace(
            '<div class="stat-number">500+</div>\n                    <div class="stat-label">ลูกค้าองค์กร</div>',
            '<div class="stat-number">5,000+</div>\n                    <div class="stat-label">บ้านและโครงการที่เคยดูแล</div>'
        )
        content = content.replace(
            '<div class="stat-number">10,000+</div>\n                    <div class="stat-label">งานที่สำเร็จ</div>',
            '<div class="stat-number">100%</div>\n                    <div class="stat-label">ความสะอาดและใส่ใจสิ่งแวดล้อม</div>'
        )
        content = content.replace(
            '<div class="stat-number">98%</div>\n                    <div class="stat-label">ความพึงพอใจ</div>',
            '<div class="stat-number">99%</div>\n                    <div class="stat-label">ลูกค้าพึงพอใจและบอกต่อ</div>'
        )
        content = content.replace(
            '<div class="stat-number">500+</div>\n                    <div class="stat-label">ลูกค้าองค์กร</div>',
            '<div class="stat-number">5,000+</div>\n                    <div class="stat-label">บ้านและโครงการที่เคยดูแล</div>'
        )
        
        with open(big_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully aligned stats in {big_file}")

if __name__ == '__main__':
    align_stats()
