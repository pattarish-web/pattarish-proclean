import os
from bs4 import BeautifulSoup

def analyze_seo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    score = 0
    max_score = 100
    report = []
    
    # 1. Title
    title = soup.find('title')
    if title and len(title.text) > 10:
        score += 10
        report.append("✅ (10/10) Title tag exists and has good length")
    else:
        report.append("❌ (0/10) Missing or short Title tag")
        
    # 2. Meta Description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and len(meta_desc.get('content', '')) > 30:
        score += 10
        report.append("✅ (10/10) Meta description exists and is well detailed")
    else:
        report.append("❌ (0/10) Missing or short Meta description")
        
    # 3. Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical and canonical.get('href'):
        score += 10
        report.append("✅ (10/10) Canonical URL is configured correctly")
    else:
        report.append("❌ (0/10) Missing Canonical URL")
        
    # 4. Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        score += 10
        report.append("✅ (10/10) Social Media Open Graph (OG) tags exist")
    else:
        report.append("❌ (0/10) Missing OG tags")
        
    # 5. Schema.org
    schema = soup.find('script', attrs={'type': 'application/ld+json'})
    if schema:
        score += 10
        report.append("✅ (10/10) Schema.org Structured Data exists")
    else:
        report.append("❌ (0/10) Missing Schema.org JSON-LD")
        
    # 6. H1 Tag
    h1s = soup.find_all('h1')
    if len(h1s) == 1:
        score += 10
        report.append("✅ (10/10) Exactly one H1 tag found (Best Practice)")
    else:
        report.append(f"❌ (0/10) Found {len(h1s)} H1 tags (Should be exactly 1)")
        
    # 7. Image Alt text
    images = soup.find_all('img')
    images_without_alt = [img for img in images if not img.get('alt')]
    if len(images_without_alt) == 0 and len(images) > 0:
        score += 10
        report.append("✅ (10/10) All images have 'alt' attributes")
    else:
        report.append(f"❌ (0/10) Missing 'alt' on {len(images_without_alt)} images")
        
    # 8. Viewport
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        score += 10
        report.append("✅ (10/10) Mobile Viewport tag exists")
    else:
        report.append("❌ (0/10) Missing Viewport tag")
        
    # 9. HTML Lang
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        score += 10
        report.append("✅ (10/10) HTML lang attribute specified")
    else:
        report.append("❌ (0/10) Missing HTML lang attribute")
        
    # 10. CSS/JS optimization (Inline style check)
    style_tags = soup.find_all('style')
    if len(style_tags) == 0:
        score += 10
        report.append("✅ (10/10) No inline <style> blocks (Good for caching/speed)")
    else:
        score += 5
        report.append(f"⚠️ (5/10) Found {len(style_tags)} inline <style> blocks. Consider moving to CSS file.")
        
    print(f"Overall SEO Score for {filepath}: {score}/{max_score}")
    print("\n".join(report))

if __name__ == '__main__':
    print("--- INDEX.HTML ---")
    analyze_seo('index.html')
