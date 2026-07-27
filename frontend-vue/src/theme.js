// 主题模块:dark / light / auto(跟随系统),写入 <html data-theme> 并联动 Element Plus dark class
import { ref } from 'vue'

const THEME_KEY = 'qa-theme'
const media = window.matchMedia('(prefers-color-scheme: dark)')

let currentMode = localStorage.getItem(THEME_KEY) || 'dark'

function resolved(mode) {
  if (mode === 'auto') return media.matches ? 'dark' : 'light'
  return mode
}

// 当前实际生效的主题('dark' | 'light'),供图表/地图等命令式渲染的组件响应切换
export const activeTheme = ref(resolved(currentMode))

// 当前主题偏好('dark' | 'light' | 'auto'),供设置页等界面反映用户选择
export const themeModeRef = ref(currentMode)

export function themeMode() {
  return currentMode
}

// 本机记录的主题选择;null 表示该浏览器从未选过主题(登录时将采用账号偏好)
export function storedTheme() {
  return localStorage.getItem(THEME_KEY)
}

export function applyTheme(mode = currentMode, { save = true } = {}) {
  currentMode = mode
  if (save) localStorage.setItem(THEME_KEY, mode)
  const actual = resolved(mode)
  const el = document.documentElement
  el.dataset.theme = actual
  el.classList.toggle('dark', actual === 'dark')
  activeTheme.value = actual
  themeModeRef.value = mode
  return actual
}

export function initTheme() {
  // 启动时仅应用、不落盘:qa-theme 只在真正发生主题选择/切换时写入,
  // 用于区分"本机从未选过主题"(登录采用账号偏好)与"沿用上次选择"(登录保持上次模式)
  applyTheme(currentMode, { save: false })
  media.addEventListener('change', () => {
    if (currentMode === 'auto') applyTheme('auto', { save: false })
  })
}
