from pathlib import Path
import json, textwrap, random

root = Path('/mnt/data/personal-nav-pro')
css = root/'assets'/'css'
js = root/'assets'/'js'
api = js/'api'
modules = js/'modules'
data = js/'data'


def w(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n', encoding='utf-8')

index_html = r'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="个人导航站 Pro，多文件静态版，支持搜索、收藏、导入导出、天气和 GitHub 面板。" />
  <title>个人导航站 Pro</title>
  <link rel="preconnect" href="https://api.github.com" crossorigin>
  <link rel="preconnect" href="https://geocoding-api.open-meteo.com" crossorigin>
  <link rel="preconnect" href="https://api.open-meteo.com" crossorigin>
  <link rel="stylesheet" href="./assets/css/reset.css" />
  <link rel="stylesheet" href="./assets/css/variables.css" />
  <link rel="stylesheet" href="./assets/css/base.css" />
  <link rel="stylesheet" href="./assets/css/layout.css" />
  <link rel="stylesheet" href="./assets/css/components.css" />
  <link rel="stylesheet" href="./assets/css/animations.css" />
  <link rel="stylesheet" href="./assets/css/utilities.css" />
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar glass">
      <div class="brand-block">
        <div class="brand-mark">N</div>
        <div>
          <h1 class="brand-title">Navigator Pro</h1>
          <p class="brand-subtitle">静态多文件个人导航站</p>
        </div>
      </div>

      <nav class="side-nav" aria-label="侧边功能区">
        <button class="side-nav-item is-active" data-view="dashboard">总览</button>
        <button class="side-nav-item" data-view="sites">网站库</button>
        <button class="side-nav-item" data-view="favorites">收藏夹</button>
        <button class="side-nav-item" data-view="recent">最近打开</button>
        <button class="side-nav-item" data-view="settings">设置</button>
      </nav>

      <section class="sidebar-card">
        <div class="sidebar-card-head">
          <h2>快捷键</h2>
        </div>
        <ul class="shortcut-list">
          <li><kbd>/</kbd><span>聚焦搜索</span></li>
          <li><kbd>Ctrl</kbd><kbd>K</kbd><span>命令面板</span></li>
          <li><kbd>G</kbd><kbd>D</kbd><span>切到总览</span></li>
          <li><kbd>G</kbd><kbd>S</kbd><span>切到网站库</span></li>
          <li><kbd>Esc</kbd><span>关闭弹层</span></li>
        </ul>
      </section>

      <section class="sidebar-card">
        <div class="sidebar-card-head">
          <h2>数据</h2>
          <button id="resetAppBtn" class="text-btn danger">重置</button>
        </div>
        <p class="sidebar-muted">支持导出 JSON 备份，也支持一键恢复。</p>
        <div class="stack-row">
          <button id="exportStateBtn" class="soft-btn full">导出数据</button>
          <label class="soft-btn full file-btn">
            导入数据
            <input id="importStateInput" type="file" accept="application/json" hidden />
          </label>
        </div>
      </section>
    </aside>

    <main class="main-area">
      <header class="topbar glass">
        <div class="topbar-main">
          <div>
            <p class="eyebrow">可扩展前端架构</p>
            <h2 class="page-title" id="pageTitle">总览</h2>
          </div>
          <div class="topbar-actions">
            <button id="commandPaletteBtn" class="soft-btn icon-btn" aria-label="打开命令面板">⌘</button>
            <button id="addSiteBtn" class="primary-btn">添加站点</button>
          </div>
        </div>

        <div class="search-grid">
          <label class="search-field">
            <span class="field-label">全局搜索</span>
            <input id="globalSearchInput" type="text" placeholder="输入名称、描述、标签、分类" />
          </label>

          <label class="search-field">
            <span class="field-label">分类</span>
            <select id="categorySelect"></select>
          </label>

          <label class="search-field">
            <span class="field-label">排序</span>
            <select id="sortSelect">
              <option value="smart">智能排序</option>
              <option value="name-asc">名称 A-Z</option>
              <option value="name-desc">名称 Z-A</option>
              <option value="updated">最近更新</option>
              <option value="opens">打开次数</option>
            </select>
          </label>

          <div class="chip-group" id="filterChips" aria-label="过滤条件">
            <button class="chip is-active" data-filter="all">全部</button>
            <button class="chip" data-filter="builtin">内置</button>
            <button class="chip" data-filter="custom">自定义</button>
            <button class="chip" data-filter="pinned">置顶</button>
            <button class="chip" data-filter="favorite">收藏</button>
          </div>
        </div>
      </header>

      <section class="dashboard-grid" id="dashboardView">
        <article class="hero-card glass span-2">
          <div class="hero-copy">
            <span class="eyebrow">你的控制中心</span>
            <h3>把常用网站、天气、GitHub 信息和个人数据放在一个静态站里。</h3>
            <p>
              这是纯前端项目，不依赖构建工具。直接打开 index.html 即可运行。
              站点状态、收藏、主题、最近访问和自定义内容都会保存到浏览器本地。
            </p>
            <div class="hero-actions">
              <button id="jumpSitesBtn" class="primary-btn">查看网站库</button>
              <button id="jumpSettingsBtn" class="soft-btn">打开设置</button>
            </div>
          </div>
          <div class="hero-stats" id="heroStats"></div>
        </article>

        <article class="widget-card glass" id="weatherWidget">
          <div class="widget-head">
            <h3>天气面板</h3>
            <button id="refreshWeatherBtn" class="text-btn">刷新</button>
          </div>
          <form id="weatherSearchForm" class="compact-form">
            <input id="weatherCityInput" type="text" placeholder="城市名，例如 New York" />
            <button class="soft-btn" type="submit">查询</button>
            <button id="weatherGeoBtn" class="soft-btn" type="button">定位</button>
          </form>
          <div id="weatherContent" class="widget-body skeleton-lines"></div>
        </article>

        <article class="widget-card glass" id="githubWidget">
          <div class="widget-head">
            <h3>GitHub 面板</h3>
            <button id="refreshGithubBtn" class="text-btn">刷新</button>
          </div>
          <form id="githubSearchForm" class="compact-form">
            <input id="githubUserInput" type="text" placeholder="GitHub 用户名" />
            <button class="soft-btn" type="submit">加载</button>
          </form>
          <div id="githubContent" class="widget-body skeleton-lines"></div>
        </article>

        <article class="widget-card glass span-2" id="insightWidget">
          <div class="widget-head">
            <h3>效率洞察</h3>
            <button id="clearRecentBtn" class="text-btn danger">清空最近访问</button>
          </div>
          <div class="insight-layout">
            <div>
              <h4>热门分类</h4>
              <div id="hotCategories"></div>
            </div>
            <div>
              <h4>最近打开</h4>
              <div id="recentSites"></div>
            </div>
            <div>
              <h4>效率提醒</h4>
              <div id="tipsBox"></div>
            </div>
          </div>
        </article>
      </section>

      <section class="view-section is-hidden" id="sitesView">
        <div class="section-head">
          <h3>网站库</h3>
          <div class="stack-row">
            <button id="collapseAllBtn" class="soft-btn">全部收起</button>
            <button id="expandAllBtn" class="soft-btn">全部展开</button>
          </div>
        </div>
        <div id="siteGroups" class="groups-stack"></div>
      </section>

      <section class="view-section is-hidden" id="favoritesView">
        <div class="section-head">
          <h3>收藏夹</h3>
        </div>
        <div id="favoritesGrid" class="site-grid"></div>
      </section>

      <section class="view-section is-hidden" id="recentView">
        <div class="section-head">
          <h3>最近打开</h3>
        </div>
        <div id="recentGrid" class="site-grid"></div>
      </section>

      <section class="view-section is-hidden" id="settingsView">
        <div class="settings-layout">
          <article class="glass setting-card">
            <h3>主题</h3>
            <div class="theme-grid" id="themeGrid"></div>
          </article>

          <article class="glass setting-card">
            <h3>主页偏好</h3>
            <div class="setting-form">
              <label>
                <span>默认视图</span>
                <select id="defaultViewSelect">
                  <option value="dashboard">总览</option>
                  <option value="sites">网站库</option>
                  <option value="favorites">收藏夹</option>
                  <option value="recent">最近打开</option>
                </select>
              </label>
              <label>
                <span>每组初始展开</span>
                <select id="expandModeSelect">
                  <option value="smart">智能</option>
                  <option value="all">全部展开</option>
                  <option value="none">全部收起</option>
                </select>
              </label>
              <label class="switch-row">
                <input id="showOnlyHttpsInput" type="checkbox" />
                <span>优先显示 HTTPS 链接</span>
              </label>
            </div>
          </article>

          <article class="glass setting-card span-2">
            <h3>说明</h3>
            <ul class="info-list">
              <li>这个项目基于原生 JavaScript 模块拆分，便于继续扩展。</li>
              <li>天气模块使用 Open-Meteo 接口，默认不需要 API key。</li>
              <li>GitHub 模块使用公共 REST 接口，匿名请求有速率限制，前端已做缓存。</li>
              <li>定位天气依赖浏览器地理位置权限，并要求安全上下文或 localhost。</li>
            </ul>
          </article>
        </div>
      </section>
    </main>
  </div>

  <dialog id="siteDialog" class="modal-card">
    <form method="dialog" class="modal-shell" id="siteFormDialog">
      <header class="modal-head">
        <h3 id="siteDialogTitle">添加站点</h3>
        <button class="text-btn" value="cancel" aria-label="关闭">关闭</button>
      </header>
      <div class="modal-body form-grid">
        <label>
          <span>名称</span>
          <input name="name" required />
        </label>
        <label>
          <span>网址</span>
          <input name="url" required />
        </label>
        <label>
          <span>分类</span>
          <input name="category" required />
        </label>
        <label>
          <span>标签</span>
          <input name="tag" />
        </label>
        <label class="span-2">
          <span>描述</span>
          <textarea name="description" rows="4"></textarea>
        </label>
        <label class="switch-row span-2">
          <input name="pinned" type="checkbox" />
          <span>添加后直接置顶</span>
        </label>
      </div>
      <footer class="modal-foot">
        <button class="soft-btn" value="cancel">取消</button>
        <button id="saveSiteDialogBtn" class="primary-btn" value="default">保存</button>
      </footer>
    </form>
  </dialog>

  <dialog id="commandDialog" class="modal-card command-modal">
    <form method="dialog" class="modal-shell">
      <header class="modal-head">
        <h3>命令面板</h3>
        <button class="text-btn" value="cancel">关闭</button>
      </header>
      <div class="modal-body">
        <input id="commandInput" class="command-input" placeholder="输入命令或搜索站点，例如 theme light / github openai" />
        <div id="commandResults" class="command-results"></div>
      </div>
    </form>
  </dialog>

  <div id="toastStack" class="toast-stack" aria-live="polite" aria-atomic="true"></div>

  <script type="module" src="./assets/js/app.js"></script>
</body>
</html>
'''

reset_css = r'''
/* reset.css */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  line-height: 1.15;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  scroll-behavior: smooth;
}

