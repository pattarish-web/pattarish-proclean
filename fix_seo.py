import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix SangkanClean LINE links to standard https://line.me/ti/p/@sangkanclean
    content = re.sub(r'https?://(?:www\.)?line\.me/(?:R/)?ti/p/(?:@|@@|%40)SangkanClean', 'https://line.me/ti/p/@sangkanclean', content, flags=re.IGNORECASE)
    
    # Fix Netlify old URLs for og:image and twitter:image
    content = content.replace('https://sangkan-cleaning.netlify.app/logo.png', 'https://sangkanclean.com/logo.png')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for filename in os.listdir('.'):
    if filename.endswith('.html'):
        fix_file(filename)
