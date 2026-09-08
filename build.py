import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import markdown
import yaml

SITE_DIR = Path(__file__).parent.resolve()
POSTS_DIR = SITE_DIR / "posts"
DIST_DIR = SITE_DIR / "dist"
ASSETS_DIR = SITE_DIR / "assets"

def parse_markdown(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as f:
        raw_text = f.read()
    
    meta = {}
    content = raw_text
    
    # Check for YAML front matter
    stripped_text = raw_text.lstrip()
    if stripped_text.startswith("---"):
        parts = stripped_text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                content = parts[2].strip()
            except Exception as e:
                print(f"Warning: Failed to parse front matter in {file_path.name}: {e}")
    
    # Fallback title if not provided
    if "title" not in meta or not meta["title"]:
        first_line = content.strip().split("\n")[0]
        if first_line.startswith("# "):
            meta["title"] = first_line.lstrip("# ").strip()
            content = content[len(first_line):].strip()
        else:
            meta["title"] = file_path.stem

    # Fallback date if not provided
    if "date" not in meta or not meta["date"]:
        # Try finding date in filename like 2024-01-30-xxx.md
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", file_path.stem)
        if match:
            meta["date"] = match.group(1)
        else:
            meta["date"] = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
    elif isinstance(meta["date"], (datetime, )):
        meta["date"] = meta["date"].strftime("%Y-%m-%d")
    else:
        meta["date"] = str(meta["date"])

    # Determine year from date (e.g. 2024 from '2024-01-30')
    year = meta["date"][:4] if meta.get("date") and len(str(meta["date"])) >= 4 else "misc"
    slug = file_path.stem
    output_rel = f"posts/{year}/{slug}.html"

    # Convert markdown to html with code highlighting
    md_converter = markdown.Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc"
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False
            }
        }
    )
    html_body = md_converter.convert(content)
    
    return {
        "title": meta["title"],
        "date": meta["date"],
        "slug": slug,
        "url": f"/{output_rel}",
        "output_path": DIST_DIR / output_rel,
        "content_html": html_body,
        "meta": meta
    }

BUILD_VERSION = int(datetime.now().timestamp())

def get_base_html(title, content_html, is_root=False):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <script>
    (function() {{
      var saved = localStorage.getItem('theme');
      if (saved) {{
        document.documentElement.setAttribute('data-theme', saved);
      }}
    }})();
  </script>
  <link rel="stylesheet" type="text/css" href="/assets/main.css?v={BUILD_VERSION}">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
          onload="renderMathInElement(document.body, {{
            delimiters: [
              {{left: '$$', right: '$$', display: true}},
              {{left: '$', right: '$', display: false}}
            ],
            throwOnError: false
          }});"></script>
</head>
<body>
  <div class="container">
    <header>
      <nav class="menu" aria-label="Main Navigation">
        <ul>
          <li><a href="/">/root</a></li>
          <li><a href="/archive.html">/archive</a></li>
          <li><a href="/about/">/about</a></li>
        </ul>
        <button id="theme-btn" class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle Theme">[auto]</button>
      </nav>
    </header>
    <main>
      {content_html}
    </main>
    <footer>
      <p>学无止境.</p>
    </footer>
  </div>
  <script>
    function toggleTheme() {{
      var current = document.documentElement.getAttribute('data-theme');
      var isDark = current === 'dark' || (!current && window.matchMedia('(prefers-color-scheme: dark)').matches);
      var next = isDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeBtn();
    }}
    function updateThemeBtn() {{
      var btn = document.getElementById('theme-btn');
      if (!btn) return;
      var current = document.documentElement.getAttribute('data-theme');
      if (!current) {{
        var isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        btn.textContent = isDark ? '[dark]' : '[light]';
      }} else {{
        btn.textContent = current === 'dark' ? '[dark]' : '[light]';
      }}
    }}
    updateThemeBtn();
  </script>
</body>
</html>
"""

def build():
    print("Building site...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    posts_dist = DIST_DIR / "posts"
    if posts_dist.exists():
        shutil.rmtree(posts_dist, ignore_errors=True)
    posts_dist.mkdir(parents=True, exist_ok=True)

    # Copy assets
    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, DIST_DIR / "assets", dirs_exist_ok=True)
        print("Copied assets.")

    # Copy about or create about
    about_src = SITE_DIR / "about"
    if about_src.exists():
        shutil.copytree(about_src, DIST_DIR / "about", dirs_exist_ok=True)
    
    # Copy 404
    if (SITE_DIR / "404.html").exists():
        shutil.copy(SITE_DIR / "404.html", DIST_DIR / "404.html")

    # Read all posts (supports subdirectories like posts/2024/, posts/2026/, etc.)
    posts = []
    if POSTS_DIR.exists():
        for md_file in POSTS_DIR.rglob("*.md"):
            post = parse_markdown(md_file)
            posts.append(post)

    # Sort posts by date descending
    posts.sort(key=lambda p: p["date"], reverse=True)
    print(f"Found {len(posts)} posts.")

    # Generate individual post pages
    for post in posts:
        article_html = f"""<article>
  <h1>{post['title']}</h1>
  <p style="color: #666; font-size: 16px; margin-bottom: 20px;">[ 发布于 {post['date']} ]</p>
  {post['content_html']}
</article>"""
        full_html = get_base_html(f"{post['title']} - /root", article_html)
        post["output_path"].parent.mkdir(parents=True, exist_ok=True)
        with open(post["output_path"], "w", encoding="utf-8") as f:
            f.write(full_html)

    # Generate index.html (Root)
    index_items = []
    for post in posts:
        index_items.append(f'<li>- [ {post["date"]} ] <a href="{post["url"]}">{post["title"]}</a></li>')
    index_list_html = "\n        ".join(index_items) if index_items else "<li>暂无文章</li>"
    
    index_content = f"""<ul>
        {index_list_html}
      </ul>"""
    index_html = get_base_html("/root", index_content, is_root=True)
    with open(DIST_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("Generated index.html.")

    # Generate archive.html
    # Group by year
    years = {}
    for post in posts:
        year = post["date"][:4]
        years.setdefault(year, []).append(post)

    archive_sections = []
    for year in sorted(years.keys(), reverse=True):
        items = []
        for post in years[year]:
            items.append(f'<li>- <time>{post["date"]} - </time><a href="{post["url"]}">{post["title"]}</a></li>')
        items_html = "\n        ".join(items)
        archive_sections.append(f"""<section>
      <h3>{year}</h3>
      <ul>
        {items_html}
      </ul>
    </section>""")
    
    archive_content = "\n    ".join(archive_sections)
    archive_html = get_base_html("Archive - /root", archive_content)
    with open(DIST_DIR / "archive.html", "w", encoding="utf-8") as f:
        f.write(archive_html)
    print("Generated archive.html.")

    print("Site build completed successfully into dist/!")

if __name__ == "__main__":
    import sys
    build()
    if "--serve" in sys.argv:
        import http.server
        import socketserver
        from functools import partial
        PORT = 8000
        handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST_DIR))
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"\n[Preview Server] Serving at http://localhost:{PORT}")
            print("Press Ctrl+C to stop.")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
