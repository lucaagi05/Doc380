import os
import glob
import re
from datetime import datetime

POSTS_DIR = "docs/blog/posts"
INDEX_FILE = "docs/blog/index.md"
BLOG_DIR = "docs/blog"

BACK_BUTTON_HTML = """
<style>
  .back-button {
    background-color: var(--md-primary-fg-color);
    color: white !important;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
    transition: background-color 0.3s, transform 0.2s;
    margin-top: 30px;
  }
  .back-button:hover {
    background-color: var(--md-accent-fg-color);
    transform: translateY(-2px);
    color: white !important;
  }
</style>
<a href="../../" class="back-button">Torna indietro</a>
"""

def get_posts():
    posts = []
    files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    
    for filename in files:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
            date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", content)
            if not date_match:
                continue
                
            post_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else os.path.basename(filename)
            
            base_name = os.path.splitext(os.path.basename(filename))[0]
            rel_path = f"posts/{base_name}/"
            
            posts.append({
                "date": post_date,
                "title": title,
                "path": rel_path
            })
            
    return sorted(posts, key=lambda x: x["date"])

def update_posts_with_back_button():
    files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    marker_start = "<!-- BACK_BUTTON_START -->"
    marker_end = "<!-- BACK_BUTTON_END -->"
    
    for filename in files:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        button_html = f"\n\n{marker_start}{BACK_BUTTON_HTML}\n{marker_end}\n"
        
        if marker_start in content and marker_end in content:
            # Replace existing button section
            new_content = re.sub(
                f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
                f"{marker_start}{BACK_BUTTON_HTML}\n{marker_end}",
                content,
                flags=re.DOTALL
            ).strip() + "\n"
        else:
            # Append new button section
            new_content = content.strip() + button_html
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)

def generate_pages():
    posts = get_posts()
    
    # Group by year
    years = {}
    for post in posts:
        year = str(post["date"].year)
        if year not in years:
            years[year] = []
        years[year].append(post)
        
    sorted_years = sorted(years.keys(), reverse=True)
    
    # 1. Generate index.md
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("# Blog\n\n")
        f.write("Seleziona un anno per leggere i post:\n\n")
        for year in sorted_years:
            f.write(f"- [{year}]({year}.md)\n")
            
    # 2. Generate year pages
    for year in sorted_years:
        year_file = os.path.join(BLOG_DIR, f"{year}.md")
        year_posts = years[year]
        
        def get_post_num(title):
            match = re.search(r"#(\d+)", title)
            return int(match.group(1)) if match else 0
            
        year_posts = sorted(year_posts, key=lambda x: get_post_num(x["title"]))
        
        with open(year_file, "w", encoding="utf-8") as f:
            f.write(f"# Blog: Anno {year}\n\n")
            
            f.write('<style>\n')
            f.write('  .sort-button {\n')
            f.write('    background-color: var(--md-primary-fg-color);\n')
            f.write('    color: var(--md-primary-bg-color);\n')
            f.write('    padding: 8px 16px;\n')
            f.write('    border: none;\n')
            f.write('    border-radius: 4px;\n')
            f.write('    cursor: pointer;\n')
            f.write('    font-weight: bold;\n')
            f.write('    margin-bottom: 20px;\n')
            f.write('    transition: background-color 0.3s, transform 0.2s;\n')
            f.write('  }\n')
            f.write('  .sort-button:hover {\n')
            f.write('    background-color: var(--md-accent-fg-color);\n')
            f.write('    transform: translateY(-2px);\n')
            f.write('  }\n')
            f.write('  .post-list {\n')
            f.write('    list-style-type: disc;\n')
            f.write('    padding-left: 20px;\n')
            f.write('  }\n')
            f.write('  .post-list li {\n')
            f.write('    margin-bottom: 10px;\n')
            f.write('  }\n')
            f.write('  .post-list a {\n')
            f.write('    color: var(--md-typeset-a-color);\n')
            f.write('    text-decoration: none;\n')
            f.write('    font-weight: bold;\n')
            f.write('  }\n')
            f.write('  .post-list a:hover {\n')
            f.write('    text-decoration: underline;\n')
            f.write('  }\n')
            f.write('</style>\n\n')
            
            f.write('<button id="sortBtn" class="sort-button" onclick="toggleSort()">Ordina: Decrescente</button>\n\n')
            
            f.write('<ul id="postList" class="post-list">\n')
            for post in year_posts:
                date_str = post["date"].strftime("%Y-%m-%d")
                f.write(f'  <li><a href="../{post["path"]}">{post["title"]}</a> <span style="color: gray; font-size: 0.9em;">({date_str})</span></li>\n')
            f.write('</ul>\n\n')
            
            f.write('''<script>
function toggleSort() {
    const btn = document.getElementById('sortBtn');
    const list = document.getElementById('postList');
    const items = Array.from(list.children);
    
    items.reverse();
    list.innerHTML = '';
    items.forEach(item => list.appendChild(item));
    
    const isDescending = btn.textContent.includes('Decrescente');
    btn.textContent = isDescending ? 'Ordina: Crescente' : 'Ordina: Decrescente';
}
</script>\n''')

if __name__ == "__main__":
    update_posts_with_back_button()
    generate_pages()
    print("✓ Pagine del blog generate e post aggiornati con successo!")
