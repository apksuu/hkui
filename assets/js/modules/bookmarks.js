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
