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
