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
  const fields = form.elements;
  document.getElementById('siteDialogTitle').textContent = site ? '编辑站点' : '添加站点';
  fields.namedItem('name').value = site?.name || '';
  fields.namedItem('url').value = site?.url || '';
  fields.namedItem('category').value = site?.category || '';
  fields.namedItem('tag').value = site?.tag || '';
  fields.namedItem('description').value = site?.description || '';
  fields.namedItem('pinned').checked = site ? state.data.pinned.includes(site.id) : false;
  editingSiteId = site?.id || null;
  openDialog(dialog);
}

function saveSiteFromDialog() {
  const form = document.getElementById('siteFormDialog');
  const fields = form.elements;
  const nameField = fields.namedItem('name');
  const urlField = fields.namedItem('url');
  const categoryField = fields.namedItem('category');
  const tagField = fields.namedItem('tag');
  const descriptionField = fields.namedItem('description');
  const pinnedField = fields.namedItem('pinned');

  const payload = {
    id: editingSiteId || uid('custom-site'),
    name: nameField.value.trim(),
    url: normalizeUrl(urlField.value.trim()),
    category: categoryField.value.trim() || '自定义',
    icon: '⭐',
    tag: tagField.value.trim() || '自定义',
    description: descriptionField.value.trim() || '自定义站点',
    keywords: [categoryField.value.trim(), tagField.value.trim(), nameField.value.trim()].filter(Boolean),
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

  if (pinnedField.checked && !state.data.pinned.includes(payload.id)) {
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
