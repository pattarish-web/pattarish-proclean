import os
import re

def reorder():
    filename = 'index.html'
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return
        
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract certifications section
    # Starts with <!-- E-E-A-T / About Us Section (GEO Optimized) -->\n    <!-- Partner & Certifications Section -->
    # Ends with </section>\n
    cert_pattern = re.compile(
        r'    <!-- E-E-A-T / About Us Section \(GEO Optimized\) -->\n    <!-- Partner & Certifications Section -->.*?    </section>\n',
        re.DOTALL
    )
    
    match = cert_pattern.search(content)
    if not match:
        print("Could not locate Certifications section in index.html")
        return
        
    cert_section_text = match.group(0)
    
    # 2. Remove certifications section from its current place
    content = content.replace(cert_section_text, "")
    
    # 3. Insert certifications section after the services section
    # The services section ends with:
    #     </section>\n\n    <!-- Why Choose Us (แบบ number1cleaningservices.com) -->
    target_marker = '    </section>\n\n    <!-- Why Choose Us (แบบ number1cleaningservices.com) -->'
    
    if target_marker in content:
        replacement = '    </section>\n\n' + cert_section_text + '\n    <!-- Why Choose Us (แบบ number1cleaningservices.com) -->'
        content = content.replace(target_marker, replacement)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully reordered index.html: Certifications is now after Services!")
    else:
        print("Could not find insertion marker after Services section")

if __name__ == '__main__':
    reorder()