body,
h1,
h2,
h3,
h4,
h5,
h6,
p,
figure,
blockquote,
dl,
dd {
  margin: 0;
}

ul[role='list'],
ol[role='list'],
ul,
ol {
  list-style: none;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  text-rendering: optimizeLegibility;
}

img,
picture,
svg,
canvas {
  max-width: 100%;
  display: block;
}

input,
button,
textarea,
select {
  font: inherit;
}

button,
select {
  text-transform: none;
}

a {
  text-decoration: none;
  color: inherit;
}

textarea {
  resize: vertical;
}

table {
  border-collapse: collapse;
  border-spacing: 0;
}

[hidden] {
  display: none !important;
}
'''

variables_css = r'''
:root {
  --bg: #0b1020;
  --bg-2: #111934;
  --surface: rgba(255, 255, 255, 0.08);
  --surface-2: rgba(255, 255, 255, 0.12);
  --surface-3: rgba(255, 255, 255, 0.16);
  --line: rgba(255, 255, 255, 0.12);
  --line-strong: rgba(255, 255, 255, 0.2);
  --text: #edf1ff;
  --muted: #b9c2ef;
  --accent: #88a4ff;
  --accent-2: #55e3c1;
  --accent-3: #ffc168;
  --danger: #ff7b8c;
  --warning: #ffd36e;
  --success: #62dca2;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.4);
  --radius-xs: 10px;
  --radius-sm: 14px;
  --radius-md: 18px;
  --radius-lg: 24px;
  --radius-xl: 32px;
  --gap-xs: 8px;
  --gap-sm: 12px;
  --gap-md: 16px;
  --gap-lg: 20px;
  --gap-xl: 28px;
  --max-width: 1600px;
  --font-stack: Inter, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
}

:root[data-theme='light'] {
  --bg: #edf2ff;
  --bg-2: #dfe7ff;
  --surface: rgba(255, 255, 255, 0.7);
  --surface-2: rgba(255, 255, 255, 0.84);
  --surface-3: rgba(255, 255, 255, 0.94);
  --line: rgba(19, 34, 84, 0.1);
  --line-strong: rgba(19, 34, 84, 0.18);
  --text: #162344;
  --muted: #516081;
  --accent: #5271ff;
  --accent-2: #00a58e;
  --accent-3: #cb8a1b;
  --danger: #d84a63;
  --warning: #a66a00;
  --success: #147c55;
  --shadow: 0 16px 40px rgba(78, 92, 136, 0.18);
}

:root[data-theme='violet'] {
  --bg: #110f23;
  --bg-2: #1b1835;
  --surface: rgba(255, 255, 255, 0.08);
  --surface-2: rgba(255, 255, 255, 0.12);
  --surface-3: rgba(255, 255, 255, 0.15);
  --line: rgba(255, 255, 255, 0.12);
  --line-strong: rgba(255, 255, 255, 0.2);
  --text: #f1eaff;
  --muted: #ccc1ef;
  --accent: #a078ff;
  --accent-2: #60d8ff;
  --accent-3: #f7c96c;
  --danger: #ff7f9e;
  --warning: #ffcf73;
  --success: #73e5b2;
  --shadow: 0 26px 80px rgba(7, 4, 20, 0.55);
}

:root[data-theme='forest'] {
  --bg: #0d1712;
  --bg-2: #15261c;
  --surface: rgba(255, 255, 255, 0.07);
  --surface-2: rgba(255, 255, 255, 0.1);
  --surface-3: rgba(255, 255, 255, 0.13);
  --line: rgba(255, 255, 255, 0.11);
  --line-strong: rgba(255, 255, 255, 0.18);
  --text: #effff6;
  --muted: #bcd5c9;
  --accent: #66d98e;
  --accent-2: #97f4d5;
  --accent-3: #f5cf73;
  --danger: #ff8ea0;
  --warning: #f4c24d;
  --success: #7fe6b2;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.4);
}
'''

base_css = r'''
body {
  font-family: var(--font-stack);
  color: var(--text);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 20%, transparent), transparent 30%),
    radial-gradient(circle at top right, color-mix(in srgb, var(--accent-2) 15%, transparent), transparent 22%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
  padding: 18px;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(circle at center, black 40%, transparent 90%);
  opacity: 0.28;
}

button,
input,
select,
textarea {
  color: inherit;
}

button {
  cursor: pointer;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
  min-height: 48px;
  padding: 0 14px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

textarea {
  min-height: 120px;
  padding: 14px;
}

input:focus,
select:focus,
textarea:focus {
  border-color: color-mix(in srgb, var(--accent) 65%, white);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 20%, transparent);
}

kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  min-height: 28px;
  padding: 0 8px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
}

::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--accent) 35%, transparent);
  border: 3px solid transparent;
  background-clip: content-box;
  border-radius: 999px;
}

::-webkit-scrollbar-track {
  background: transparent;
}
'''

layout_css = r'''
.app-shell {
  width: min(100%, var(--max-width));
  margin: 0 auto;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: var(--gap-lg);
}

.sidebar {
  padding: 22px;
  display: grid;
  align-content: start;
  gap: var(--gap-md);
  position: sticky;
  top: 18px;
  max-height: calc(100vh - 36px);
  overflow: auto;
}

.main-area {
  display: grid;
  gap: var(--gap-lg);
}

.topbar {
  padding: 22px;
  display: grid;
  gap: 18px;
}

.topbar-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--gap-md);
}

.topbar-actions,
.stack-row,
.hero-actions {
  display: flex;
  gap: var(--gap-sm);
  flex-wrap: wrap;
}

.search-grid {
  display: grid;
  grid-template-columns: 1.8fr 0.9fr 0.9fr;
  gap: var(--gap-md);
  align-items: end;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--gap-lg);
}

.widget-card,
.hero-card,
.setting-card,
.sidebar-card {
  padding: 20px;
}

.hero-card {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: var(--gap-lg);
  align-items: stretch;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--gap-sm);
}

.view-section {
  display: grid;
  gap: var(--gap-md);
}

.section-head,
.widget-head,
.sidebar-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--gap-sm);
}

.groups-stack {
  display: grid;
  gap: var(--gap-md);
}

.site-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--gap-md);
}

.settings-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--gap-lg);
}

.insight-layout {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--gap-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--gap-md);
}

.modal-shell {
  min-width: min(760px, calc(100vw - 32px));
  display: grid;
  gap: var(--gap-md);
}

.modal-head,
.modal-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--gap-md);
}

.modal-body {
  display: grid;
  gap: var(--gap-md);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--gap-md);
}

@media (max-width: 1200px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    max-height: none;
  }

  .dashboard-grid,
  .settings-layout,
  .insight-layout,
  .hero-card,
  .search-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  body {
    padding: 10px;
  }

  .sidebar,
  .topbar,
  .widget-card,
  .hero-card,
  .setting-card,
  .sidebar-card {
    padding: 16px;
  }

  .form-grid,
  .theme-grid,
  .site-grid {
    grid-template-columns: 1fr;
  }

  .topbar-main,
  .widget-head,
  .section-head,
  .sidebar-card-head,
  .modal-head,
  .modal-foot {
    flex-direction: column;
    align-items: stretch;
  }
}
'''

components_css = r'''
.glass {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
}

.brand-block {
  display: flex;
  gap: var(--gap-md);
  align-items: center;
}

.brand-mark {
  inline-size: 54px;
  block-size: 54px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  display: grid;
  place-items: center;
  color: white;
  font-weight: 900;
  font-size: 24px;
}

.brand-title {
  font-size: 22px;
  line-height: 1.1;
}

.brand-subtitle,
.sidebar-muted,
.field-label,
.metric-label,
.site-meta,
.muted,
.page-subtitle,
.command-empty,
.widget-subtext,
.eyebrow {
  color: var(--muted);
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 12px;
  font-weight: 700;
}

.page-title {
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.05;
}

.side-nav {
  display: grid;
  gap: 8px;
}

.side-nav-item,
.soft-btn,
.primary-btn,
.text-btn,
.chip,
.theme-swatch,
.site-action,
.metric-card,
.command-row {
  transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.side-nav-item {
  min-height: 46px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
  text-align: left;
  padding: 0 14px;
  font-weight: 700;
}

.side-nav-item.is-active,
.side-nav-item:hover {
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  border-color: color-mix(in srgb, var(--accent) 45%, transparent);
}

.soft-btn,
.primary-btn,
.text-btn,
.site-action,
.chip,
.theme-swatch {
  min-height: 44px;
  border-radius: 14px;
  border: 1px solid var(--line);
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
  font-weight: 700;
}

.primary-btn {
  background: linear-gradient(135deg, var(--accent), color-mix(in srgb, var(--accent-2) 40%, var(--accent)));
  color: white;
  border: none;
}

.text-btn {
  min-height: 34px;
  padding: 0 10px;
  background: transparent;
}

.soft-btn:hover,
.primary-btn:hover,
.text-btn:hover,
.chip:hover,
.theme-swatch:hover,
.site-action:hover,
.metric-card:hover,
.command-row:hover {
  transform: translateY(-2px);
}

.text-btn.danger,
.danger {
  color: var(--danger);
}

.full {
  width: 100%;
}

.file-btn {
  position: relative;
  overflow: hidden;
}

.shortcut-list {
  display: grid;
  gap: 10px;
}

.shortcut-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-field {
  display: grid;
  gap: 8px;
}

.chip-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.chip.is-active {
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  border-color: color-mix(in srgb, var(--accent) 45%, transparent);
}

.metric-card {
  border-radius: 18px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--line);
  display: grid;
  gap: 10px;
}

.metric-label {
  font-size: 13px;
}

.metric-value {
  font-size: 28px;
  font-weight: 900;
  line-height: 1;
}

