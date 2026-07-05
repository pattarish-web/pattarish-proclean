import os

gtag_code = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18299765093"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'AW-18299765093');
    </script>
"""

files = ['index.html', 'landing-bigcleaning.html', 'landing-maid.html', 'blog.html']

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if 'AW-18299765093' not in content:
            # Insert before </head>
            content = content.replace('</head>', gtag_code + '</head>')
            
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f'Added gtag to {f}')
        else:
            print(f'gtag already in {f}')
