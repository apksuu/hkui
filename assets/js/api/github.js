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
