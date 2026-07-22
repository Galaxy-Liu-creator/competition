// 主题模块:dark / light / auto(跟随系统),写入 <html data-theme> 并联动 Element Plus dark class
const THEME_KEY = 'qa-theme'
const media = window.matchMedia('(prefers-color-scheme: dark)')

let currentMode = localStorage.getItem(THEME_KEY) || 'dark'

function resolved(mode) {
  if (mode === 'auto') return media.matches ? 'dark' : 'light'
  return mode
}

export function themeMode() {
  return currentMode
}

export function applyTheme(mode = currentMode) {
  currentMode = mode
  localStorage.setItem(THEME_KEY, mode)
  const actual = resolved(mode)
  const el = document.documentElement
  el.dataset.theme = actual
  el.classList.toggle('dark', actual === 'dark')
  return actual
}

export function initTheme() {
  applyTheme(currentMode)
  media.addEventListener('change', () => {
    if (currentMode === 'auto') applyTheme('auto')
  })
}