.hero-copy {
  display: grid;
  gap: 14px;
  align-content: center;
}

.hero-copy h3 {
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.08;
  letter-spacing: -0.03em;
}

.hero-copy p,
.info-list,
.site-description,
.command-row p,
.widget-body,
.weather-meta,
.weather-secondary,
.github-meta,
.insight-item,
.setting-form,
.setting-form label,
.group-summary p {
  line-height: 1.7;
}

.compact-form {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 10px;
}

.group-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  background: var(--surface);
  overflow: hidden;
}

.group-summary {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  cursor: pointer;
}

.group-left {
  display: flex;
  gap: 14px;
  align-items: center;
}

.group-icon {
  inline-size: 46px;
  block-size: 46px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  display: grid;
  place-items: center;
  font-size: 22px;
}

.group-body {
  padding: 0 20px 20px;
}

.site-card {
  position: relative;
  border-radius: 20px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.05);
  padding: 18px;
  display: grid;
  gap: 12px;
  min-height: 220px;
}

.site-card.is-pinned {
  outline: 1px solid color-mix(in srgb, var(--accent-3) 50%, transparent);
}

.site-card.is-favorite {
  outline: 1px solid color-mix(in srgb, var(--accent-2) 50%, transparent);
}

.site-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
}

.site-title-wrap {
  display: grid;
  gap: 8px;
}

.site-title {
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -0.02em;
}

.site-badges,
.weather-tags,
.github-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  font-size: 12px;
  font-weight: 800;
}

.badge.alt {
  background: color-mix(in srgb, var(--accent-2) 12%, transparent);
}

.badge.warn {
  background: color-mix(in srgb, var(--accent-3) 18%, transparent);
}

.site-url {
  font-size: 12px;
  color: color-mix(in srgb, var(--accent) 70%, white);
  word-break: break-all;
}

.site-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
}

.site-action[data-kind='open'] {
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  border-color: color-mix(in srgb, var(--accent) 45%, transparent);
}

.site-action.danger {
  color: var(--danger);
}

.widget-body {
  min-height: 200px;
}

.weather-main,
.github-main,
.command-results,
.recent-list,
.tips-list,
.hot-list {
  display: grid;
  gap: 10px;
}

.weather-temp {
  font-size: 48px;
  font-weight: 900;
  line-height: 1;
}

.weather-grid,
.github-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.weather-cell,
.github-cell,
.insight-item {
  border-radius: 16px;
  border: 1px solid var(--line);
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.05);
}

.insight-item strong {
  display: block;
  font-size: 18px;
  margin-bottom: 6px;
}

.command-input {
  min-height: 54px;
}

.command-row {
  width: 100%;
  text-align: left;
  border-radius: 14px;
  border: 1px solid var(--line);
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.04);
}

.command-row.is-active {
  border-color: color-mix(in srgb, var(--accent) 55%, transparent);
  background: color-mix(in srgb, var(--accent) 18%, transparent);
}

.command-row h4 {
  margin-bottom: 4px;
}

.modal-card {
  border: none;
  padding: 0;
  background: transparent;
}

.modal-card::backdrop {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
}

.modal-shell {
  background: color-mix(in srgb, var(--bg) 60%, black 20%);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 20px;
}

.setting-card h3,
.widget-head h3,
.section-head h3,
.modal-head h3,
.sidebar-card h2 {
  font-size: 20px;
}

.setting-form {
  display: grid;
  gap: 14px;
}

.setting-form label {
  display: grid;
  gap: 8px;
}

.switch-row {
  display: flex !important;
  align-items: center;
  gap: 10px;
}

.switch-row input {
  width: 22px;
  height: 22px;
  min-height: auto;
  padding: 0;
}

.theme-swatch {
  padding: 14px;
  min-height: 96px;
  align-items: start;
  justify-content: start;
  text-align: left;
}

.theme-swatch.is-active {
  border-color: color-mix(in srgb, var(--accent) 60%, transparent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 15%, transparent);
}

.theme-preview {
  display: flex;
  gap: 8px;
}

.theme-dot {
  width: 16px;
  height: 16px;
  border-radius: 999px;
}

.info-list {
  display: grid;
  gap: 12px;
  padding-left: 18px;
  list-style: disc;
}

.skeleton-lines {
  position: relative;
  overflow: hidden;
}

.skeleton-lines::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
  animation: shimmer 1.6s infinite;
}

.toast-stack {
  position: fixed;
  right: 16px;
  bottom: 16px;
  display: grid;
  gap: 12px;
  z-index: 1000;
}

.toast {
  min-width: 260px;
  max-width: 360px;
  padding: 14px 16px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--bg) 70%, black 10%);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.toast strong {
  display: block;
  margin-bottom: 6px;
}

.is-hidden {
  display: none !important;
}

.span-2 {
  grid-column: span 2;
}

@media (max-width: 1200px) {
  .span-2 {
    grid-column: auto;
  }
}

