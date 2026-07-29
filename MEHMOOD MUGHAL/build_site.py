import os
import re
import sys
import subprocess

# --------------------------------------------------------------------------
# DEPENDENCY MANAGER
# --------------------------------------------------------------------------
try:
    import markdown
except ImportError:
    print("Installing 'markdown' library for HTML conversion...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
    except Exception as e:
        print(f"Failed to install markdown automatically: {e}")
        print("Please install it manually using: pip install markdown")
        sys.exit(1)

# --------------------------------------------------------------------------
# CONSTANTS & PATHS
# --------------------------------------------------------------------------
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(DIRECTORY, 'articles')

# Ensure articles folder exists
os.makedirs(ARTICLES_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------------
def parse_md(filepath):
    """
    Parses a markdown file to extract front-matter YAML metadata and the body.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match YAML front matter between dashes
    match = re.match(r'^---\r?\n([\s\S]*?)\r?\n---', content)
    metadata = {}
    body = content
    
    if match:
        yaml_content = match.group(1)
        body = content[match.end():].strip()
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                metadata[key] = val
    return metadata, body

def clean_snippet(text):
    """
    Generates a short preview snippet from the raw text body.
    """
    clean = re.sub(r'[#\*_`\[\]\-]', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:180] + '...' if len(clean) > 180 else clean

def parse_filename(filename):
    """
    Fallback parser extracting metadata from the filename itself.
    """
    name_without_ext = re.sub(r'\.md$', '', filename)
    parts = name_without_ext.split(' - ')
    if len(parts) >= 2:
        date_part = parts[0].strip()
        title_part = ' - '.join(parts[1:]).strip()
        date_words = date_part.split(' ')
        day_of_week = date_words[0]
        date_str = ' '.join(date_words[1:]) if len(date_words) > 1 else date_part
        return {
            'dayOfWeek': day_of_week,
            'date': date_str,
            'title': title_part
        }
    return {
        'dayOfWeek': '',
        'date': '',
        'title': name_without_ext
    }

# --------------------------------------------------------------------------
# CSS & JS TEMPLATE CONTENT
# --------------------------------------------------------------------------
STYLE_CSS = """/* Shared CSS for Mehmood Mughal Static Archive */
:root {
  --font-ui: 'Tajawal', system-ui, sans-serif;
  --font-read-lateef: 'Lateef', serif;
  --font-read-amiri: 'Amiri', serif;
  --font-read-noto: 'Noto Naskh Arabic', serif;
  --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-sm: 0 2px 5px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 15px rgba(0,0,0,0.08);
}

/* Themes */
body.theme-light {
  --bg-app: #f5f6f8;
  --bg-card: #ffffff;
  --bg-hover: #f0f2f5;
  --text-primary: #1e2022;
  --text-secondary: #626875;
  --text-muted: #8e95a5;
  --primary: #9b2c2c;
  --primary-hover: #7b2020;
  --border: #e2e8f0;
}

body.theme-sepia {
  --bg-app: #ebe1cd;
  --bg-card: #fbf5e6;
  --bg-hover: #f3e9d2;
  --text-primary: #433422;
  --text-secondary: #6e5b44;
  --text-muted: #958169;
  --primary: #8a3219;
  --primary-hover: #6e2713;
  --border: #e8dcc4;
}

body.theme-dark {
  --bg-app: #0f0f11;
  --bg-card: #18181c;
  --bg-hover: #22222a;
  --text-primary: #e6e6eb;
  --text-secondary: #a2a2b0;
  --text-muted: #6b6b7a;
  --primary: #f26b5b;
  --primary-hover: #f58476;
  --border: #292932;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-ui);
  background-color: var(--bg-app);
  color: var(--text-primary);
  direction: rtl;
  min-height: 100vh;
  padding: 0;
  transition: background-color var(--transition-normal), color var(--transition-normal);
}

a {
  color: inherit;
  text-decoration: none;
}

/* Container */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* Header & Profile */
.main-header {
  text-align: center;
  margin-bottom: 40px;
}

.author-badge {
  display: inline-flex;
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  color: white;
  border-radius: 20px;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  box-shadow: var(--shadow-md);
  margin-bottom: 15px;
}

.main-header h1 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
}

.main-header p {
  color: var(--text-secondary);
  font-size: 15px;
}

/* Nav Toolbar (Theme Switcher, Back button) */
.nav-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  padding: 12px 24px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: var(--shadow-sm);
}

