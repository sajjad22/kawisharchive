import os
import re
import sys
import json
import shutil
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
# CONSTANTS & PATHS & TRANSLATIONS
# --------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_SOURCE = "/home/sajjad/Downloads/sattar.ttf"
TRANSLATIONS_FILE = os.path.join(ROOT_DIR, "author_translations.json")

def load_author_translations():
    if os.path.exists(TRANSLATIONS_FILE):
        try:
            with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning loading translations: {e}")
    return {}

AUTHOR_TRANSLATIONS = load_author_translations()

def get_sindhi_author_name(english_name):
    return AUTHOR_TRANSLATIONS.get(english_name.strip(), english_name)

# Ensure custom font is available in root assets
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
FONT_TARGET = os.path.join(ASSETS_DIR, "sattar.ttf")

if os.path.exists(FONT_SOURCE) and not os.path.exists(FONT_TARGET):
    try:
        shutil.copy2(FONT_SOURCE, FONT_TARGET)
        print(f"Copied custom font '{FONT_SOURCE}' to '{FONT_TARGET}'.")
    except Exception as e:
        print(f"Warning: Could not copy font: {e}")

# --------------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------------
def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
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
    clean = re.sub(r'[#\*_`\[\]\-]', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean[:180] + '...' if len(clean) > 180 else clean

def parse_filename(filename):
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
STYLE_CSS = """/* Shared CSS with custom Sattar font & Modern Layout */
@font-face {
  font-family: 'SattarFont';
  src: url('../../assets/sattar.ttf') format('truetype'),
       url('../assets/sattar.ttf') format('truetype'),
       url('assets/sattar.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}

:root {
  --font-ui: 'SattarFont', 'Tajawal', system-ui, -apple-system, sans-serif;
  --font-read-body: 'SattarFont', 'Lateef', serif;
  --font-read-heading: 'SattarFont', 'Amiri', serif;
  --transition-normal: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
}

/* Modern Clean Palette */
body.theme-light {
  --bg-app: #f8fafc;
  --bg-card: #ffffff;
  --bg-hover: #f1f5f9;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --primary: #8b0000;
  --primary-hover: #660000;
  --border: #e2e8f0;
}

body.theme-sepia {
  --bg-app: #f5efe6;
  --bg-card: #fdfbf7;
  --bg-hover: #ebdcc9;
  --text-primary: #2c221e;
  --text-secondary: #5c4b43;
  --text-muted: #8c786e;
  --primary: #943b17;
  --primary-hover: #732a0e;
  --border: #e6dac8;
}

body.theme-dark {
  --bg-app: #0f172a;
  --bg-card: #1e293b;
  --bg-hover: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #64748b;
  --primary: #f87171;
  --primary-hover: #ef4444;
  --border: #334155;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-ui);
  background-color: var(--bg-app);
  color: var(--text-primary);
  direction: rtl;
  min-height: 100vh;
  transition: background-color var(--transition-normal), color var(--transition-normal);
  line-height: 1.6;
}
a { color: inherit; text-decoration: none; }

.container { max-width: 900px; margin: 0 auto; padding: 30px 16px; }

.main-header { text-align: center; margin-bottom: 30px; }
.author-badge { display: inline-flex; width: 64px; height: 64px; background: linear-gradient(135deg, var(--primary), var(--primary-hover)); color: white; border-radius: 16px; align-items: center; justify-content: center; font-size: 24px; font-weight: 800; box-shadow: var(--shadow-md); margin-bottom: 12px; }
.main-header h1 { font-size: 28px; font-weight: 800; margin-bottom: 2px; }
.main-header .author-english-sub { font-size: 14px; color: var(--text-muted); font-weight: normal; margin-bottom: 6px; font-family: sans-serif; letter-spacing: 0.5px; }
.main-header p { color: var(--text-secondary); font-size: 14px; }

.nav-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 12px; flex-wrap: wrap; }
.btn-back { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; color: var(--text-primary); font-weight: 600; font-size: 13px; transition: all var(--transition-normal); box-shadow: var(--shadow-sm); }
.btn-back:hover { background-color: var(--bg-hover); transform: translateX(2px); }

.theme-controls { display: flex; background-color: var(--bg-card); padding: 4px; border-radius: 10px; border: 1px solid var(--border); gap: 4px; }
.theme-btn { border: none; background: transparent; padding: 6px 12px; border-radius: 6px; color: var(--text-secondary); font-family: var(--font-ui); font-size: 13px; cursor: pointer; transition: all var(--transition-normal); }
.theme-btn:hover { color: var(--text-primary); }
.theme-btn.active { background-color: var(--primary); color: white; font-weight: bold; }

.controls-card { background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 18px; margin-bottom: 25px; box-shadow: var(--shadow-sm); }
.search-box { position: relative; margin-bottom: 0px; }
.search-input { width: 100%; padding: 12px 40px 12px 16px; background-color: var(--bg-app); border: 1px solid var(--border); border-radius: 10px; font-family: var(--font-ui); font-size: 15px; color: var(--text-primary); outline: none; transition: border-color var(--transition-normal); }
.search-input:focus { border-color: var(--primary); }
.search-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 16px; }

.filters-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 15px; }
.filter-btn { border: 1px solid var(--border); background-color: var(--bg-app); color: var(--text-secondary); padding: 5px 12px; border-radius: 18px; font-family: var(--font-ui); font-size: 13px; cursor: pointer; transition: all var(--transition-normal); }
.filter-btn:hover, .filter-btn.active { background-color: var(--primary); color: white; border-color: var(--primary); }

.articles-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
.article-card { display: block; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; transition: all var(--transition-normal); box-shadow: var(--shadow-sm); }
.article-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--primary); }
.card-header-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 10px; }
.card-title { font-family: var(--font-read-heading); font-size: 20px; font-weight: 700; color: var(--text-primary); line-height: 1.4; }
.card-date { font-size: 12px; color: var(--text-muted); white-space: nowrap; }
.card-snippet { font-family: var(--font-read-body); font-size: 16px; line-height: 1.6; color: var(--text-secondary); margin-bottom: 14px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-muted); border-top: 1px dashed var(--border); padding-top: 10px; }
.card-meta-tag { background-color: var(--bg-hover); padding: 3px 8px; border-radius: 6px; color: var(--primary); font-weight: 600; }

/* Article Reading View - Full Bleed Screen Optimization */
.reading-pane {
  background-color: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
}

.article-meta-header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 18px;
  margin-bottom: 25px;
}

.article-heading {
  font-family: var(--font-read-heading);
  font-size: 26px;
  font-weight: 800;
  line-height: 1.4;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.meta-info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary);
  align-items: center;
}

.meta-link { color: var(--primary); font-weight: 500; }
.meta-link:hover { text-decoration: underline; }

.article-body {
  font-family: var(--font-read-body);
  font-size: 20px;
  line-height: 1.85;
  color: var(--text-primary);
  text-align: justify;
}

.article-body p {
  margin-bottom: 1.4em;
  text-indent: 0;
}

.article-body h2 {
  font-family: var(--font-read-heading);
  font-size: 24px;
  margin-top: 1.4em;
  margin-bottom: 0.6em;
  color: var(--primary);
}

/* Copy Content Action Section */
.copy-action-bar {
  margin-top: 35px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.btn-copy-article {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.btn-copy-article:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-copy-article.copied {
  background-color: #10b981;
}

/* Hub Grid */
.authors-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.author-hub-card { display: flex; flex-direction: column; background-color: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; transition: all var(--transition-normal); box-shadow: var(--shadow-sm); text-decoration: none; }
.author-hub-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--primary); }
.hub-avatar { width: 48px; height: 48px; background: linear-gradient(135deg, var(--primary), var(--primary-hover)); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; margin-bottom: 12px; }
.hub-title { font-family: var(--font-read-heading); font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
.hub-title-english { font-size: 12px; color: var(--text-muted); font-family: sans-serif; margin-bottom: 10px; }
.hub-meta { font-size: 13px; color: var(--text-secondary); margin-top: auto; padding-top: 12px; border-top: 1px dashed var(--border); display: flex; justify-content: space-between; }

@media (max-width: 600px) {
  .container { padding: 15px 12px; }
  .article-heading { font-size: 22px; }
  .article-body { font-size: 18px; line-height: 1.75; text-align: right; }
  .main-header h1 { font-size: 24px; }
  .card-title { font-size: 18px; }
  .card-snippet { font-size: 15px; }
}
"""

THEME_SCRIPT = """<script>
const savedTheme = localStorage.getItem('kawish_theme_static') || 'theme-sepia';
document.body.className = savedTheme;

document.addEventListener('DOMContentLoaded', () => {
  const activeBtn = document.querySelector(`.theme-btn[data-theme="${savedTheme}"]`);
  if (activeBtn) activeBtn.classList.add('active');
});

function changeTheme(themeName) {
  document.body.className = themeName;
  localStorage.setItem('kawish_theme_static', themeName);
  document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.querySelector(`.theme-btn[data-theme="${themeName}"]`);
  if (activeBtn) activeBtn.classList.add('active');
}

function filterArticles() {
  const query = document.getElementById('searchInput')?.value.toLowerCase().trim() || '';
  const cards = document.querySelectorAll('.article-card');
  let visibleCount = 0;
  cards.forEach(card => {
    const title = card.getAttribute('data-title') || '';
    const snippet = card.getAttribute('data-snippet') || '';
    const year = card.getAttribute('data-year') || '';
    const matchesSearch = !query || title.includes(query) || snippet.includes(query);
    const matchesYear = !window.selectedYearFilter || year === window.selectedYearFilter;
    if (matchesSearch && matchesYear) { card.style.display = 'block'; visibleCount++; }
    else { card.style.display = 'none'; }
  });
  const counterEl = document.getElementById('visibleCount');
  if (counterEl) counterEl.textContent = visibleCount;
}

function filterAuthorsHub() {
  const query = document.getElementById('hubSearchInput')?.value.toLowerCase().trim() || '';
  const cards = document.querySelectorAll('.author-hub-card');
  let visibleCount = 0;
  cards.forEach(card => {
    const title = card.getAttribute('data-name') || '';
    const englishName = card.getAttribute('data-english') || '';
    if (!query || title.includes(query) || englishName.includes(query)) {
      card.style.display = 'flex';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });
  const counterEl = document.getElementById('visibleAuthorCount');
  if (counterEl) counterEl.textContent = visibleCount;
}

function filterYear(yearStr) {
  window.selectedYearFilter = (window.selectedYearFilter === yearStr) ? null : yearStr;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', yearStr && btn.textContent.includes(yearStr) && window.selectedYearFilter === yearStr);
  });
  filterArticles();
}

function copyArticleContent() {
  const heading = document.querySelector('.article-heading')?.innerText || '';
  const bodyText = document.querySelector('.article-body')?.innerText || '';
  const fullText = heading + '\\n\\n' + bodyText;
  
  navigator.clipboard.writeText(fullText).then(() => {
    const copyBtn = document.getElementById('copyArticleBtn');
    if (copyBtn) {
      copyBtn.classList.add('copied');
      copyBtn.innerHTML = '<span>✓ ڪاپي ٿي ويو!</span>';
      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.innerHTML = '<span>📋 مضمون ڪاپي ڪريو</span>';
      }, 2500);
    }
  }).catch(err => {
    console.error('Failed to copy: ', err);
  });
}
</script>"""

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="sd" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}} - {{AUTHOR_SINDHI}}</title>
  <link rel="stylesheet" href="../style.css?v=4.0">
