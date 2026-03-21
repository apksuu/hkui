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