.toolbar-title {
  font-weight: 700;
  font-size: 16px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
  transition: transform 0.2s ease;
}
.btn-back:hover {
  transform: translateX(4px);
}

.theme-controls {
  display: flex;
  gap: 8px;
}

.theme-btn {
  background-color: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  font-family: var(--font-ui);
  transition: all 0.2s ease;
}
.theme-btn:hover {
  border-color: var(--primary);
}
.theme-btn.active {
  background-color: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* Search and Filters */
.search-filter-section {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-wrapper {
  position: relative;
}

.search-wrapper input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background-color: var(--bg-app);
  color: var(--text-primary);
  outline: none;
  font-family: var(--font-ui);
  font-size: 15px;
  transition: border-color 0.2s ease;
}

.search-wrapper input:focus {
  border-color: var(--primary);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-btn {
  background-color: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-btn:hover, .filter-btn.active {
  background-color: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* Article Cards list */
.cards-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: block;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.card-title {
  font-family: var(--font-read-amiri);
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.4;
}

.card-date {
  font-size: 13px;
  color: var(--text-muted);
  white-space: nowrap;
}

.card-snippet {
  font-family: var(--font-read-lateef);
  font-size: 19px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--text-muted);
}

.card-meta-tag {
  background-color: var(--bg-hover);
  padding: 4px 10px;
  border-radius: 6px;
}

/* Reading View Specifics */
.reading-pane {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  padding: 45px 35px;
  border-radius: 16px;
  box-shadow: var(--shadow-md);
}

.article-meta-header {
  margin-bottom: 30px;
  border-bottom: 2px dashed var(--border);
  padding-bottom: 20px;
}

.article-heading {
  font-family: var(--font-read-amiri);
  font-size: 36px;
  font-weight: 800;
  line-height: 1.4;
  margin-bottom: 15px;
}

.meta-info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: var(--text-secondary);
}

.meta-link {
  color: var(--primary);
  font-weight: 500;
}
.meta-link:hover {
  text-decoration: underline;
}

.article-body {
  font-family: var(--font-read-lateef);
  font-size: 24px;
  line-height: 1.8;
  color: var(--text-primary);
  text-align: justify;
}

.article-body p {
  margin-bottom: 1.8em;
  text-indent: 1.2em;
}

.article-body h2 {
  font-family: var(--font-read-amiri);
  font-size: 28px;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  color: var(--primary);
}

.article-body blockquote {
  border-right: 4px solid var(--primary);
  padding: 10px 20px;
  margin: 20px 0;
  background-color: var(--bg-hover);
  color: var(--text-secondary);
  font-style: italic;
  border-radius: 4px;
}

.article-footer {
  margin-top: 50px;
  border-top: 1px solid var(--border);
  padding-top: 30px;
}

.bio-card {
  display: flex;
  gap: 16px;
  align-items: center;
  background-color: var(--bg-hover);
  padding: 20px;
  border-radius: 12px;
}

.bio-avatar {
  width: 50px;
  height: 50px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.bio-details h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.bio-details p {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .container {
    padding: 20px 10px;
  }
  .reading-pane {
    padding: 25px 15px;
  }
  .card-header-row {
    flex-direction: column;
    gap: 4px;
  }
  .article-heading {
    font-size: 28px;
  }
  .article-body {
    font-size: 21px;
    text-align: right;
  }
}
"""

THEME_SCRIPT = """<script>
// Load Theme preference
const savedTheme = localStorage.getItem('mm_theme_static') || 'theme-sepia';
document.body.className = savedTheme;

// Setup active button highlight if in DOM
document.addEventListener('DOMContentLoaded', () => {
  const activeBtn = document.querySelector(`.theme-btn[data-theme="${savedTheme}"]`);
  if (activeBtn) activeBtn.classList.add('active');
});

function changeTheme(themeName) {
  document.body.className = themeName;
  localStorage.setItem('mm_theme_static', themeName);
  
  // Highlight active button
  document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.querySelector(`.theme-btn[data-theme="${themeName}"]`);
  if (activeBtn) activeBtn.classList.add('active');
}
</script>"""

# --------------------------------------------------------------------------
# PAGE TEMPLATES (Safe Plain Strings)
# --------------------------------------------------------------------------
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="sd" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}} - محمود مغل</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Lateef&family=Noto+Naskh+Arabic:wght@400;700&family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="../style.css?v=2.0">
</head>
<body class="theme-sepia">
  <div class="container">
    <nav class="nav-toolbar">
      <a href="../index.html" class="btn-back">
        <span>← فهرست ڏانهن واپس</span>
      </a>
      
      <div class="theme-controls">
        <button class="theme-btn" data-theme="theme-light" onclick="changeTheme('theme-light')">اڇو</button>
        <button class="theme-btn" data-theme="theme-sepia" onclick="changeTheme('theme-sepia')">سيميا</button>
        <button class="theme-btn" data-theme="theme-dark" onclick="changeTheme('theme-dark')">تاريڪ</button>
      </div>
    </nav>

    <main class="reading-pane">
      <header class="article-meta-header">
        <h1 class="article-heading">{{TITLE}}</h1>
        <div class="meta-info-row">
          <span>📅 {{DATE}}</span>
          <span>⏱️ {{READ_TIME}} منٽ پڙهڻ جو وقت</span>
          {{ORIGINAL_URL}}
        </div>
      </header>

      <article class="article-body">
        {{BODY}}
      </article>

      <footer class="article-footer">
        <div class="bio-card">
          <div class="bio-avatar">MM</div>
          <div class="bio-details">
            <h4>محمود مغل</h4>
            <p>سنڌي ادب جو نامور ڪالم نگار ۽ ڪهاڻيڪار، جنهن جي تحريرن ۾ روزمره جي جيون جا رنگ ۽ سماجي سچايون نمايان هونديون آهن.</p>
          </div>
        </div>
      </footer>
    </main>
  </div>

  {{THEME_SCRIPT}}
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="sd" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>محمود مغل - مضمون ۽ مقالا</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Lateef&family=Noto+Naskh+Arabic:wght@400;700&family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css?v=2.0">
</head>
<body class="theme-sepia">
  <div class="container">
    <header class="main-header">
      <div class="author-badge">MM</div>
      <h1>محمود مغل جي ادبي دنيا</h1>
      <p>ڪاوش اخبار ۾ ڇپيل مضمونن ۽ مقالن جو خوبصورت سنگهه</p>
    </header>

    <nav class="nav-toolbar">
      <div class="toolbar-title">سڀ مضمون ({{TOTAL_COUNT}})</div>
      <div class="theme-controls">
        <button class="theme-btn" data-theme="theme-light" onclick="changeTheme('theme-light')">اڇو</button>
        <button class="theme-btn" data-theme="theme-sepia" onclick="changeTheme('theme-sepia')">سيميا</button>
        <button class="theme-btn" data-theme="theme-dark" onclick="changeTheme('theme-dark')">تاريڪ</button>
      </div>
    </nav>

    <section class="search-filter-section">
      <div class="search-wrapper">
        <input type="text" id="searchInput" placeholder="ڳولا ڪريو... (عنوان يا ڪي ورڊ)" oninput="filterList()">
      </div>
      
      <div class="filter-row">
        <button class="filter-btn active" id="btnAll" onclick="filterYear('all')">سڀ سال</button>
        {{YEAR_FILTERS}}
      </div>
    </section>

    <main class="cards-list" id="cardsList">
      {{CARDS}}
    </main>
  </div>

  {{THEME_SCRIPT}}
  
  <script>
  let activeYear = 'all';
  
  function filterYear(year) {
    activeYear = year;
    
    // Toggle active classes on buttons
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (year === 'all') {
      document.getElementById('btnAll').classList.add('active');
    } else {
      // Find the specific button
      const buttons = document.querySelectorAll('.filter-btn');
      buttons.forEach(btn => {
        if (btn.textContent === year + 'ع') {
          btn.classList.add('active');
        }
      });
    }
    
    filterList();
  }
  
  function filterList() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.article-card');
    
    cards.forEach(card => {
      const title = card.getAttribute('data-title');
      const snippet = card.getAttribute('data-snippet');
      const year = card.getAttribute('data-year');
      
      const matchesSearch = !query || title.includes(query) || snippet.includes(query);
      const matchesYear = activeYear === 'all' || year === activeYear;
      
      if (matchesSearch && matchesYear) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }
  </script>
</body>
</html>
"""

# --------------------------------------------------------------------------
# MAIN BUILD SEQUENCE
# --------------------------------------------------------------------------
def main():
    print("Static Site Generator: Scanning directories...")
    
    # 1. Get MD files
    files = [f for f in os.listdir(DIRECTORY) if f.endswith('.md') and f not in ['README.md', 'SKILL.md', 'AGENTS.md']]
    print(f"Found {len(files)} markdown articles.")
    
    # Write style.css
    with open(os.path.join(DIRECTORY, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(STYLE_CSS)
    print("Generated style.css")
    
    articles_data = []
    
    # 2. Process each file
    for idx, filename in enumerate(files):
        filepath = os.path.join(DIRECTORY, filename)
        metadata, body = parse_md(filepath)
        filename_meta = parse_filename(filename)
        
        title = metadata.get('title') or filename_meta['title']
        date = metadata.get('date') or filename_meta['date']
        year = metadata.get('year') or (re.search(r'\d{4}', date).group(0) if re.search(r'\d{4}', date) else '')
        day_of_week = filename_meta['dayOfWeek']
        url = metadata.get('url') or ''
        
        snippet = clean_snippet(body)
        word_count = len(body.split())
        read_time = max(1, round(word_count / 180))
        
        # Output URL filename using safe slug format: art_1.html, art_2.html, etc.
        art_id = idx + 1
        html_filename = f"art_{art_id}.html"
        html_filepath = os.path.join(ARTICLES_DIR, html_filename)
        
        # Convert Markdown body to HTML
        body_html = markdown.markdown(body)
        
        # Assemble standalone page using string replacements (no f-string format errors)
        orig_url_html = f'<span>🔗 <a href="{url}" class="meta-link" target="_blank" rel="noopener">ڪاوش اخبار تي اصل مضمون</a></span>' if url else ''
        
        page_html = ARTICLE_TEMPLATE
        page_html = page_html.replace('{{TITLE}}', title)
        page_html = page_html.replace('{{DATE}}', date)
        page_html = page_html.replace('{{READ_TIME}}', str(read_time))
        page_html = page_html.replace('{{ORIGINAL_URL}}', orig_url_html)
        page_html = page_html.replace('{{BODY}}', body_html)
        page_html = page_html.replace('{{THEME_SCRIPT}}', THEME_SCRIPT)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(page_html)
            
        articles_data.append({
            'id': art_id,
            'title': title,
            'date': date,
            'year': year,
            'dayOfWeek': day_of_week,
            'snippet': snippet,
            'readTime': read_time,
            'link': f"articles/{html_filename}"
        })
        
    # Sort articles reverse-chronologically by year first
    articles_data.sort(key=lambda x: (x['year'], x['date']), reverse=True)
    
    # 3. Generate index.html
    # Get unique years for the filter pills
    years = sorted(list(set([a['year'] for a in articles_data if a['year']])), reverse=True)
    year_filters_html = "\n".join([
        f'<button class="filter-btn" onclick="filterYear(\'{y}\')">{y}ع</button>' for y in years
    ])
    
    # Render all articles into HTML cards
    cards_html = ""
    for art in articles_data:
        cards_html += f"""
      <a href="{art['link']}" class="article-card" data-title="{art['title'].lower()}" data-year="{art['year']}" data-day="{art['dayOfWeek']}" data-snippet="{art['snippet'].lower()}">
        <div class="card-header-row">
          <h2 class="card-title">{art['title']}</h2>
          <span class="card-date">{art['date']}</span>
        </div>
        <p class="card-snippet">{art['snippet']}</p>
        <div class="card-footer">
          <span>⏱️ {art['readTime']} منٽ</span>
          <span class="card-meta-tag">{art['year']}ع</span>
        </div>
      </a>"""
      
    # Assemble index page using replacements
    index_html = INDEX_TEMPLATE
    index_html = index_html.replace('{{TOTAL_COUNT}}', str(len(articles_data)))
    index_html = index_html.replace('{{YEAR_FILTERS}}', year_filters_html)
    index_html = index_html.replace('{{CARDS}}', cards_html)
    index_html = index_html.replace('{{THEME_SCRIPT}}', THEME_SCRIPT)

    with open(os.path.join(DIRECTORY, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
        
    print("Generated index.html")
    print(f"Generated {len(articles_data)} static HTML pages in 'articles/' directory.")
    print("Build complete! You can open index.html directly in browser or upload the files to any site!")

if __name__ == '__main__':
    main()
