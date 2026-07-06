import json
import os

with open('posts.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

latest = list(reversed(posts[-3:]))
html = ""
for p in latest:
    html += f"""                <article class="article-card">
                    <div class="article-img">
                        <img src="{p['image']}" alt="{p['title']}">
                        <span class="article-tag">{p['category']}</span>
                    </div>
                    <div class="article-body">
                        <h3>{p['title']}</h3>
                        <p>{p['description']}</p>
                        <a href="blog/{p['slug']}.html" class="read-more">อ่านต่อ <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </article>\n"""

with open('latest_posts.html', 'w', encoding='utf-8') as f:
    f.write(html)