</head>
<body class="theme-sepia">
  <div class="container">
    <nav class="nav-toolbar">
      <a href="../index.html" class="btn-back"><span>← {{AUTHOR_SINDHI}} جا مضمون</span></a>
      <a href="../../index.html" class="btn-back"><span>🏠 مکيه صفحو</span></a>
      <div class="theme-controls">
        <button class="theme-btn" data-theme="theme-light" onclick="changeTheme('theme-light')">اڇو</button>
        <button class="theme-btn" data-theme="theme-sepia" onclick="changeTheme('theme-sepia')">سيپيا</button>
        <button class="theme-btn" data-theme="theme-dark" onclick="changeTheme('theme-dark')">تاريڪ</button>
      </div>
    </nav>
    <main class="reading-pane">
      <header class="article-meta-header">
        <h1 class="article-heading">{{TITLE}}</h1>
        <div class="meta-info-row">
          <span>✍️ {{AUTHOR_SINDHI}}</span>
          <span>📅 {{DATE}}</span>
          <span>⏱️ {{READ_TIME}} منٽ</span>
          {{ORIGINAL_URL}}
        </div>
      </header>
      <article class="article-body">{{BODY}}</article>
      <div class="copy-action-bar">
        <button id="copyArticleBtn" class="btn-copy-article" onclick="copyArticleContent()">
          <span>📋 مضمون ڪاپي ڪريو</span>
        </button>
      </div>
    </main>
  </div>
  {{THEME_SCRIPT}}
