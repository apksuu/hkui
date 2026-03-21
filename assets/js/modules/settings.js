export function syncSettingControls(state) {
  document.getElementById('defaultViewSelect').value = state.ui.defaultView;
  document.getElementById('expandModeSelect').value = state.ui.expandMode;
  document.getElementById('showOnlyHttpsInput').checked = Boolean(state.ui.showOnlyHttps);
}
