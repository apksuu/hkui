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