</body>
</html>"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="sd" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{AUTHOR_SINDHI}} - ڪاوش آرڪائيو</title>
  <link rel="stylesheet" href="style.css?v=4.0">
</head>
<body class="theme-sepia">
  <div class="container">
    <nav class="nav-toolbar">
      <a href="../index.html" class="btn-back"><span>🏠 مکيه صفحو</span></a>
      <div class="theme-controls">
        <button class="theme-btn" data-theme="theme-light" onclick="changeTheme('theme-light')">اڇو</button>
        <button class="theme-btn" data-theme="theme-sepia" onclick="changeTheme('theme-sepia')">سيپيا</button>
        <button class="theme-btn" data-theme="theme-dark" onclick="changeTheme('theme-dark')">تاريڪ</button>
      </div>
    </nav>
    <header class="main-header">
      <div class="author-badge">{{INITIALS}}</div>
      <h1>{{AUTHOR_SINDHI}}</h1>
      <div class="author-english-sub">{{AUTHOR_ENGLISH}}</div>
      <p>ڪُل <span id="visibleCount">{{TOTAL_COUNT}}</span> مضمون</p>
    </header>
    <section class="controls-card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="مضمون جي عنوان يا مواد مان ڳوليو..." oninput="filterArticles()">
      </div>
      <div class="filters-row">
        <span style="font-size: 13px; color: var(--text-muted);">سال:</span>
        {{YEAR_FILTERS}}
      </div>
    </section>
    <main class="articles-grid">{{CARDS}}</main>
  </div>
  {{THEME_SCRIPT}}
