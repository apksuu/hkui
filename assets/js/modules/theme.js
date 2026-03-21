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
