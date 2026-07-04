import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

image_pool = [
    'https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1563453392212-326f5e854473?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1524813686514-a57563d77965?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1502672260266-1c1f52d11f0d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1618221118493-9c874288b894?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1584622781564-1d8935470d0e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1518131672697-611eb14fc8c6?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1628177142856-07921c56f675?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1585421514738-01798e348b17?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1584820927508-0111f11cb209?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1595846519845-68e298c2cebc?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517520286827-0b1a03e1e699?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1583847268964-b28ce8f31586?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1600585154526-990dced4ea0d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542889601-399c4f3a8402?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&w=600&q=80'
]

valid = []
for url in image_pool:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
    try:
        urllib.request.urlopen(req, context=ctx)
        valid.append(url)
    except Exception as e:
        pass

with open('seo/content_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

valid_str = 'image_pool = [\n    ' + ',\n    '.join([f'"{u}"' for u in valid]) + '\n]'
new_content = re.sub(r'image_pool = \[.*?\]', valid_str, content, flags=re.DOTALL)

# Adjust the queue size if we have fewer images
if len(valid) < 21:
    new_queue_size = max(1, len(valid) - 2)
    new_content = re.sub(r'len\(last_used_images\) > 20', f'len(last_used_images) > {new_queue_size}', new_content)

with open('seo/content_generator.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Updated content_generator.py. Valid images: {len(valid)} / {len(image_pool)}")