</body>
</html>"""

MAIN_HUB_TEMPLATE = """<!DOCTYPE html>
<html lang="sd" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>روزاني ڪاوش - مضمون ۽ مقالا آرڪائيو</title>
  <link rel="stylesheet" href="assets/style.css?v=4.0">
</head>
<body class="theme-sepia">
  <div class="container">
    <nav class="nav-toolbar">
      <div style="font-weight: bold; font-size: 18px;">📰 روزاني ڪاوش مقالا آرڪائيو</div>
      <div class="theme-controls">
        <button class="theme-btn" data-theme="theme-light" onclick="changeTheme('theme-light')">اڇو</button>
        <button class="theme-btn" data-theme="theme-sepia" onclick="changeTheme('theme-sepia')">سيپيا</button>
        <button class="theme-btn" data-theme="theme-dark" onclick="changeTheme('theme-dark')">تاريڪ</button>
      </div>
    </nav>
    <header class="main-header">
      <div class="author-badge">K</div>
      <h1>مصنفن جو مکيه پورٽل</h1>
      <p>ڪُل <span id="visibleAuthorCount">{{AUTHOR_COUNT}}</span> مصنفن جا مضمون موجود آهن</p>
    </header>

    <section class="controls-card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="hubSearchInput" class="search-input" placeholder="مصنف جي نالي مان ڳوليو..." oninput="filterAuthorsHub()">
      </div>
    </section>

    <main class="authors-grid">{{AUTHOR_CARDS}}</main>
  </div>
  {{THEME_SCRIPT}}
