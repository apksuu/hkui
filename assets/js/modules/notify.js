let stack;

export function initNotifier() {
  stack = document.getElementById('toastStack');
}

export function toast(title, message = '', timeout = 2600) {
  if (!stack) return;
  const node = document.createElement('div');
  node.className = 'toast';
  node.innerHTML = `<strong>${title}</strong><div>${message}</div>`;
  stack.append(node);
  window.setTimeout(() => {
    node.remove();
  }, timeout);
}
