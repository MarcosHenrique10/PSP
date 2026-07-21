import os
import json
import re
import html

def clean_title(raw_title, folder_name):
    if not raw_title:
        return format_folder_name(folder_name)
    
    t = raw_title.replace('\u2014', '-').replace('\u2013', '-').replace('&mdash;', '-').replace('&ndash;', '-')
    t = html.unescape(t)
    t = re.sub(r'[\s\-\|:\u2014\u2013]*ChoiceScript.*$', '', t, flags=re.IGNORECASE).strip()
    t = t.replace('\ufffd', '').strip()
    
    if not t:
        return format_folder_name(folder_name)
    return t

def format_folder_name(folder_name):
    words = re.findall(r'[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', folder_name)
    if words:
        return ' '.join(w.capitalize() for w in words)
    return folder_name

def scan_games():
    games = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for category in ['COG', 'HG']:
        cat_dir = os.path.join(base_dir, category)
        if not os.path.exists(cat_dir):
            continue
        
        subdirs = sorted(os.listdir(cat_dir))
        for sub in subdirs:
            sub_path = os.path.join(cat_dir, sub)
            if os.path.isdir(sub_path):
                idx_path = os.path.join(sub_path, 'index.html')
                if os.path.exists(idx_path):
                    raw_title = ""
                    try:
                        with open(idx_path, 'rb') as f:
                            content = f.read(8000)
                            try:
                                text = content.decode('utf-8')
                            except UnicodeDecodeError:
                                text = content.decode('latin-1', errors='ignore')
                            
                            m = re.search(r'<title>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
                            if m:
                                raw_title = m.group(1).strip()
                    except Exception as e:
                        pass
                    
                    title = clean_title(raw_title, sub)
                    games.append({
                        'category': category,
                        'folder': sub,
                        'title': title,
                        'path': f"{category}/{sub}/index.html"
                    })
    
    return games

def generate_html(games):
    cog_count = sum(1 for g in games if g['category'] == 'COG')
    hg_count = sum(1 for g in games if g['category'] == 'HG')
    total_count = len(games)
    
    json_str = json.dumps(games, ensure_ascii=False)

    html_content = f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Choice Games & Hosted Games Library</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      /* ChoiceScript Original Parchment Theme Colors */
      --bg: #f4f1ea;
      --fg: #222222;
      --muted: #666666;
      --accent: #7a5c3e;
      --card-bg: #fbf9f3;
      --card-hover: #ffffff;
      --border: #dfdcd3;
      --border-hover: #b8b2a5;
      
      --choice-blue: #2f5d78;
      --choice-bg: #eef4f8;
      --chosen-green: #3d6b3d;
      --chosen-bg: #eef5ec;

      --cog-color: #2f5d78;
      --cog-bg: #eef4f8;
      --cog-border: #b3cde0;

      --hg-color: #8b0000;
      --hg-bg: #fef2f2;
      --hg-border: #fca5a5;

      --paper-line-color: rgba(34, 30, 25, 0.04);
      --paper-texture: repeating-linear-gradient(
        0deg,
        var(--paper-line-color) 0,
        var(--paper-line-color) 1px,
        transparent 1px,
        transparent 3px
      );

      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
      --shadow-sm: 0 2px 5px rgba(0,0,0,0.04), 0 1px 2px rgba(122, 92, 62, 0.05);
      --shadow-md: 0 8px 20px rgba(122, 92, 62, 0.08), 0 2px 6px rgba(0,0,0,0.04);
    }}

    body.dark-mode {{
      --bg: #1a1714;
      --fg: #e6e1d7;
      --muted: #a0988c;
      --accent: #d4a373;
      --card-bg: #24201c;
      --card-hover: #2d2924;
      --border: #38322c;
      --border-hover: #544b42;

      --cog-color: #7dd3fc;
      --cog-bg: #0c2a3a;
      --cog-border: #1e405b;

      --hg-color: #fca5a5;
      --hg-bg: #3b1212;
      --hg-border: #5c1d1d;

      --paper-line-color: rgba(255, 255, 255, 0.02);
      --shadow-sm: 0 2px 5px rgba(0,0,0,0.3);
      --shadow-md: 0 8px 20px rgba(0,0,0,0.4);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      background-image: var(--paper-texture);
      background-attachment: scroll;
      color: var(--fg);
      min-height: 100vh;
      line-height: 1.6;
      padding-bottom: 60px;
      transition: background-color 0.3s ease, color 0.3s ease;
    }}

    header {{
      padding: 36px 24px 20px 24px;
      max-width: 1240px;
      margin: 0 auto;
      border-bottom: 2px solid var(--accent);
      margin-bottom: 24px;
    }}

    .header-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
    }}

    .title-area h1 {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 2.2rem;
      font-weight: 700;
      color: var(--fg);
      letter-spacing: -0.01em;
      margin-bottom: 6px;
    }}

    .title-area p {{
      color: var(--accent);
      font-size: 0.98rem;
      font-weight: 500;
      font-style: italic;
    }}

    .stats-container {{
      display: flex;
      gap: 12px;
    }}

    .stat-badge {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      padding: 10px 18px;
      border-radius: var(--radius-md);
      text-align: center;
      min-width: 105px;
    }}

    .stat-number {{
      font-family: 'Merriweather', serif;
      font-size: 1.35rem;
      font-weight: 700;
      line-height: 1.2;
      color: var(--accent);
    }}

    .stat-label {{
      font-size: 0.72rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-top: 3px;
      font-weight: 600;
    }}

    /* Controls Bar */
    .controls-wrapper {{
      max-width: 1240px;
      margin: 0 auto 28px auto;
      padding: 0 24px;
    }}

    .controls-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .search-filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }}

    .search-box {{
      position: relative;
      flex: 1;
      min-width: 260px;
    }}

    .search-box input {{
      width: 100%;
      padding: 11px 40px 11px 40px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      color: var(--fg);
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      transition: all 0.2s ease;
    }}

    .search-box input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(122, 92, 62, 0.15);
    }}

    .search-box .search-icon {{
      position: absolute;
      left: 13px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      pointer-events: none;
    }}

    .search-box .clear-btn {{
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--muted);
      cursor: pointer;
      font-size: 1rem;
      display: none;
      padding: 4px;
    }}

    .search-box input:not(:placeholder-shown) + .search-icon + .clear-btn {{
      display: block;
    }}

    .filter-group {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .filter-btn {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--fg);
      padding: 8px 15px;
      border-radius: var(--radius-md);
      font-size: 0.86rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    .filter-btn.active {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
      font-weight: 600;
    }}

    .filter-btn.active.cog {{
      background: var(--cog-color);
      color: #ffffff;
      border-color: var(--cog-color);
    }}

    .filter-btn.active.hg {{
      background: var(--hg-color);
      color: #ffffff;
      border-color: var(--hg-color);
    }}

    .action-btn {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--fg);
      padding: 8px 14px;
      border-radius: var(--radius-md);
      font-size: 0.86rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .action-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    .action-btn.surprise {{
      background: var(--chosen-green);
      color: #ffffff;
      border-color: var(--chosen-green);
      font-weight: 600;
    }}
    .action-btn.surprise:hover {{
      opacity: 0.9;
      transform: translateY(-1px);
    }}

    /* Alphabet bar */
    .alpha-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 3px;
      justify-content: center;
      padding-top: 10px;
      border-top: 1px dashed var(--border);
    }}

    .alpha-btn {{
      background: none;
      border: none;
      color: var(--muted);
      font-size: 0.8rem;
      font-weight: 600;
      padding: 4px 7px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .alpha-btn:hover {{
      color: var(--accent);
      background: rgba(122, 92, 62, 0.08);
    }}

    .alpha-btn.active {{
      color: var(--accent);
      background: rgba(122, 92, 62, 0.15);
      font-weight: 700;
    }}

    /* Grid & View Modes */
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    .grid-view {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(285px, 1fr));
      gap: 18px;
    }}

    .list-view {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    /* Card Styling */
    .game-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      text-decoration: none;
      color: inherit;
      transition: all 0.2s ease;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
    }}

    .game-card:hover {{
      background: var(--card-hover);
      border-color: var(--border-hover);
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}

    .badge.COG {{
      background: var(--cog-bg);
      color: var(--cog-color);
      border: 1px solid var(--cog-border);
    }}

    .badge.HG {{
      background: var(--hg-bg);
      color: var(--hg-color);
      border: 1px solid var(--hg-border);
    }}

    .fav-star {{
      background: none;
      border: none;
      color: var(--border-hover);
      font-size: 1.15rem;
      cursor: pointer;
      transition: all 0.2s ease;
      padding: 0 2px;
    }}

    .fav-star:hover, .fav-star.active {{
      color: #d97706;
      transform: scale(1.15);
    }}

    .card-title {{
      font-family: 'Merriweather', Georgia, serif;
      font-size: 1.08rem;
      font-weight: 700;
      color: var(--fg);
      line-height: 1.4;
      margin-bottom: 10px;
      word-break: break-word;
    }}

    .card-folder {{
      font-size: 0.78rem;
      color: var(--muted);
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 14px;
      font-family: monospace;
      background: var(--bg);
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 12px;
      border-top: 1px dashed var(--border);
      font-size: 0.85rem;
    }}

    .play-link {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: var(--choice-blue);
      font-weight: 600;
      font-size: 0.88rem;
    }}

    body.dark-mode .play-link {{
      color: #7dd3fc;
    }}

    .game-card:hover .play-link {{
      text-decoration: underline;
    }}

    /* List view modifications */
    .list-view .game-card {{
      flex-direction: row;
      align-items: center;
      padding: 12px 18px;
    }}

    .list-view .card-top {{
      margin-bottom: 0;
      order: 1;
    }}

    .list-view .card-body {{
      display: flex;
      align-items: center;
      gap: 16px;
      flex: 1;
      margin: 0 16px;
    }}

    .list-view .card-title {{
      margin-bottom: 0;
      font-size: 0.98rem;
    }}

    .list-view .card-folder {{
      margin-bottom: 0;
    }}

    .list-view .card-footer {{
      border: none;
      padding: 0;
      order: 3;
    }}

    /* Empty state */
    .no-results {{
      text-align: center;
      padding: 50px 20px;
      background: var(--card-bg);
      border: 1px dashed var(--border);
      border-radius: var(--radius-lg);
      grid-column: 1 / -1;
    }}

    .no-results h3 {{
      font-family: 'Merriweather', serif;
      font-size: 1.25rem;
      margin-bottom: 8px;
      color: var(--fg);
    }}

    .no-results p {{
      color: var(--muted);
    }}

    /* Floating Back to top */
    .back-to-top {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--fg);
      width: 42px;
      height: 42px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      opacity: 0;
      visibility: hidden;
      transition: all 0.25s ease;
      box-shadow: var(--shadow-md);
      z-index: 100;
    }}

    .back-to-top.visible {{
      opacity: 1;
      visibility: visible;
    }}

    .back-to-top:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}

    @media (max-width: 768px) {{
      header {{ padding: 24px 16px 16px 16px; }}
      .controls-wrapper {{ padding: 0 16px; }}
      main {{ padding: 0 16px; }}
      .header-top {{ flex-direction: column; align-items: flex-start; }}
      .stats-container {{ width: 100%; justify-content: space-between; }}
      .stat-badge {{ flex: 1; min-width: 0; }}
      .list-view .game-card {{ flex-direction: column; align-items: flex-start; gap: 8px; }}
      .list-view .card-body {{ margin: 0; flex-direction: column; align-items: flex-start; gap: 6px; }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-top">
      <div class="title-area">
        <h1>Choice Games Library</h1>
        <p>Koleksi Interaktif Choice of Games & Hosted Games</p>
      </div>
      <div class="stats-container">
        <div class="stat-badge">
          <div class="stat-number" id="stat-total">{total_count}</div>
          <div class="stat-label">Total Game</div>
        </div>
        <div class="stat-badge">
          <div class="stat-number" style="color: var(--cog-color);" id="stat-cog">{cog_count}</div>
          <div class="stat-label">COG</div>
        </div>
        <div class="stat-badge">
          <div class="stat-number" style="color: var(--hg-color);" id="stat-hg">{hg_count}</div>
          <div class="stat-label">HG</div>
        </div>
      </div>
    </div>
  </header>

  <div class="controls-wrapper">
    <div class="controls-card">
      <div class="search-filter-row">
        <div class="search-box">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="search-input" placeholder="Cari judul game atau folder..." autocomplete="off">
          <button class="clear-btn" id="clear-search" title="Bersihkan">✕</button>
        </div>

        <div class="filter-group">
          <button class="filter-btn active" data-filter="ALL">Semua ({total_count})</button>
          <button class="filter-btn cog" data-filter="COG">COG ({cog_count})</button>
          <button class="filter-btn hg" data-filter="HG">HG ({hg_count})</button>
          <button class="filter-btn" data-filter="FAV">Favorit ★</button>
        </div>

        <div style="display: flex; gap: 8px;">
          <button class="action-btn" id="theme-toggle-btn" title="Ubah Tema Warna">
            📜 Kertas
          </button>
          <button class="action-btn surprise" id="surprise-btn" title="Mainkan game acak!">
            🎲 Acak
          </button>
          <button class="action-btn" id="view-toggle-btn" title="Ubah Tampilan">
            <span id="view-icon">☰</span>
          </button>
        </div>
      </div>

      <div class="alpha-bar" id="alpha-bar">
        <!-- Generated by JS -->
      </div>
    </div>
  </div>

  <main>
    <div class="grid-view" id="games-container">
      <!-- Cards rendered here -->
    </div>
  </main>

  <button class="back-to-top" id="back-to-top" title="Kembali ke atas">
    ↑
  </button>

  <script>
    const GAMES_DATA = {json_str};

    let currentFilter = 'ALL';
    let currentAlpha = 'ALL';
    let searchQuery = '';
    let isGridView = true;
    let isDarkMode = localStorage.getItem('theme') === 'dark';
    let favorites = new Set(JSON.parse(localStorage.getItem('fav_games') || '[]'));

    const container = document.getElementById('games-container');
    const searchInput = document.getElementById('search-input');
    const clearSearch = document.getElementById('clear-search');
    const alphaBar = document.getElementById('alpha-bar');
    const viewToggleBtn = document.getElementById('view-toggle-btn');
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const viewIcon = document.getElementById('view-icon');
    const surpriseBtn = document.getElementById('surprise-btn');
    const backToTopBtn = document.getElementById('back-to-top');

    // Theme logic
    function applyTheme() {{
      if (isDarkMode) {{
        document.body.classList.add('dark-mode');
        themeToggleBtn.textContent = '🌙 Gelap';
      }} else {{
        document.body.classList.remove('dark-mode');
        themeToggleBtn.textContent = '📜 Kertas';
      }}
    }}

    themeToggleBtn.addEventListener('click', () => {{
      isDarkMode = !isDarkMode;
      localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
      applyTheme();
    }});

    // Init Alphabet Bar
    function initAlphaBar() {{
      const letters = ['ALL', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')];
      alphaBar.innerHTML = letters.map(l => 
        `<button class="alpha-btn ${{l === 'ALL' ? 'active' : ''}}" data-alpha="${{l}}">${{l}}</button>`
      ).join('');
    }}

    // Filter Logic
    function getFilteredGames() {{
      const q = searchQuery.toLowerCase().trim();
      return GAMES_DATA.filter(game => {{
        // Category Filter
        if (currentFilter === 'COG' && game.category !== 'COG') return false;
        if (currentFilter === 'HG' && game.category !== 'HG') return false;
        if (currentFilter === 'FAV' && !favorites.has(game.path)) return false;

        // Alphabet Filter
        if (currentAlpha !== 'ALL') {{
          const firstChar = game.title.charAt(0).toUpperCase();
          if (firstChar !== currentAlpha) return false;
        }}

        // Search Query
        if (q) {{
          const titleMatch = game.title.toLowerCase().includes(q);
          const folderMatch = game.folder.toLowerCase().includes(q);
          return titleMatch || folderMatch;
        }}

        return true;
      }});
    }}

    // Render Function
    function render() {{
      const filtered = getFilteredGames();
      
      if (filtered.length === 0) {{
        container.innerHTML = `
          <div class="no-results">
            <h3>Tidak Ada Game Ditemukan</h3>
            <p>Coba sesuaikan kata kunci pencarian atau filter kategori Anda.</p>
          </div>
        `;
        return;
      }}

      container.className = isGridView ? 'grid-view' : 'list-view';

      container.innerHTML = filtered.map(game => {{
        const isFav = favorites.has(game.path);
        return `
          <a href="${{game.path}}" class="game-card ${{game.category}}" target="_blank" rel="noopener">
            <div class="card-top">
              <span class="badge ${{game.category}}">${{game.category}}</span>
              <button class="fav-star ${{isFav ? 'active' : ''}}" 
                      data-path="${{game.path}}" 
                      title="${{isFav ? 'Hapus dari favorit' : 'Tambah ke favorit'}}"
                      onclick="toggleFavorite(event, '${{game.path}}')">
                ${{isFav ? '★' : '☆'}}
              </button>
            </div>
            <div class="card-body">
              <div class="card-title">${{escapeHtml(game.title)}}</div>
              <div class="card-folder">📁 ${{escapeHtml(game.folder)}}</div>
            </div>
            <div class="card-footer">
              <span class="play-link">Buka Game ➔</span>
            </div>
          </a>
        `;
      }}).join('');
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }}

    function toggleFavorite(event, path) {{
      event.preventDefault();
      event.stopPropagation();
      if (favorites.has(path)) {{
        favorites.delete(path);
      }} else {{
        favorites.add(path);
      }}
      localStorage.setItem('fav_games', JSON.stringify([...favorites]));
      render();
    }}

    // Event Listeners
    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value;
      render();
    }});

    clearSearch.addEventListener('click', () => {{
      searchInput.value = '';
      searchQuery = '';
      render();
    }});

    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        render();
      }});
    }});

    alphaBar.addEventListener('click', (e) => {{
      if (e.target.classList.contains('alpha-btn')) {{
        document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentAlpha = e.target.dataset.alpha;
        render();
      }}
    }});

    viewToggleBtn.addEventListener('click', () => {{
      isGridView = !isGridView;
      viewIcon.textContent = isGridView ? '☰' : '☷';
      render();
    }});

    surpriseBtn.addEventListener('click', () => {{
      const filtered = getFilteredGames();
      if (filtered.length > 0) {{
        const randomGame = filtered[Math.floor(Math.random() * filtered.length)];
        window.open(randomGame.path, '_blank');
      }}
    }});

    window.addEventListener('scroll', () => {{
      if (window.scrollY > 300) {{
        backToTopBtn.classList.add('visible');
      }} else {{
        backToTopBtn.classList.remove('visible');
      }}
    }});

    backToTopBtn.addEventListener('click', () => {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});

    // Initialize
    applyTheme();
    initAlphaBar();
    render();
  </script>
</body>
</html>
'''
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Generated index.html successfully with ChoiceScript paper theme!")

if __name__ == '__main__':
    data = scan_games()
    print(f"Total games indexed: {len(data)}")
    cog_count = sum(1 for g in data if g['category'] == 'COG')
    hg_count = sum(1 for g in data if g['category'] == 'HG')
    print(f"COG: {cog_count}, HG: {hg_count}")
    
    with open('games_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to games_data.json")
    
    generate_html(data)