</body>
</html>"""

def build_author_site(author_dir):
    if not os.path.isdir(author_dir): return None
    author_english = os.path.basename(author_dir.rstrip('/\\'))
    author_sindhi = get_sindhi_author_name(author_english)
    
    files = [f for f in os.listdir(author_dir) if f.endswith('.md')]
    articles_dir = os.path.join(author_dir, 'articles')
    os.makedirs(articles_dir, exist_ok=True)
    with open(os.path.join(author_dir, 'style.css'), 'w', encoding='utf-8') as f: f.write(STYLE_CSS)
    initials = "".join([w[0] for w in author_english.split() if w])[:2].upper() or "KA"

    if not files:
        html_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')] if os.path.exists(articles_dir) else []
        if html_files or os.path.exists(os.path.join(author_dir, 'index.html')):
            return {'author_english': author_english, 'author_sindhi': author_sindhi, 'count': len(html_files), 'dir': author_english, 'initials': initials}
        return None
    articles_data = []
    for idx, filename in enumerate(files):
        filepath = os.path.join(author_dir, filename)
        metadata, body = parse_md(filepath)
        filename_meta = parse_filename(filename)
        title = metadata.get('title') or filename_meta['title']
        date = metadata.get('date') or filename_meta['date']
        year = metadata.get('year') or (re.search(r'\d{4}', date).group(0) if re.search(r'\d{4}', date) else '')
        art_id = idx + 1
        html_filename = f"art_{art_id}.html"
        read_time = max(1, round(len(body.split())/180))
        body_html = markdown.markdown(body)
        
        page_html = ARTICLE_TEMPLATE.replace('{{TITLE}}', title).replace('{{AUTHOR_ENGLISH}}', author_english).replace('{{AUTHOR_SINDHI}}', author_sindhi).replace('{{INITIALS}}', initials).replace('{{DATE}}', date).replace('{{READ_TIME}}', str(read_time)).replace('{{ORIGINAL_URL}}', '').replace('{{BODY}}', body_html).replace('{{THEME_SCRIPT}}', THEME_SCRIPT)
        with open(os.path.join(articles_dir, html_filename), 'w', encoding='utf-8') as f: f.write(page_html)
        articles_data.append({'title': title, 'date': date, 'year': year, 'snippet': clean_snippet(body), 'readTime': read_time, 'link': f"articles/{html_filename}"})
    articles_data.sort(key=lambda x: (x['year'], x['date']), reverse=True)
    years = sorted(list(set([a['year'] for a in articles_data if a['year']])), reverse=True)
    year_filters_html = "\n".join([f'<button class="filter-btn" onclick="filterYear(\'{y}\')">{y}ع</button>' for y in years])
    cards_html = "".join([f'<a href="{a["link"]}" class="article-card" data-title="{a["title"].lower()}" data-year="{a["year"]}" data-snippet="{a["snippet"].lower()}"><div class="card-header-row"><h2 class="card-title">{a["title"]}</h2><span class="card-date">{a["date"]}</span></div><p class="card-snippet">{a["snippet"]}</p><div class="card-footer"><span>⏱️ {a["readTime"]} منٽ</span><span class="card-meta-tag">{a["year"]}ع</span></div></a>' for a in articles_data])
    index_html = INDEX_TEMPLATE.replace('{{AUTHOR_ENGLISH}}', author_english).replace('{{AUTHOR_SINDHI}}', author_sindhi).replace('{{INITIALS}}', initials).replace('{{TOTAL_COUNT}}', str(len(articles_data))).replace('{{YEAR_FILTERS}}', year_filters_html).replace('{{CARDS}}', cards_html).replace('{{THEME_SCRIPT}}', THEME_SCRIPT)
    with open(os.path.join(author_dir, 'index.html'), 'w', encoding='utf-8') as f: f.write(index_html)
    return {'author_english': author_english, 'author_sindhi': author_sindhi, 'count': len(articles_data), 'dir': author_english, 'initials': initials}

def build_main_hub(base_dir=ROOT_DIR):
    assets_dir = os.path.join(base_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    font_target = os.path.join(assets_dir, 'sattar.ttf')
    if os.path.exists(FONT_SOURCE) and not os.path.exists(font_target):
        try:
            shutil.copy2(FONT_SOURCE, font_target)
        except Exception as e:
            print(f"Warning font copy: {e}")

    with open(os.path.join(assets_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(STYLE_CSS)

    authors_found = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.') and item not in ['assets', '__pycache__']:
            res = build_author_site(item_path)
            if res:
                authors_found.append(res)
    authors_found.sort(key=lambda x: x['author_sindhi'])

    cards_html = "".join([f'<a href="{a["dir"]}/index.html" class="author-hub-card" data-name="{a["author_sindhi"].lower()}" data-english="{a["author_english"].lower()}"><div class="hub-avatar">{a["initials"]}</div><div class="hub-title">{a["author_sindhi"]}</div><div class="hub-title-english">{a["author_english"]}</div><div class="hub-meta"><span>📚 {a["count"]} مضمون</span><span>سائيٽ ڏسو ←</span></div></a>' for a in authors_found])
    hub_html = MAIN_HUB_TEMPLATE.replace('{{AUTHOR_COUNT}}', str(len(authors_found))).replace('{{AUTHOR_CARDS}}', cards_html).replace('{{THEME_SCRIPT}}', THEME_SCRIPT)
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(hub_html)

def main():
    print("Building all author sites and main hub portal...")
    build_main_hub(ROOT_DIR)
    print("Build complete!")

if __name__ == '__main__':
    main()
