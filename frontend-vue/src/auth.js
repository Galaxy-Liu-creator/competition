import { reactive } from 'vue'
import request from './api/request'
import { applyTheme, storedTheme, themeMode } from './theme'

// 登录态模块:token/user 持久化 localStorage,后端不可用时回退演示账号
const TOKEN_KEY = 'qa-token'
const USER_KEY = 'qa-user'

export const DEFAULT_PREFERENCES = {
  theme: 'dark',
  sidebarCollapsed: false,
  notifyRisk: true,
  notifyDeviceOffline: true,
  notifyApproval: false,
  landingPage: '/workbench',
}

const DEMO_USER = {
  id: 0,
  username: 'admin',
  name: '安全管理员',
  role: '系统管理员',
  email: 'admin@qingan.com',
  avatar_text: '安',
  avatar: '',
  last_login_at: '',
  last_login_ip: '',
  preferences: { ...DEFAULT_PREFERENCES },
}

function readJson(key) {
  try { return JSON.parse(localStorage.getItem(key)) } catch { return null }
}

export const auth = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: readJson(USER_KEY),
})

function persist() {
  if (auth.token) localStorage.setItem(TOKEN_KEY, auth.token)
  else localStorage.removeItem(TOKEN_KEY)
  if (auth.user) localStorage.setItem(USER_KEY, JSON.stringify(auth.user))
  else localStorage.removeItem(USER_KEY)
}

export function isLoggedIn() {
  return Boolean(auth.token)
}

export function preferences() {
  return { ...DEFAULT_PREFERENCES, ...(auth.user?.preferences || {}) }
}

// 无头像图片时的文字回退:头像字 → 姓名首字 → 账户名首字
export function avatarFallback(user) {
  return user?.avatar_text || user?.name?.[0] || user?.username?.[0] || '安'
}

// 登录/注册后的主题策略:优先沿用本机上一次使用的日间/夜间模式(每次登录与上次保持一致),
// 仅当本机从未选择过主题时才采用账号偏好;随后把生效模式回写账号,保证设置页与后端记录一致。
// 回写走 updateMe(携带 Authorization),因此只在 token 已落盘后调用(persist 之后)。
function syncThemeWithAccount() {
  const mode = storedTheme() || auth.user?.preferences?.theme || themeMode()
  if (mode !== themeMode()) applyTheme(mode)
  if (auth.user && auth.user.preferences?.theme !== mode && localStorage.getItem(TOKEN_KEY)) {
    updateMe({ preferences: { ...preferences(), theme: mode } }).catch(() => {})
  }
}

export async function login(username, password, { remember = true } = {}) {
  try {
    const data = await request.post('/api/auth/login', { username, password })
    auth.token = data.token
    auth.user = data.user
  } catch (error) {
    // 网络层失败(后端未启动)时回退演示账号;业务失败(密码错)原样抛出
    if (error.response) throw error
    if (username !== 'admin' || password !== 'admin123') {
      const err = new Error('账号或密码错误')
      err.isBiz = true
      throw err
    }
    auth.user = {
      ...DEMO_USER,
      last_login_at: new Date().toLocaleString('zh-CN'),
      preferences: { ...DEFAULT_PREFERENCES, theme: themeMode() },
    }
    auth.token = 'demo-token'
  }
  if (remember) persist()
  syncThemeWithAccount()
  return auth.user
}

export async function register({ username, password, name }) {
  // 把登录页当前选择的主题作为新账号的初始偏好
  const data = await request.post('/api/auth/register', {
    username,
    password,
    name,
    preferences: { ...DEFAULT_PREFERENCES, theme: themeMode() },
  })
  auth.token = data.token
  auth.user = data.user
  persist()
  syncThemeWithAccount()
  return auth.user
}

export function logout() {
  auth.token = ''
  auth.user = null
  persist()
}

export async function loadMe() {
  try {
    auth.user = await request.get('/api/auth/me')
    persist()
  } catch { /* 后端不可用时沿用本地缓存 */ }
  return auth.user
}

export async function updateMe(payload) {
  try {
    auth.user = await request.put('/api/auth/me', payload)
  } catch (error) {
    if (error.response) throw error
    // 演示模式:仅更新本地
    auth.user = {
      ...auth.user,
      ...payload,
      preferences: { ...preferences(), ...(payload.preferences || {}) },
    }
  }
  persist()
  return auth.user
}

export async function savePreferences(patch) {
  return updateMe({ preferences: { ...preferences(), ...patch } })
}

export async function changePassword(oldPassword, newPassword) {
  return request.put('/api/auth/password', {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
