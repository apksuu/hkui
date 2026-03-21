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