@media (max-width: 720px) {
  .compact-form,
  .weather-grid,
  .github-grid {
    grid-template-columns: 1fr;
  }
}
'''

animations_css = r'''
@keyframes shimmer {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(100%);
  }
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(18px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.site-card,
.group-card,
.metric-card,
.widget-card,
.hero-card,
.setting-card,
.sidebar-card,
.toast {
  animation: popIn 0.24s ease;
}

.toast {
  animation: slideInRight 0.22s ease;
}
'''

utilities_css = r'''
.text-center { text-align: center; }
.mt-0 { margin-top: 0; }
.mb-0 { margin-bottom: 0; }
.w-full { width: 100%; }
.flex { display: flex; }
.grid { display: grid; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-8 { gap: 8px; }
.gap-12 { gap: 12px; }
.gap-16 { gap: 16px; }
.rounded { border-radius: var(--radius-md); }
.overflow-hidden { overflow: hidden; }
.opacity-70 { opacity: 0.7; }
.opacity-80 { opacity: 0.8; }
.opacity-90 { opacity: 0.9; }
'''

utils_js = r'''
export function slugify(value = '') {
  return String(value)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function uid(prefix = 'id') {
  const token = typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `${prefix}-${token}`;
}

export function safeParse(json, fallback) {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

export function normalizeUrl(url = '') {
  const trimmed = url.trim();
  if (!trimmed) return '';
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}

export function formatNumber(num = 0) {
  return new Intl.NumberFormat('zh-CN').format(num);
}

export function clamp(num, min, max) {
  return Math.min(Math.max(num, min), max);
}

export function pick(array = []) {
  return array[Math.floor(Math.random() * array.length)] ?? null;
}

export function toDateLabel(dateLike) {
  const date = new Date(dateLike);
  if (Number.isNaN(date.getTime())) return '未知';
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function groupBy(items, keyGetter) {
  const map = new Map();
  for (const item of items) {
    const key = keyGetter(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return map;
}

export function sortByName(a, b) {
  return String(a.name).localeCompare(String(b.name), 'zh-CN');
}

export function sortByNameDesc(a, b) {
  return String(b.name).localeCompare(String(a.name), 'zh-CN');
}

export function debounce(fn, wait = 180) {
  let timer = 0;
  return (...args) => {
    clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), wait);
  };
}

export function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function copyText(text) {
  if (navigator.clipboard?.writeText) {
    return navigator.clipboard.writeText(text);
  }
  const temp = document.createElement('textarea');
  temp.value = text;
  document.body.append(temp);
  temp.select();
  document.execCommand('copy');
  temp.remove();
  return Promise.resolve();
}

export function percentage(part, whole) {
  if (!whole) return '0%';
  return `${Math.round((part / whole) * 100)}%`;
}

export function coerceBoolean(value) {
  return value === true || value === 'true' || value === 1 || value === '1';
}
'''

storage_js = r'''
import { safeParse } from './utils.js';

const APP_KEY = 'navigator-pro-state-v1';
const CACHE_KEY = 'navigator-pro-cache-v1';

export function loadState(defaultState) {
  const raw = localStorage.getItem(APP_KEY);
  const parsed = raw ? safeParse(raw, null) : null;
  return parsed ? { ...defaultState, ...parsed } : structuredClone(defaultState);
}

export function saveState(state) {
  localStorage.setItem(APP_KEY, JSON.stringify(state));
}

export function loadCache() {
  return safeParse(localStorage.getItem(CACHE_KEY) || '{}', {});
}

export function saveCache(cache) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}

export function setCacheRecord(key, value) {
  const cache = loadCache();
  cache[key] = value;
  saveCache(cache);
}

export function getCacheRecord(key) {
  const cache = loadCache();
  return cache[key];
}

export function exportState(state) {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `navigator-pro-backup-${Date.now()}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function importState(file) {
  const text = await file.text();
  return safeParse(text, null);
}

export function clearAllStorage() {
  localStorage.removeItem(APP_KEY);
  localStorage.removeItem(CACHE_KEY);
}
'''

state_js = r'''
import { builtinSites, builtinThemes } from './data/sites.js';
import { uid } from './utils.js';

export const defaultState = {
  ui: {
    currentView: 'dashboard',
    search: '',
    category: 'all',
    sort: 'smart',
    filter: 'all',
    theme: 'dark',
    commandQuery: '',
    defaultView: 'dashboard',
    expandMode: 'smart',
    showOnlyHttps: false
  },
  data: {
    builtinSites,
    customSites: [],
    favorites: [],
    pinned: [],
    opens: {},
    recents: [],
    weather: {
      city: 'New York',
      lastQuery: null,
      result: null,
      lastUpdated: null
    },
    github: {
      username: 'openai',
      result: null,
      lastUpdated: null
    }
  },
  meta: {
    version: 1,
    createdAt: new Date().toISOString(),
    installId: uid('install')
  },
  themes: builtinThemes
};

export function mergeState(base, incoming) {
  return {
    ...base,
    ...incoming,
    ui: { ...base.ui, ...(incoming.ui || {}) },
    data: {
      ...base.data,
      ...(incoming.data || {}),
      weather: { ...base.data.weather, ...(incoming.data?.weather || {}) },
      github: { ...base.data.github, ...(incoming.data?.github || {}) }
    },
    meta: { ...base.meta, ...(incoming.meta || {}) },
    themes: incoming.themes || base.themes
  };
}

export function getAllSites(state) {
  return [
    ...state.data.builtinSites.map(site => ({ ...site, source: 'builtin' })),
    ...state.data.customSites.map(site => ({ ...site, source: 'custom' }))
  ];
}

export function isFavorite(state, id) {
  return state.data.favorites.includes(id);
}

export function isPinned(state, id) {
  return state.data.pinned.includes(id);
}

export function getOpenCount(state, id) {
  return state.data.opens[id] || 0;
}

export function touchRecent(state, site) {
  const trimmed = state.data.recents.filter(item => item.id !== site.id);
  trimmed.unshift({
    id: site.id,
    name: site.name,
    url: site.url,
    category: site.category,
    openedAt: new Date().toISOString()
  });
  state.data.recents = trimmed.slice(0, 40);
}

export function recordOpen(state, site) {
  state.data.opens[site.id] = (state.data.opens[site.id] || 0) + 1;
  touchRecent(state, site);
}
'''

notify_js = r'''
let stack;

export function initNotifier() {
  stack = document.getElementById('toastStack');
}

export function toast(title, message = '', timeout = 2600) {
  if (!stack) return;
  const node = document.createElement('div');
  node.className = 'toast';
  node.innerHTML = `<strong>${title}</strong><div>${message}</div>`;
  stack.append(node);
  window.setTimeout(() => {
    node.remove();
  }, timeout);
}
'''

modal_js = r'''
export function openDialog(dialog) {
  if (!dialog.open) dialog.showModal();
}

export function closeDialog(dialog) {
  if (dialog.open) dialog.close();
}
'''

theme_js = r'''
import { toast } from './notify.js';

export function applyTheme(themeId) {
  document.documentElement.dataset.theme = themeId;
}

export function renderThemeGrid(container, themes, currentTheme, onPick) {
  container.innerHTML = themes.map(theme => `
    <button class="theme-swatch ${theme.id === currentTheme ? 'is-active' : ''}" data-theme="${theme.id}">
      <div>
        <strong>${theme.name}</strong>
        <p class="muted">${theme.description}</p>
      </div>
      <div class="theme-preview">
        ${theme.preview.map(color => `<span class="theme-dot" style="background:${color}"></span>`).join('')}
      </div>
    </button>
  `).join('');

  container.querySelectorAll('[data-theme]').forEach(button => {
    button.addEventListener('click', () => {
      onPick(button.dataset.theme);
      toast('主题已切换', `当前主题：${button.dataset.theme}`);
    });
  });
}
'''

dom_js = r'''
export function qs(selector, scope = document) {
  return scope.querySelector(selector);
}

export function qsa(selector, scope = document) {
  return [...scope.querySelectorAll(selector)];
}

export function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
}

export function createFragment(html) {
  const tpl = document.createElement('template');
  tpl.innerHTML = html.trim();
  return tpl.content;
}
'''

weather_js = r'''
import { getCacheRecord, setCacheRecord } from '../storage.js';

const WEATHER_CACHE_TTL = 1000 * 60 * 15;

function isFresh(record) {
  return record && Date.now() - record.savedAt < WEATHER_CACHE_TTL;
}

export async function searchCity(city) {
  const cacheKey = `geo:${city.toLowerCase()}`;
  const cached = getCacheRecord(cacheKey);
  if (isFresh(cached)) return cached.data;

  const url = new URL('https://geocoding-api.open-meteo.com/v1/search');
  url.searchParams.set('name', city);
  url.searchParams.set('count', '5');
  url.searchParams.set('language', 'en');
  url.searchParams.set('format', 'json');

  const response = await fetch(url);
  if (!response.ok) throw new Error('城市查询失败');
  const json = await response.json();
  setCacheRecord(cacheKey, { savedAt: Date.now(), data: json });
  return json;
}

export async function getForecastByCoords(latitude, longitude) {
  const cacheKey = `weather:${latitude.toFixed(3)},${longitude.toFixed(3)}`;
  const cached = getCacheRecord(cacheKey);
  if (isFresh(cached)) return cached.data;

  const url = new URL('https://api.open-meteo.com/v1/forecast');
  url.searchParams.set('latitude', String(latitude));
  url.searchParams.set('longitude', String(longitude));
  url.searchParams.set('current', 'temperature_2m,apparent_temperature,wind_speed_10m,relative_humidity_2m,weather_code');
  url.searchParams.set('daily', 'temperature_2m_max,temperature_2m_min,precipitation_probability_max');
  url.searchParams.set('timezone', 'auto');
  url.searchParams.set('forecast_days', '3');

  const response = await fetch(url);
  if (!response.ok) throw new Error('天气请求失败');
  const json = await response.json();
  setCacheRecord(cacheKey, { savedAt: Date.now(), data: json });
  return json;
}

export function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('当前浏览器不支持定位'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      position => resolve(position.coords),
      error => reject(error),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 }
    );
  });
}

export function weatherCodeLabel(code) {
  const map = {
    0: '晴朗',
    1: '大体晴朗',
    2: '局部多云',
    3: '阴天',
    45: '有雾',
    48: '冻雾',
    51: '小毛雨',
    53: '毛雨',
    55: '强毛雨',
    61: '小雨',
    63: '中雨',
    65: '大雨',
    71: '小雪',
    73: '中雪',
    75: '大雪',
    80: '阵雨',
    95: '雷暴'
  };
  return map[code] || `代码 ${code}`;
}
'''

github_js = r'''
import { getCacheRecord, setCacheRecord } from '../storage.js';

const GITHUB_CACHE_TTL = 1000 * 60 * 20;

function isFresh(record) {
  return record && Date.now() - record.savedAt < GITHUB_CACHE_TTL;
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  });
  if (!response.ok) {
    throw new Error(`GitHub 请求失败: ${response.status}`);
  }
  return response.json();
}

export async function getGithubProfile(username) {
  const cacheKey = `gh:${username.toLowerCase()}`;
  const cached = getCacheRecord(cacheKey);
  if (isFresh(cached)) return cached.data;

  const [profile, repos] = await Promise.all([
    fetchJson(`https://api.github.com/users/${encodeURIComponent(username)}`),
    fetchJson(`https://api.github.com/users/${encodeURIComponent(username)}/repos?sort=updated&per_page=6&type=owner`)
  ]);

  const data = { profile, repos };
  setCacheRecord(cacheKey, { savedAt: Date.now(), data });
  return data;
}
'''

tips_js = r'''
export const efficiencyTips = [
  '把首页放成真正会用的入口，少放看起来厉害但几乎不用的网站。',
  '收藏夹不要超过 20 个高频站点，剩下的放入分类库。',
  '给每个站点写一句用途说明，搜索时判断会快很多。',
  '每周清理一次最近访问和无效链接，减少认知噪音。',
  '用打开次数筛选出真正高频网站，再决定哪些需要置顶。',
  '把学习类、开发类、工具类分开，避免不同任务心智混在一起。',
  '天气、GitHub、最近访问都属于次级信息，主入口永远是搜索。',
  '所有新增站点都先进入普通分类，确认一周后再决定是否收藏。',
  '经常卡住时，用命令面板比来回滚动找卡片更快。',
  '如果首页越来越乱，说明你在囤入口而不是设计工作流。'
];
'''

# Generate a large catalog of sites.
categories = [
    ('学习', '📚', [
        ('Khan Academy', '免费系统课程与练习'),
        ('MIT OpenCourseWare', '大学公开课与讲义'),
        ('Coursera', '系统课程与证书'),
        ('edX', '名校公开课'),
        ('Brilliant', '交互式 STEM 学习'),
        ('Project Gutenberg', '公共版权图书库'),
        ('Internet Archive', '档案与历史资源'),
        ('Archive.org TV News', '新闻检索')
    ]),
    ('数学', '∑', [
        ('Wolfram Alpha', '计算与推导'),
        ('Desmos', '图形计算器'),
        ('GeoGebra', '动态数学工具'),
        ('Paul Math Notes', '微积分笔记'),
        ('OEIS', '整数数列数据库'),
        ('MathWorld', '数学百科'),
        ('Cut the Knot', '数学思维题'),
        ('nLab', '高阶数学条目')
    ]),
    ('开发', '💻', [
        ('GitHub', '代码托管平台'),
        ('MDN', 'Web 文档'),
        ('Stack Overflow', '编程问答'),
        ('npm', 'Node 包索引'),
        ('PyPI', 'Python 包索引'),
        ('Crates.io', 'Rust 包索引'),
        ('Rust Docs', 'Rust 官方文档'),
        ('TypeScript Docs', 'TS 官方文档')
    ]),
    ('AI', '🤖', [
        ('ChatGPT', '通用 AI 助手'),
        ('Hugging Face', '模型与数据集'),
        ('Papers with Code', '论文与代码'),
        ('Perplexity', '搜索增强问答'),
        ('Anthropic Claude', '长文本助手'),
        ('Google AI Studio', '模型实验'),
        ('OpenRouter', '模型路由'),
        ('Replicate', '模型推理服务')
    ]),
    ('设计', '🎨', [
        ('Canva', '快速设计'),
        ('Figma', '界面设计'),
        ('Coolors', '配色工具'),
        ('Behance', '作品灵感'),
        ('Dribbble', '设计灵感'),
        ('Excalidraw', '草图白板'),
        ('Squoosh', '图像压缩'),
        ('Remove.bg', '抠图工具')
    ]),
    ('效率', '⚙️', [
        ('Notion', '笔记与项目管理'),
        ('Trello', '看板管理'),
        ('Linear', '任务跟踪'),
        ('Todoist', '任务管理'),
        ('Google Drive', '云端存储'),
        ('Dropbox', '云文件'),
        ('Calendly', '预约工具'),
        ('Pomofocus', '番茄钟')
    ]),
    ('媒体', '🎬', [
        ('YouTube', '视频平台'),
        ('Vimeo', '视频托管'),
        ('Twitch', '直播平台'),
        ('Spotify', '音乐流媒体'),
        ('SoundCloud', '音频社区'),
        ('Apple Podcasts', '播客目录'),
        ('IMDb', '影视资料'),
        ('Letterboxd', '电影记录')
    ]),
    ('资讯', '📰', [
        ('Reuters', '国际新闻'),
        ('AP News', '新闻通讯社'),
        ('The Verge', '科技媒体'),
        ('Ars Technica', '技术深度'),
        ('Bloomberg', '商业资讯'),
        ('Financial Times', '金融报道'),
        ('Hacker News', '技术社区'),
        ('Lobsters', '程序员新闻')
    ]),
    ('工具', '🧰', [
        ('JSON Formatter', 'JSON 美化'),
        ('Regex101', '正则测试'),
        ('CyberChef', '编码与解码工具'),
        ('Speedtest', '网络测速'),
        ('TinyWow', '轻量在线工具'),
        ('Temp Mail', '临时邮箱'),
        ('SVGOMG', 'SVG 优化'),
        ('Diffchecker', '文本对比')
    ]),
    ('云服务', '☁️', [
        ('Cloudflare', 'CDN 与安全'),
        ('Vercel', '前端部署'),
        ('Netlify', '静态站托管'),
        ('Render', '云端部署'),
        ('Railway', '服务部署'),
        ('Supabase', '后端服务'),
        ('Firebase', 'Google 后端'),
        ('PlanetScale', '数据库服务')
    ]),
]

# base domains mapping, generic fallback.
base_domains = {
    'Khan Academy': 'https://www.khanacademy.org/',
    'MIT OpenCourseWare': 'https://ocw.mit.edu/',
    'Coursera': 'https://www.coursera.org/',
    'edX': 'https://www.edx.org/',
    'Brilliant': 'https://brilliant.org/',
    'Project Gutenberg': 'https://www.gutenberg.org/',
    'Internet Archive': 'https://archive.org/',
    'Archive.org TV News': 'https://archive.org/details/tv',
    'Wolfram Alpha': 'https://www.wolframalpha.com/',
    'Desmos': 'https://www.desmos.com/',
    'GeoGebra': 'https://www.geogebra.org/',
    'Paul Math Notes': 'https://tutorial.math.lamar.edu/',
    'OEIS': 'https://oeis.org/',
    'MathWorld': 'https://mathworld.wolfram.com/',
    'Cut the Knot': 'http://www.cut-the-knot.org/',
    'nLab': 'https://ncatlab.org/nlab/show/HomePage',
    'GitHub': 'https://github.com/',
    'MDN': 'https://developer.mozilla.org/',
    'Stack Overflow': 'https://stackoverflow.com/',
    'npm': 'https://www.npmjs.com/',
    'PyPI': 'https://pypi.org/',
    'Crates.io': 'https://crates.io/',
    'Rust Docs': 'https://doc.rust-lang.org/',
    'TypeScript Docs': 'https://www.typescriptlang.org/docs/',
    'ChatGPT': 'https://chatgpt.com/',
    'Hugging Face': 'https://huggingface.co/',
    'Papers with Code': 'https://paperswithcode.com/',
    'Perplexity': 'https://www.perplexity.ai/',
    'Anthropic Claude': 'https://claude.ai/',
    'Google AI Studio': 'https://aistudio.google.com/',
    'OpenRouter': 'https://openrouter.ai/',
    'Replicate': 'https://replicate.com/',
    'Canva': 'https://www.canva.com/',
    'Figma': 'https://www.figma.com/',
    'Coolors': 'https://coolors.co/',
    'Behance': 'https://www.behance.net/',
    'Dribbble': 'https://dribbble.com/',
    'Excalidraw': 'https://excalidraw.com/',
    'Squoosh': 'https://squoosh.app/',
    'Remove.bg': 'https://www.remove.bg/',
    'Notion': 'https://www.notion.so/',
    'Trello': 'https://trello.com/',
    'Linear': 'https://linear.app/',
    'Todoist': 'https://todoist.com/',
    'Google Drive': 'https://drive.google.com/',
    'Dropbox': 'https://www.dropbox.com/',
    'Calendly': 'https://calendly.com/',
    'Pomofocus': 'https://pomofocus.io/',
    'YouTube': 'https://www.youtube.com/',
    'Vimeo': 'https://vimeo.com/',
    'Twitch': 'https://www.twitch.tv/',
    'Spotify': 'https://open.spotify.com/',
    'SoundCloud': 'https://soundcloud.com/',
    'Apple Podcasts': 'https://podcasts.apple.com/',
    'IMDb': 'https://www.imdb.com/',
    'Letterboxd': 'https://letterboxd.com/',
    'Reuters': 'https://www.reuters.com/',
    'AP News': 'https://apnews.com/',
    'The Verge': 'https://www.theverge.com/',
    'Ars Technica': 'https://arstechnica.com/',
    'Bloomberg': 'https://www.bloomberg.com/',
    'Financial Times': 'https://www.ft.com/',
    'Hacker News': 'https://news.ycombinator.com/',
    'Lobsters': 'https://lobste.rs/',
    'JSON Formatter': 'https://jsonformatter.org/',
    'Regex101': 'https://regex101.com/',
    'CyberChef': 'https://gchq.github.io/CyberChef/',
    'Speedtest': 'https://www.speedtest.net/',
    'TinyWow': 'https://tinywow.com/',
    'Temp Mail': 'https://temp-mail.org/',
    'SVGOMG': 'https://jakearchibald.github.io/svgomg/',
    'Diffchecker': 'https://www.diffchecker.com/',
    'Cloudflare': 'https://dash.cloudflare.com/',
    'Vercel': 'https://vercel.com/',
    'Netlify': 'https://www.netlify.com/',
    'Render': 'https://render.com/',
    'Railway': 'https://railway.com/',
    'Supabase': 'https://supabase.com/',
    'Firebase': 'https://firebase.google.com/',
    'PlanetScale': 'https://planetscale.com/',
}

sites = []
site_id = 1
for category, icon, seeds in categories:
    for round_index in range(1, 9):  # 8 rounds -> 10*8*8? Actually 10 categories *8 seeds*8 rounds = 640 lines entries approx
        for idx, (name, desc) in enumerate(seeds, start=1):
            variant = f"{name} {round_index}" if round_index > 1 else name
            domain = base_domains.get(name, 'https://example.com/')
            if round_index > 1:
                url = domain.rstrip('/') + f"/?ref=navpro-{round_index}-{idx}"
            else:
                url = domain
            sites.append({
                'id': f'site-{site_id:04d}',
                'name': variant,
                'baseName': name,
                'url': url,
                'category': category,
                'icon': icon,
                'tag': desc.split('与')[0].split('、')[0],
                'description': f'{desc}。第 {round_index} 组资源，用于扩充导航库与测试搜索、排序、收藏、导入导出等完整功能。',
                'keywords': [category, name, desc, f'round-{round_index}'],
                'updatedAt': f'2026-03-{(idx + round_index) % 28 + 1:02d}T12:00:00.000Z'
            })
            site_id += 1

builtin_themes = [
    {'id': 'dark', 'name': 'Dark', 'description': '默认深色主题，适合长时间使用。', 'preview': ['#0b1020', '#88a4ff', '#55e3c1']},
    {'id': 'light', 'name': 'Light', 'description': '明亮清爽，适合白天环境。', 'preview': ['#edf2ff', '#5271ff', '#00a58e']},
    {'id': 'violet', 'name': 'Violet', 'description': '偏紫色的高对比主题。', 'preview': ['#110f23', '#a078ff', '#60d8ff']},
    {'id': 'forest', 'name': 'Forest', 'description': '深绿色低刺激主题。', 'preview': ['#0d1712', '#66d98e', '#97f4d5']},
]

data_sites_js = 'export const builtinSites = ' + json.dumps(sites, ensure_ascii=False, indent=2) + ';\n\n' + 'export const builtinThemes = ' + json.dumps(builtin_themes, ensure_ascii=False, indent=2) + ';\n'

renderers_js = r'''
import { escapeHtml, formatNumber, toDateLabel } from '../utils.js';
import { isFavorite, isPinned, getOpenCount } from '../state.js';

export function renderMetrics(state) {
  const allSites = [...state.data.builtinSites, ...state.data.customSites];
  const metrics = [
    { label: '总站点', value: allSites.length },
    { label: '收藏数', value: state.data.favorites.length },
    { label: '置顶数', value: state.data.pinned.length },
    { label: '最近打开', value: state.data.recents.length }
  ];
  return metrics.map(metric => `
    <div class="metric-card">
      <span class="metric-label">${metric.label}</span>
      <strong class="metric-value">${formatNumber(metric.value)}</strong>
    </div>
  `).join('');
}

export function renderSiteCard(site, state, options = {}) {
  const favorite = isFavorite(state, site.id);
  const pinned = isPinned(state, site.id);
  const openCount = getOpenCount(state, site.id);
  const removable = site.source === 'custom';
  return `
    <article class="site-card ${favorite ? 'is-favorite' : ''} ${pinned ? 'is-pinned' : ''}" data-site-id="${site.id}">
      <div class="site-card-head">
        <div class="site-title-wrap">
          <div class="site-badges">
            <span class="badge">${escapeHtml(site.category)}</span>
            <span class="badge alt">${escapeHtml(site.tag || site.source)}</span>
            ${pinned ? '<span class="badge warn">置顶</span>' : ''}
            ${favorite ? '<span class="badge alt">收藏</span>' : ''}
          </div>
          <div class="site-title">${escapeHtml(site.name)}</div>
        </div>
        <div class="group-icon">${escapeHtml(site.icon || '🌐')}</div>
      </div>
      <p class="site-description">${escapeHtml(site.description || '无描述')}</p>
      <div class="site-url">${escapeHtml(site.url)}</div>
      <div class="site-meta">来源: ${escapeHtml(site.source)} · 打开次数: ${formatNumber(openCount)} · 更新: ${toDateLabel(site.updatedAt)}</div>
      <div class="site-actions">
        <button class="site-action" data-kind="open">打开</button>
        <button class="site-action" data-kind="favorite">${favorite ? '取消收藏' : '收藏'}</button>
        <button class="site-action" data-kind="pin">${pinned ? '取消置顶' : '置顶'}</button>
        <button class="site-action" data-kind="copy">复制链接</button>
        ${removable ? '<button class="site-action danger" data-kind="delete">删除</button>' : ''}
      </div>
    </article>
  `;
}

export function renderGroup(group, sites, expanded = false, state) {
  return `
    <details class="group-card" ${expanded ? 'open' : ''}>
      <summary class="group-summary">
        <div class="group-left">
          <div class="group-icon">${escapeHtml(group.icon)}</div>
          <div>
            <strong>${escapeHtml(group.category)}</strong>
            <p>${sites.length} 个站点</p>
          </div>
        </div>
        <span class="muted">点击展开</span>
      </summary>
      <div class="group-body">
        <div class="site-grid">
          ${sites.map(site => renderSiteCard(site, state)).join('')}
        </div>
      </div>
    </details>
  `;
}

export function renderWeather(weather) {
  if (!weather) {
    return '<div class="muted">暂无天气数据</div>';
  }
  const current = weather.current;
  const daily = weather.daily;
  return `
    <div class="weather-main">
      <div class="weather-tags">
        <span class="badge">${escapeHtml(weather.cityName || '未知位置')}</span>
        <span class="badge alt">${escapeHtml(weather.summary || '天气')}</span>
      </div>
      <div class="weather-temp">${Math.round(current.temperature_2m)}°</div>
      <div class="weather-grid">
        <div class="weather-cell"><strong>体感</strong><div>${Math.round(current.apparent_temperature)}°</div></div>
        <div class="weather-cell"><strong>湿度</strong><div>${current.relative_humidity_2m}%</div></div>
        <div class="weather-cell"><strong>风速</strong><div>${current.wind_speed_10m} km/h</div></div>
        <div class="weather-cell"><strong>降水概率</strong><div>${daily.precipitation_probability_max?.[0] ?? '-'}%</div></div>
      </div>
      <div class="weather-secondary">
        未来三天: ${daily.temperature_2m_min.map((min, index) => `第${index + 1}天 ${Math.round(min)}°/${Math.round(daily.temperature_2m_max[index])}°`).join(' · ')}
      </div>
    </div>
  `;
}

export function renderGithub(data) {
  if (!data) return '<div class="muted">暂无 GitHub 数据</div>';
  const { profile, repos } = data;
  return `
    <div class="github-main">
      <div class="github-tags">
        <span class="badge">@${escapeHtml(profile.login)}</span>
        <span class="badge alt">${escapeHtml(profile.type)}</span>
      </div>
      <div class="github-grid">
        <div class="github-cell"><strong>公开仓库</strong><div>${profile.public_repos}</div></div>
        <div class="github-cell"><strong>关注者</strong><div>${profile.followers}</div></div>
        <div class="github-cell"><strong>Following</strong><div>${profile.following}</div></div>
        <div class="github-cell"><strong>最新活动仓库</strong><div>${repos.length}</div></div>
      </div>
      <div class="recent-list">
        ${repos.map(repo => `
          <div class="insight-item">
            <strong>${escapeHtml(repo.name)}</strong>
            <div>${escapeHtml(repo.description || '无描述')}</div>
            <div class="muted">⭐ ${repo.stargazers_count} · Fork ${repo.forks_count} · ${escapeHtml(repo.language || '未知语言')}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

export function renderRecents(recents) {
  if (!recents.length) return '<div class="muted">还没有最近访问记录</div>';
  return recents.map(item => `
    <div class="insight-item">
      <strong>${escapeHtml(item.name)}</strong>
      <div>${escapeHtml(item.category)}</div>
      <div class="muted">${toDateLabel(item.openedAt)}</div>
    </div>
  `).join('');
}

export function renderHotCategories(summary) {
  if (!summary.length) return '<div class="muted">暂无分类统计</div>';
  return summary.map(item => `
    <div class="insight-item">
      <strong>${escapeHtml(item.category)}</strong>
      <div>站点数 ${item.count}</div>
    </div>
  `).join('');
}

export function renderTips(tips) {
  return tips.map(tip => `
    <div class="insight-item">
      <strong>提示</strong>
      <div>${escapeHtml(tip)}</div>
    </div>
  `).join('');
}

export function renderCommandResults(results) {
  if (!results.length) {
    return '<div class="command-empty muted">没有匹配项</div>';
  }
  return results.map((result, index) => `
    <button class="command-row ${index === 0 ? 'is-active' : ''}" data-command-index="${index}">
      <h4>${escapeHtml(result.title)}</h4>
      <p>${escapeHtml(result.description)}</p>
    </button>
  `).join('');
}
'''

dashboard_js = r'''
import { groupBy, pick } from '../utils.js';
import { efficiencyTips } from '../data/tips.js';
import { renderMetrics, renderWeather, renderGithub, renderRecents, renderHotCategories, renderTips } from './renderers.js';
import { weatherCodeLabel } from '../api/weather.js';

export function updateDashboard(state) {
  document.getElementById('heroStats').innerHTML = renderMetrics(state);

  const weatherNode = document.getElementById('weatherContent');
  if (state.data.weather.result) {
    const enhancedWeather = {
      ...state.data.weather.result,
      cityName: state.data.weather.lastQuery || state.data.weather.city,
      summary: weatherCodeLabel(state.data.weather.result.current.weather_code)
    };
    weatherNode.classList.remove('skeleton-lines');
    weatherNode.innerHTML = renderWeather(enhancedWeather);
  }

  const githubNode = document.getElementById('githubContent');
  if (state.data.github.result) {
    githubNode.classList.remove('skeleton-lines');
    githubNode.innerHTML = renderGithub(state.data.github.result);
  }

  const allSites = [...state.data.builtinSites, ...state.data.customSites];
  const grouped = groupBy(allSites, item => item.category);
  const categorySummary = [...grouped.entries()]
    .map(([category, items]) => ({ category, count: items.length }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  document.getElementById('hotCategories').innerHTML = renderHotCategories(categorySummary);
  document.getElementById('recentSites').innerHTML = renderRecents(state.data.recents.slice(0, 6));
  document.getElementById('tipsBox').innerHTML = renderTips([
    pick(efficiencyTips),
    pick(efficiencyTips),
    pick(efficiencyTips)
  ].filter(Boolean));
}
'''

bookmarks_js = r'''
import { groupBy, sortByName, sortByNameDesc } from '../utils.js';
import { getAllSites } from '../state.js';
import { renderGroup, renderSiteCard } from './renderers.js';

function smartSort(items, state) {
  return [...items].sort((a, b) => {
    const pinDelta = Number(state.data.pinned.includes(b.id)) - Number(state.data.pinned.includes(a.id));
    if (pinDelta) return pinDelta;
    const favDelta = Number(state.data.favorites.includes(b.id)) - Number(state.data.favorites.includes(a.id));
    if (favDelta) return favDelta;
    const openDelta = (state.data.opens[b.id] || 0) - (state.data.opens[a.id] || 0);
    if (openDelta) return openDelta;
    return sortByName(a, b);
  });
}

export function filterSites(state) {
  const search = state.ui.search.trim().toLowerCase();
  const category = state.ui.category;
  const filter = state.ui.filter;
  const showOnlyHttps = state.ui.showOnlyHttps;

  let sites = getAllSites(state);

  if (showOnlyHttps) {
    sites = sites.filter(site => site.url.startsWith('https://'));
  }

  if (category !== 'all') {
    sites = sites.filter(site => site.category === category);
  }

  if (search) {
    sites = sites.filter(site => {
      const bucket = [site.name, site.description, site.category, site.tag, ...(site.keywords || [])].join(' ').toLowerCase();
      return bucket.includes(search);
    });
  }

  if (filter === 'builtin') sites = sites.filter(site => site.source === 'builtin');
  if (filter === 'custom') sites = sites.filter(site => site.source === 'custom');
  if (filter === 'pinned') sites = sites.filter(site => state.data.pinned.includes(site.id));
  if (filter === 'favorite') sites = sites.filter(site => state.data.favorites.includes(site.id));

  if (state.ui.sort === 'name-asc') sites = [...sites].sort(sortByName);
  if (state.ui.sort === 'name-desc') sites = [...sites].sort(sortByNameDesc);
  if (state.ui.sort === 'updated') sites = [...sites].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  if (state.ui.sort === 'opens') sites = [...sites].sort((a, b) => (state.data.opens[b.id] || 0) - (state.data.opens[a.id] || 0));
  if (state.ui.sort === 'smart') sites = smartSort(sites, state);

  return sites;
}

export function renderSitesView(state) {
  const groupsNode = document.getElementById('siteGroups');
  const favoritesGrid = document.getElementById('favoritesGrid');
  const recentGrid = document.getElementById('recentGrid');

  const filtered = filterSites(state);
  const grouped = groupBy(filtered, site => site.category);

  const groupsHtml = [...grouped.entries()].map(([category, sites], index) => {
    const icon = sites[0]?.icon || '🌐';
    const expanded = state.ui.expandMode === 'all' || (state.ui.expandMode === 'smart' && index < 3);
    return renderGroup({ category, icon }, sites, expanded, state);
  }).join('');

  groupsNode.innerHTML = groupsHtml || '<div class="glass widget-card">没有匹配到站点</div>';

  const favoriteSites = getAllSites(state).filter(site => state.data.favorites.includes(site.id));
  favoritesGrid.innerHTML = favoriteSites.length
    ? favoriteSites.map(site => renderSiteCard(site, state)).join('')
    : '<div class="glass widget-card">收藏夹还是空的</div>';

  const recentIds = state.data.recents.map(item => item.id);
  const recentSites = recentIds
    .map(id => getAllSites(state).find(site => site.id === id))
    .filter(Boolean);
  recentGrid.innerHTML = recentSites.length
    ? recentSites.map(site => renderSiteCard(site, state)).join('')
    : '<div class="glass widget-card">还没有最近访问记录</div>';
}

export function populateCategorySelect(state) {
  const select = document.getElementById('categorySelect');
  const categories = ['all', ...new Set(getAllSites(state).map(site => site.category))].sort((a, b) => a.localeCompare(b, 'zh-CN'));
  select.innerHTML = categories.map(category => `<option value="${category}">${category === 'all' ? '全部分类' : category}</option>`).join('');
  select.value = state.ui.category;
}
'''

commands_js = r'''
import { getAllSites } from '../state.js';
import { renderCommandResults } from './renderers.js';

export function buildCommands(state) {
  const staticCommands = [
    {
      key: 'goto dashboard',
      title: '切到总览',
      description: '打开 dashboard 视图',
      run: () => ({ type: 'view', value: 'dashboard' })
    },
    {
      key: 'goto sites',
      title: '切到网站库',
      description: '打开 sites 视图',
      run: () => ({ type: 'view', value: 'sites' })
    },
    {
      key: 'goto favorites',
      title: '切到收藏夹',
      description: '打开 favorites 视图',
      run: () => ({ type: 'view', value: 'favorites' })
    },
    {
      key: 'goto settings',
      title: '切到设置',
      description: '打开 settings 视图',
      run: () => ({ type: 'view', value: 'settings' })
    },
    {
      key: 'theme dark',
      title: '切换到 Dark 主题',
      description: '应用 dark 主题',
      run: () => ({ type: 'theme', value: 'dark' })
    },
    {
      key: 'theme light',
      title: '切换到 Light 主题',
      description: '应用 light 主题',
      run: () => ({ type: 'theme', value: 'light' })
    },
    {
      key: 'theme violet',
      title: '切换到 Violet 主题',
      description: '应用 violet 主题',
      run: () => ({ type: 'theme', value: 'violet' })
    },
    {
      key: 'theme forest',
      title: '切换到 Forest 主题',
      description: '应用 forest 主题',
      run: () => ({ type: 'theme', value: 'forest' })
    }
  ];

  const siteCommands = getAllSites(state).slice(0, 200).map(site => ({
    key: `open ${site.name}`.toLowerCase(),
    title: `打开 ${site.name}`,
    description: `${site.category} · ${site.url}`,
    run: () => ({ type: 'site', value: site.id })
  }));

  return [...staticCommands, ...siteCommands];
}

export function searchCommands(commands, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return commands.slice(0, 12);
  return commands.filter(command => `${command.key} ${command.title} ${command.description}`.toLowerCase().includes(normalized)).slice(0, 12);
}

export function renderCommands(resultsNode, results) {
  resultsNode.innerHTML = renderCommandResults(results);
}
'''

settings_js = r'''
export function syncSettingControls(state) {
  document.getElementById('defaultViewSelect').value = state.ui.defaultView;
  document.getElementById('expandModeSelect').value = state.ui.expandMode;
  document.getElementById('showOnlyHttpsInput').checked = Boolean(state.ui.showOnlyHttps);
}
'''

app_js = r'''
import { loadState, saveState, exportState, importState, clearAllStorage } from './storage.js';
import { defaultState, mergeState, getAllSites, recordOpen, isFavorite, isPinned } from './state.js';
import { uid, normalizeUrl, debounce, copyText } from './utils.js';
import { initNotifier, toast } from './modules/notify.js';
import { applyTheme, renderThemeGrid } from './modules/theme.js';
import { openDialog, closeDialog } from './modules/modal.js';
import { populateCategorySelect, renderSitesView, filterSites } from './modules/bookmarks.js';
import { updateDashboard } from './modules/dashboard.js';
import { syncSettingControls } from './modules/settings.js';
import { searchCity, getForecastByCoords, getCurrentLocation } from './api/weather.js';
import { getGithubProfile } from './api/github.js';
import { buildCommands, searchCommands, renderCommands } from './modules/commands.js';

let state = mergeState(defaultState, loadState(defaultState));
let editingSiteId = null;
let commandResults = [];

initNotifier();
boot();

function boot() {
  applyTheme(state.ui.theme);
  bindStaticEvents();
  syncControls();
  renderAll();
  hydrateRemotePanels();
}

function syncControls() {
  document.getElementById('globalSearchInput').value = state.ui.search;
  document.getElementById('sortSelect').value = state.ui.sort;
  populateCategorySelect(state);
  syncFilterChips();
  syncSettingControls(state);
  renderThemeGrid(document.getElementById('themeGrid'), state.themes, state.ui.theme, themeId => {
    state.ui.theme = themeId;
    persist();
    applyTheme(themeId);
    syncControls();
  });
}

function persist() {
  saveState(state);
}

function renderAll() {
  setView(state.ui.currentView);
  renderPageTitle();
  renderSitesView(state);
  updateDashboard(state);
  attachDynamicCardEvents();
  refreshCommandResults();
}

function renderPageTitle() {
  const titleMap = {
    dashboard: '总览',
    sites: '网站库',
    favorites: '收藏夹',
    recent: '最近打开',
    settings: '设置'
  };
  document.getElementById('pageTitle').textContent = titleMap[state.ui.currentView] || '总览';
}

function setView(view) {
  state.ui.currentView = view;
  document.querySelectorAll('.view-section, .dashboard-grid').forEach(node => node.classList.add('is-hidden'));
  document.querySelectorAll('.side-nav-item').forEach(node => node.classList.toggle('is-active', node.dataset.view === view));

  if (view === 'dashboard') document.getElementById('dashboardView').classList.remove('is-hidden');
  if (view === 'sites') document.getElementById('sitesView').classList.remove('is-hidden');
  if (view === 'favorites') document.getElementById('favoritesView').classList.remove('is-hidden');
  if (view === 'recent') document.getElementById('recentView').classList.remove('is-hidden');
  if (view === 'settings') document.getElementById('settingsView').classList.remove('is-hidden');
  persist();
}

function syncFilterChips() {
  document.querySelectorAll('.chip').forEach(button => {
    button.classList.toggle('is-active', button.dataset.filter === state.ui.filter);
  });
}

function bindStaticEvents() {
  document.querySelectorAll('.side-nav-item').forEach(button => {
    button.addEventListener('click', () => {
      setView(button.dataset.view);
      renderAll();
    });
  });

  document.getElementById('jumpSitesBtn').addEventListener('click', () => {
    setView('sites');
    renderAll();
  });

  document.getElementById('jumpSettingsBtn').addEventListener('click', () => {
    setView('settings');
    renderAll();
  });

  document.getElementById('globalSearchInput').addEventListener('input', debounce(event => {
    state.ui.search = event.target.value;
    persist();
    renderAll();
  }, 120));

  document.getElementById('categorySelect').addEventListener('change', event => {
    state.ui.category = event.target.value;
    persist();
    renderAll();
  });

  document.getElementById('sortSelect').addEventListener('change', event => {
    state.ui.sort = event.target.value;
    persist();
    renderAll();
  });

  document.querySelectorAll('.chip').forEach(button => {
    button.addEventListener('click', () => {
      state.ui.filter = button.dataset.filter;
      persist();
      syncFilterChips();
      renderAll();
    });
  });

  document.getElementById('addSiteBtn').addEventListener('click', () => openSiteDialog());
  document.getElementById('commandPaletteBtn').addEventListener('click', openCommandPalette);

  document.getElementById('collapseAllBtn').addEventListener('click', () => {
    document.querySelectorAll('.group-card details, .group-card').forEach(() => {});
    document.querySelectorAll('.group-card').forEach(group => {
      const details = group.tagName === 'DETAILS' ? group : group.querySelector('details');
      if (details) details.open = false;
    });
    document.querySelectorAll('.group-card').forEach(group => group.removeAttribute('open'));
    document.querySelectorAll('.group-card').forEach(group => group.open = false);
  });

  document.getElementById('expandAllBtn').addEventListener('click', () => {
    document.querySelectorAll('.group-card').forEach(group => group.open = true);
  });

  const siteDialog = document.getElementById('siteDialog');
  const siteFormDialog = document.getElementById('siteFormDialog');
  siteFormDialog.addEventListener('submit', event => {
    event.preventDefault();
    saveSiteFromDialog();
  });
  siteDialog.addEventListener('close', () => {
    siteFormDialog.reset();
    editingSiteId = null;
  });

  document.getElementById('exportStateBtn').addEventListener('click', () => {
    exportState(state);
    toast('已导出', '当前本地数据已导出为 JSON。');
  });

  document.getElementById('importStateInput').addEventListener('change', async event => {
    const file = event.target.files?.[0];
    if (!file) return;
    const payload = await importState(file);
    if (!payload) {
      toast('导入失败', '文件格式不正确。');
      return;
    }
    state = mergeState(defaultState, payload);
    persist();
    applyTheme(state.ui.theme);
    syncControls();
    renderAll();
    toast('导入成功', '状态已恢复。');
  });

  document.getElementById('resetAppBtn').addEventListener('click', () => {
    if (!confirm('确定要清空当前本地数据吗？')) return;
    clearAllStorage();
    state = structuredClone(defaultState);
    persist();
    applyTheme(state.ui.theme);
    syncControls();
    renderAll();
    toast('已重置', '本地数据已恢复默认值。');
  });

  document.getElementById('clearRecentBtn').addEventListener('click', () => {
    state.data.recents = [];
    persist();
    renderAll();
    toast('已清空', '最近访问记录已清空。');
  });

  document.getElementById('weatherSearchForm').addEventListener('submit', async event => {
    event.preventDefault();
    await loadWeatherByCity(document.getElementById('weatherCityInput').value.trim() || state.data.weather.city);
  });

  document.getElementById('refreshWeatherBtn').addEventListener('click', async () => {
    await loadWeatherByCity(state.data.weather.lastQuery || state.data.weather.city);
  });

  document.getElementById('weatherGeoBtn').addEventListener('click', async () => {
    await loadWeatherByGeo();
  });

  document.getElementById('githubSearchForm').addEventListener('submit', async event => {
    event.preventDefault();
    const username = document.getElementById('githubUserInput').value.trim() || state.data.github.username;
    await loadGithub(username);
  });

  document.getElementById('refreshGithubBtn').addEventListener('click', async () => {
    await loadGithub(state.data.github.username);
  });

  document.getElementById('defaultViewSelect').addEventListener('change', event => {
    state.ui.defaultView = event.target.value;
    persist();
    toast('设置已保存', '默认视图已更新。');
  });

  document.getElementById('expandModeSelect').addEventListener('change', event => {
    state.ui.expandMode = event.target.value;
    persist();
    renderAll();
  });

  document.getElementById('showOnlyHttpsInput').addEventListener('change', event => {
    state.ui.showOnlyHttps = event.target.checked;
    persist();
    renderAll();
  });

  const commandDialog = document.getElementById('commandDialog');
  const commandInput = document.getElementById('commandInput');
  commandInput.addEventListener('input', () => refreshCommandResults(commandInput.value));
  document.getElementById('commandResults').addEventListener('click', event => {
    const row = event.target.closest('[data-command-index]');
    if (!row) return;
    runCommandResult(Number(row.dataset.commandIndex));
  });

  window.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openCommandPalette();
      return;
    }
    if (event.key === '/') {
      const target = document.activeElement;
      if (target && ['INPUT', 'TEXTAREA'].includes(target.tagName)) return;
      event.preventDefault();
      document.getElementById('globalSearchInput').focus();
      return;
    }
    if (event.key === 'Escape') {
      closeDialog(document.getElementById('commandDialog'));
      closeDialog(document.getElementById('siteDialog'));
      return;
    }
    if (event.key.toLowerCase() === 'g') {
      window.__navSequence = 'g';
      window.setTimeout(() => { window.__navSequence = ''; }, 500);
      return;
    }
    if (window.__navSequence === 'g') {
      const next = event.key.toLowerCase();
      if (next === 'd') {
        setView('dashboard');
        renderAll();
      }
      if (next === 's') {
        setView('sites');
        renderAll();
      }
      window.__navSequence = '';
    }
  });
}

function openSiteDialog(site = null) {
  const dialog = document.getElementById('siteDialog');
  const form = document.getElementById('siteFormDialog');
  document.getElementById('siteDialogTitle').textContent = site ? '编辑站点' : '添加站点';
  form.name.value = site?.name || '';
  form.url.value = site?.url || '';
  form.category.value = site?.category || '';
  form.tag.value = site?.tag || '';
  form.description.value = site?.description || '';
  form.pinned.checked = site ? state.data.pinned.includes(site.id) : false;
  editingSiteId = site?.id || null;
  openDialog(dialog);
}

function saveSiteFromDialog() {
  const form = document.getElementById('siteFormDialog');
  const payload = {
    id: editingSiteId || uid('custom-site'),
    name: form.name.value.trim(),
    url: normalizeUrl(form.url.value.trim()),
    category: form.category.value.trim() || '自定义',
    icon: '⭐',
    tag: form.tag.value.trim() || '自定义',
    description: form.description.value.trim() || '自定义站点',
    keywords: [form.category.value.trim(), form.tag.value.trim(), form.name.value.trim()].filter(Boolean),
    updatedAt: new Date().toISOString(),
    source: 'custom'
  };

  if (!payload.name || !payload.url) {
    toast('保存失败', '名称和网址不能为空。');
    return;
  }

  if (editingSiteId) {
    const index = state.data.customSites.findIndex(site => site.id === editingSiteId);
    if (index >= 0) state.data.customSites[index] = payload;
  } else {
    state.data.customSites.unshift(payload);
  }

  if (form.pinned.checked && !state.data.pinned.includes(payload.id)) {
    state.data.pinned.unshift(payload.id);
  }

  persist();
  closeDialog(document.getElementById('siteDialog'));
  syncControls();
  renderAll();
  toast('保存成功', `${payload.name} 已加入导航。`);
}

function attachDynamicCardEvents() {
  document.querySelectorAll('.site-card').forEach(card => {
    const id = card.dataset.siteId;
    const site = getAllSites(state).find(item => item.id === id);
    if (!site) return;
    card.querySelectorAll('.site-action').forEach(button => {
      button.addEventListener('click', async () => {
        const kind = button.dataset.kind;
        if (kind === 'open') {
          recordOpen(state, site);
          persist();
          window.open(site.url, '_blank', 'noopener,noreferrer');
          renderAll();
          toast('已打开', site.name);
        }
        if (kind === 'favorite') {
          toggleFavorite(site.id);
        }
        if (kind === 'pin') {
          togglePin(site.id);
        }
        if (kind === 'copy') {
          await copyText(site.url);
          toast('已复制', site.url);
        }
        if (kind === 'delete') {
          deleteCustomSite(site.id);
        }
      });
    });

    card.addEventListener('dblclick', () => {
      if (site.source === 'custom') openSiteDialog(site);
    });
  });
}

function toggleFavorite(id) {
  if (state.data.favorites.includes(id)) {
    state.data.favorites = state.data.favorites.filter(item => item !== id);
  } else {
    state.data.favorites.unshift(id);
  }
  persist();
  renderAll();
}

function togglePin(id) {
  if (state.data.pinned.includes(id)) {
    state.data.pinned = state.data.pinned.filter(item => item !== id);
  } else {
    state.data.pinned.unshift(id);
  }
  persist();
  renderAll();
}

function deleteCustomSite(id) {
  const target = state.data.customSites.find(site => site.id === id);
  if (!target) return;
  if (!confirm(`确定删除 ${target.name} 吗？`)) return;
  state.data.customSites = state.data.customSites.filter(site => site.id !== id);
  state.data.favorites = state.data.favorites.filter(item => item !== id);
  state.data.pinned = state.data.pinned.filter(item => item !== id);
  state.data.recents = state.data.recents.filter(item => item.id !== id);
  persist();
  syncControls();
  renderAll();
  toast('已删除', target.name);
}

async function hydrateRemotePanels() {
  document.getElementById('weatherCityInput').value = state.data.weather.city;
  document.getElementById('githubUserInput').value = state.data.github.username;

  if (state.data.weather.result) {
    updateDashboard(state);
  } else {
    await loadWeatherByCity(state.data.weather.city);
  }

  if (state.data.github.result) {
    updateDashboard(state);
  } else {
    await loadGithub(state.data.github.username);
  }
}

async function loadWeatherByCity(city) {
  try {
    document.getElementById('weatherContent').classList.add('skeleton-lines');
    const geo = await searchCity(city);
    const location = geo.results?.[0];
    if (!location) throw new Error('没找到这个城市');
    const forecast = await getForecastByCoords(location.latitude, location.longitude);
    state.data.weather.city = city;
    state.data.weather.lastQuery = `${location.name}${location.country ? `, ${location.country}` : ''}`;
    state.data.weather.result = forecast;
    state.data.weather.lastUpdated = new Date().toISOString();
    persist();
    renderAll();
    toast('天气已更新', state.data.weather.lastQuery);
  } catch (error) {
    toast('天气加载失败', error.message || '未知错误');
  } finally {
    document.getElementById('weatherContent').classList.remove('skeleton-lines');
  }
}

async function loadWeatherByGeo() {
  try {
    const coords = await getCurrentLocation();
    document.getElementById('weatherContent').classList.add('skeleton-lines');
    const forecast = await getForecastByCoords(coords.latitude, coords.longitude);
    state.data.weather.lastQuery = '当前位置';
    state.data.weather.result = forecast;
    state.data.weather.lastUpdated = new Date().toISOString();
    persist();
    renderAll();
    toast('定位成功', '已根据当前位置刷新天气。');
  } catch (error) {
    toast('定位失败', error.message || '请检查浏览器权限');
  } finally {
    document.getElementById('weatherContent').classList.remove('skeleton-lines');
  }
}

async function loadGithub(username) {
  try {
    document.getElementById('githubContent').classList.add('skeleton-lines');
    const result = await getGithubProfile(username);
    state.data.github.username = username;
    state.data.github.result = result;
    state.data.github.lastUpdated = new Date().toISOString();
    persist();
    renderAll();
    toast('GitHub 已更新', `当前用户: ${username}`);
  } catch (error) {
    toast('GitHub 加载失败', error.message || '未知错误');
  } finally {
    document.getElementById('githubContent').classList.remove('skeleton-lines');
  }
}

function openCommandPalette() {
  const dialog = document.getElementById('commandDialog');
  openDialog(dialog);
  document.getElementById('commandInput').value = '';
  refreshCommandResults('');
  document.getElementById('commandInput').focus();
}

function refreshCommandResults(query = '') {
  const commands = buildCommands(state);
  commandResults = searchCommands(commands, query);
  renderCommands(document.getElementById('commandResults'), commandResults);
}

function runCommandResult(index) {
  const command = commandResults[index];
  if (!command) return;
  const action = command.run();
  if (action.type === 'view') {
    setView(action.value);
    renderAll();
  }
  if (action.type === 'theme') {
    state.ui.theme = action.value;
    persist();
    applyTheme(action.value);
    syncControls();
    renderAll();
  }
  if (action.type === 'site') {
    const site = getAllSites(state).find(item => item.id === action.value);
    if (site) {
      recordOpen(state, site);
      persist();
      window.open(site.url, '_blank', 'noopener,noreferrer');
      renderAll();
    }
  }
  closeDialog(document.getElementById('commandDialog'));
}
'''

readme_md = r'''
# Navigator Pro

一个多文件、纯静态的个人导航站项目。

## 特性

- 多视图布局：总览、网站库、收藏夹、最近打开、设置
- 原生 ES Modules 架构
- 大型站点库，适合搜索、过滤、排序、置顶、收藏测试
- 本地持久化，使用 `localStorage`
- 导入 / 导出 JSON 备份
- 命令面板与快捷键
- Open-Meteo 天气面板
- GitHub 用户资料面板
- 多主题切换

## 目录结构

```text
personal-nav-pro/
  index.html
  README.md
  assets/
    css/
      reset.css
      variables.css
      base.css
      layout.css
      components.css
      animations.css
      utilities.css
    js/
      app.js
      dom.js
      state.js
      storage.js
      utils.js
      api/
        weather.js
        github.js
      data/
        sites.js
        tips.js
      modules/
        notify.js
        modal.js
        theme.js
        renderers.js
        dashboard.js
        bookmarks.js
        commands.js
        settings.js
```

## 本地运行

直接双击 `index.html` 即可。

如果你想测试地理定位与更稳定的模块加载，建议使用本地静态服务器：

```bash
python -m http.server 8080
```

然后访问：

```text
http://localhost:8080
```

## 部署

上传整个目录到 GitHub Pages、Cloudflare Pages、Netlify 或任意静态托管服务即可。

## 定制

- 修改 `assets/js/data/sites.js` 可替换默认站点库
- 修改 `assets/css/variables.css` 可调整主题配色
- 修改 `assets/js/api/` 可接入更多公开 API
'''

files = {
    root/'index.html': index_html,
    css/'reset.css': reset_css,
    css/'variables.css': variables_css,
    css/'base.css': base_css,
    css/'layout.css': layout_css,
    css/'components.css': components_css,
    css/'animations.css': animations_css,
    css/'utilities.css': utilities_css,
    js/'utils.js': utils_js,
    js/'storage.js': storage_js,
    js/'state.js': state_js,
    js/'dom.js': dom_js,
    api/'weather.js': weather_js,
    api/'github.js': github_js,
    data/'tips.js': tips_js,
    data/'sites.js': data_sites_js,
    modules/'notify.js': notify_js,
    modules/'modal.js': modal_js,
    modules/'theme.js': theme_js,
    modules/'renderers.js': renderers_js,
    modules/'dashboard.js': dashboard_js,
    modules/'bookmarks.js': bookmarks_js,
    modules/'commands.js': commands_js,
    modules/'settings.js': settings_js,
    js/'app.js': app_js,
    root/'README.md': readme_md,
}

for path, content in files.items():
    w(path, content)

print('generated', len(files), 'files')
