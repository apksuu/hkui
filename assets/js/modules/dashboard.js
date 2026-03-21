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
