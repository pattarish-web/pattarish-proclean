import os

def add_certs():
    filename = 'index.html'
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return
        
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the new Certifications Section HTML
    certs_html = """    <!-- E-E-A-T / About Us Section (GEO Optimized) -->"""
    
    new_section = """    <!-- E-E-A-T / About Us Section (GEO Optimized) -->
    <!-- Partner & Certifications Section -->
    <section id="certifications" class="section-padding" style="padding: 5rem 0; background: #ffffff; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;">
        <div class="container text-center">
            <span class="sub-title">STANDARD & SAFETY</span>
            <h2 style="margin-bottom: 1.5rem; font-size: 2rem;">มาตรฐานเคมีภัณฑ์และความปลอดภัยที่เราเลือกใช้</h2>
            <p style="max-width: 800px; margin: 0 auto 3.5rem; color: #475569; font-size: 1.1rem; line-height: 1.8;">
                Sangkan Clean ใส่ใจในสุขอนามัยและความปลอดภัยสูงสุดของสมาชิกทุกท่านในบ้านและสำนักงาน เราจึงร่วมมือกับพันธมิตรผู้ผลิตเคมีภัณฑ์ชั้นนำ <strong>SevenSave (แบรนด์ Greenmind)</strong> ที่ได้รับรองมาตรฐานสากลและควบคุมการปนเปื้อน 100%
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2rem; justify-items: center; align-items: stretch; margin-bottom: 3.5rem;">
                <!-- SGS ISO 9001 -->
                <div style="padding: 2rem 1.5rem; border-radius: 16px; background: #f8fafc; border: 1px solid #e2e8f0; width: 100%; max-width: 260px; transition: transform 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="font-size: 3rem; color: #ea580c; margin-bottom: 1.2rem;"><i class="fa-solid fa-check-double"></i></div>
                    <h4 style="margin-bottom: 0.5rem; font-size: 1.2rem; color: #0f172a;">SGS ISO 9001:2015</h4>
                    <p style="font-size: 0.95rem; color: #64748b; line-height: 1.5; margin: 0;">มาตรฐานสากลการจัดระบบการทำงานและคุณภาพการผลิตเคมีภัณฑ์</p>
                </div>
                <!-- BSI ISO 14001 -->
                <div style="padding: 2rem 1.5rem; border-radius: 16px; background: #f8fafc; border: 1px solid #e2e8f0; width: 100%; max-width: 260px; transition: transform 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="font-size: 3rem; color: #16a34a; margin-bottom: 1.2rem;"><i class="fa-solid fa-leaf"></i></div>
                    <h4 style="margin-bottom: 0.5rem; font-size: 1.2rem; color: #0f172a;">BSI ISO 14001:2015</h4>
                    <p style="font-size: 0.95rem; color: #64748b; line-height: 1.5; margin: 0;">มาตรฐานระบบการจัดการสิ่งแวดล้อม ปลอดภัยต่อธรรมชาติ</p>
                </div>
                <!-- SGS GHPs -->
                <div style="padding: 2rem 1.5rem; border-radius: 16px; background: #f8fafc; border: 1px solid #e2e8f0; width: 100%; max-width: 260px; transition: transform 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="font-size: 3rem; color: #0284c7; margin-bottom: 1.2rem;"><i class="fa-solid fa-shield-virus"></i></div>
                    <h4 style="margin-bottom: 0.5rem; font-size: 1.2rem; color: #0f172a;">SGS GHPs Standard</h4>
                    <p style="font-size: 0.95rem; color: #64748b; line-height: 1.5; margin: 0;">มาตรฐานสุขอนามัยที่ดี ปลอดภัยระดับโรงพยาบาลและโรงแรมชั้นนำ</p>
                </div>
                <!-- Green Industry & TGO -->
                <div style="padding: 2rem 1.5rem; border-radius: 16px; background: #f8fafc; border: 1px solid #e2e8f0; width: 100%; max-width: 260px; transition: transform 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="font-size: 3rem; color: #059669; margin-bottom: 1.2rem;"><i class="fa-solid fa-seedling"></i></div>
                    <h4 style="margin-bottom: 0.5rem; font-size: 1.2rem; color: #0f172a;">Green Industry & TGO</h4>
                    <p style="font-size: 0.95rem; color: #64748b; line-height: 1.5; margin: 0;">อุตสาหกรรมสีเขียวระดับ 3 และฉลากลดคาร์บอนฟุตพริ้นท์รักษ์โลก</p>
                </div>
            </div>
            
            <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 2rem; padding: 1.5rem; background: #f1f5f9; border-radius: 12px; max-width: 800px; margin: 0 auto;">
                <div style="font-size: 1.5rem; color: #475569;"><i class="fa-solid fa-circle-info"></i></div>
                <div style="text-align: left; font-size: 0.95rem; color: #475569; line-height: 1.6;">
                    <strong>การรับรองเพิ่มเติมระดับประเทศ:</strong> เคมีภัณฑ์ทั้งหมดที่เลือกใช้ผ่านการจดทะเบียนรับรองจาก <strong>สำนักงานคณะกรรมการอาหารและยา (อย.)</strong>, <strong>กรมปศุสัตว์</strong>, <strong>Made in Thailand (MiT)</strong> และผ่านเกณฑ์การประเมินด้านความรับผิดชอบต่อสังคม <strong>CSR-DIW</strong>
                </div>
            </div>
        </div>
    </section>"""
    
    if certs_html in content:
        # Avoid double adding if already run
        if 'Partner & Certifications Section' not in content:
            content = content.replace(certs_html, new_section)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully added Partner & Certifications Section to index.html")
        else:
            print("Section already exists in index.html")
    else:
        print("Could not find insertion marker in index.html")

if __name__ == '__main__':
    add_certs()
