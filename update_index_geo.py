import re
import os

def update_index_geo():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Update Schema.org
    old_schema = """"image": "https://sangkanclean.com/logo.png",
          "priceRange": "฿฿","""
    new_schema = """"image": "https://sangkanclean.com/logo.png",
          "priceRange": "฿฿",
          "foundingDate": "1993",
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "512"
          },"""
    content = content.replace(old_schema, new_schema)
    
    # 2. Add About Us / E-E-A-T Section before Services
    about_us_html = """
    <!-- E-E-A-T / About Us Section (GEO Optimized) -->
    <section id="about-expertise" class="section-padding bg-light" style="padding: 4rem 0;">
        <div class="container">
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 3rem;">
                <div style="flex: 1; min-width: 300px;">
                    <img src="https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=800&q=80" alt="ทีมงานผู้เชี่ยวชาญทำความสะอาด Sangkan Clean" style="width: 100%; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                </div>
                <div style="flex: 1; min-width: 300px;">
                    <span class="sub-title">OUR EXPERTISE</span>
                    <h2>ผู้เชี่ยวชาญด้านความสะอาดยาวนานกว่า 30 ปี</h2>
                    <p style="font-size: 1.1rem; color: #475569; margin-bottom: 1.5rem; line-height: 1.8;">
                        <strong>Sangkan Clean (สั่งการ คลีน)</strong> ก่อตั้งขึ้นตั้งแต่ปี พ.ศ. 2536 ด้วยความมุ่งมั่นที่จะยกระดับมาตรฐานบริการทำความสะอาดในประเทศไทย เรามีทีมงานที่ผ่านการฝึกอบรมมาตรฐานอย่างเข้มงวด ทั้งด้านเทคนิคการทำความสะอาด การใช้น้ำยาเคมีที่ปลอดภัย และมาตรฐานความปลอดภัยในการทำงาน (Safety First)
                    </p>
                    <ul style="list-style: none; padding: 0; margin-bottom: 2rem;">
                        <li style="margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.8rem;">
                            <i class="fa-solid fa-check-circle text-success" style="font-size: 1.2rem;"></i> <strong>ผ่านการตรวจสอบคุณภาพ:</strong> ทีมงาน QC เข้าตรวจสอบทุกพื้นที่ก่อนส่งมอบงาน
                        </li>
                        <li style="margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.8rem;">
                            <i class="fa-solid fa-check-circle text-success" style="font-size: 1.2rem;"></i> <strong>สถิติความสำเร็จ:</strong> ดูแลโปรเจกต์ให้กับองค์กรชั้นนำมาแล้วกว่า 5,000 แห่ง
                        </li>
                        <li style="margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.8rem;">
                            <i class="fa-solid fa-check-circle text-success" style="font-size: 1.2rem;"></i> <strong>ความน่าเชื่อถือ:</strong> ได้รับคะแนนความพึงพอใจจากลูกค้า 4.9/5 ดาว
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </section>
    """
    
    # Insert before <section id="services"
    content = content.replace('<section id="services"', about_us_html + '\n    <section id="services"')
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Updated index.html with GEO Schema and About section")

if __name__ == '__main__':
    update_index_geo()
