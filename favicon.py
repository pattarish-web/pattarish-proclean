import os
import re

files = ['index.html', 'landing-bigcleaning.html', 'landing-maid.html', 'blog.html']
favicon_tag = '    <link rel="icon" type="image/png" href="logo.png">\n'

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'rel="icon"' not in content:
            content = re.sub(r'(<head>)', r'\1\n' + favicon_tag, content, count=1)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
        print(f'Updated {f}')
