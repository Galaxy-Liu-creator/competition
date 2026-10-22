<template>
  <div class="split">
    <!-- ============ 左侧品牌区 ============ -->
    <section class="hero">
      <div class="brand">
        <div class="logo"><img src="/logo.svg" alt="油擎智安 Logo" /></div>
        <div>
          <strong>油擎智安</strong>
          <span>吊装安全运营平台 · YOUQING SMART SAFETY</span>
        </div>
      </div>

      <div class="slogan">
        <span class="kicker">◈ 智能吊装 · 安全护航</span>
        <h1>重新定义<em>吊装安全</em>的<br />技术边界</h1>
        <p class="sub">不止看见现场，更能感知运动、距离与三维空间风险。</p>
      </div>

      <div class="feats">
        <div class="feat">
          <i aria-hidden="true">
            <!-- 雷达扫描 -->
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
              <circle cx="12" cy="12" r="8.5" />
              <path d="M12 7.5a4.5 4.5 0 0 1 4.5 4.5" />
              <path d="M12 12 17.6 6.4" />
              <circle cx="8.9" cy="9.3" r="1.2" fill="currentColor" stroke="none" />
              <circle cx="12" cy="12" r=".9" fill="currentColor" stroke="none" />
              <path d="M12 3.5v1.4M20.5 12h-1.4M12 20.5v-1.4M3.5 12h1.4" opacity=".55" />
            </svg>
          </i>雷达感知 · 毫米级运动与距离测算
        </div>
        <div class="feat">
          <i aria-hidden="true">
            <!-- 三维空间建模 -->
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 3 20 7.5v9L12 21l-8-4.5v-9L12 3Z" />
              <path d="M12 12 20 7.5M12 12 4 7.5M12 12v9" />
              <circle cx="12" cy="7.6" r="1.1" fill="currentColor" stroke="none" />
            </svg>
          </i>三维空间风险建模 · 电子围栏预警
        </div>
        <div class="feat">
          <i aria-hidden="true">
            <!-- 数据闭环 -->
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M21 3v5h-5" />
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
              <path d="M8 16H3v5" />
              <path d="M9.3 14.2v-2.1M12 14.2V9.8M14.7 14.2v-3.2" stroke-width="1.7" />
            </svg>
          </i>风险事件全流程闭环 · 数据可视化
        </div>
      </div>
    </section>

    <!-- ============ 右侧表单区 ============ -->
    <section class="pane">
      <div class="pane-top">
        <div class="tabs">
          <button type="button" :class="{ on: tab === 'login' }" @click="tab = 'login'">
            登录<small>Sign In</small>
          </button>
          <button type="button" :class="{ on: tab === 'register' }" @click="tab = 'register'">
            注册<small>Create</small>
          </button>
        </div>
        <button
          type="button"
          class="theme-btn"
          :aria-label="isDark ? '切换日间模式' : '切换夜间模式'"
          :title="isDark ? '切换日间模式' : '切换夜间模式'"
          @click="toggleTheme"
        >
          <el-icon><Sunny v-if="isDark" /><Moon v-else /></el-icon>
        </button>
      </div>

      <form class="form-wrap" @submit.prevent="submit">
        <template v-if="tab === 'login'">
          <h2>欢迎回来</h2>
          <p class="hint">输入您的账号信息，继续守护每一次安全吊装。</p>

          <div class="field">
            <label for="login-username">账号 / 手机号</label>
            <div class="control">
              <el-icon><User /></el-icon>
              <input id="login-username" v-model.trim="form.username" placeholder="请输入您的账号信息" autocomplete="username" />
            </div>
          </div>
          <div class="field">
            <label for="login-password">登录密码</label>
            <div class="control">
              <el-icon><Lock /></el-icon>
              <input
                id="login-password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入您的密码"
                autocomplete="current-password"
              />
              <el-icon class="eye" @click="showPassword = !showPassword"><View v-if="showPassword" /><Hide v-else /></el-icon>
            </div>
          </div>

          <div class="row">
            <label class="remember"><input v-model="remember" type="checkbox" />记住登录状态</label>
            <a href="#" @click.prevent="forgot">忘记密码？</a>
          </div>

          <button class="submit" type="submit" :disabled="loading">
            {{ loading ? '登录中…' : '立即登录 →' }}
          </button>
        </template>

        <template v-else>
          <h2>创建账号</h2>
          <p class="hint">注册专属账号，开始体验智能吊装安全管理。</p>

          <div class="field">
            <label for="reg-username">账号</label>
            <div class="control">
              <el-icon><User /></el-icon>
              <input
                id="reg-username"
                v-model.trim="regForm.username"
                placeholder="3-20 位字母、数字或下划线"
                autocomplete="username"
              />
            </div>
          </div>
          <div class="field">
            <label for="reg-name">姓名<em class="opt">选填，默认同账号</em></label>
            <div class="control">
              <el-icon><Postcard /></el-icon>
              <input id="reg-name" v-model.trim="regForm.name" maxlength="16" placeholder="用于系统内展示与头像首字" />
            </div>
          </div>
          <div class="field">
            <label for="reg-password">登录密码</label>
            <div class="control">
              <el-icon><Lock /></el-icon>
              <input
                id="reg-password"
                v-model="regForm.password"
                :type="showRegPassword ? 'text' : 'password'"
                placeholder="至少 6 位"
                autocomplete="new-password"
              />
              <el-icon class="eye" @click="showRegPassword = !showRegPassword"><View v-if="showRegPassword" /><Hide v-else /></el-icon>
            </div>
          </div>
          <div class="field">
            <label for="reg-confirm">确认密码</label>
            <div class="control">
              <el-icon><Lock /></el-icon>
              <input
                id="reg-confirm"
                v-model="regForm.confirm"
                type="password"
                placeholder="再次输入密码"
                autocomplete="new-password"
              />
            </div>
          </div>

          <button class="submit" type="submit" :disabled="loading">
            {{ loading ? '注册中…' : '注册并登录 →' }}
          </button>
        </template>
      </form>

      <p class="foot">
        <template v-if="tab === 'login'">还没有账号？<a href="#" @click.prevent="tab = 'register'">立即注册</a></template>
        <template v-else>已有账号？<a href="#" @click.prevent="tab = 'login'">立即登录</a></template>
      </p>
      <p class="copyright">© 2026 油擎智安 · 吊装安全运营平台</p>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide, Sunny, Moon, Postcard } from '@element-plus/icons-vue'
import { login, preferences, register } from '@/auth'
import { activeTheme, applyTheme } from '@/theme'

const router = useRouter()
const route = useRoute()

const tab = ref('login')
const showPassword = ref(false)
const showRegPassword = ref(false)
const remember = ref(true)
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', name: '', password: '', confirm: '' })
const isDark = computed(() => activeTheme.value === 'dark')

function toggleTheme() {
  applyTheme(isDark.value ? 'light' : 'dark')
}

function forgot() {
  ElMessage.info('请联系系统管理员重置密码')
}

function enter() {
  router.replace(route.query.redirect || preferences().landingPage || '/workbench')
}

async function submit() {
  if (tab.value === 'register') return doRegister()
  if (!form.username || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    await login(form.username, form.password, { remember: remember.value })
    ElMessage.success('登录成功，欢迎回来')
    enter()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '登录失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  if (!/^[A-Za-z0-9_]{3,20}$/.test(regForm.username)) {
    ElMessage.warning('账号需为 3-20 位字母、数字或下划线')
    return
  }
  if (regForm.password.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  if (regForm.password !== regForm.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await register({ username: regForm.username, password: regForm.password, name: regForm.name })
    ElMessage.success('注册成功，已自动登录')
    enter()
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data?.message || '注册失败，请稍后再试')
    } else {
      ElMessage.error('后端服务未启动，暂无法注册，请稍后再试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.split { display: grid; grid-template-columns: 55% 45%; height: 100vh; }

/* ============ 左侧品牌区 ============ */
.hero {
  position: relative; overflow: hidden;
  display: flex; flex-direction: column; justify-content: space-between;
  padding: 44px 56px 48px;
  background: url('/login-bg.png') center / cover no-repeat;
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(115deg, rgba(4, 10, 22, .86) 0%, rgba(6, 13, 26, .55) 58%, rgba(6, 13, 26, .25) 100%);
}
.hero::after {
  content: ''; position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(34, 211, 238, .05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34, 211, 238, .04) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: linear-gradient(to right, black, transparent 75%);
}
.hero > * { position: relative; z-index: 1; }

.brand { display: flex; align-items: center; gap: 12px; }
.brand .logo {
  width: 46px; height: 46px; display: grid; place-items: center;
  background: rgba(16, 39, 66, .8); border: 1px solid var(--qa-cyan);
  border-radius: 10px;
  box-shadow: 0 0 18px rgba(34, 211, 238, .35);
}
.brand .logo img { width: 34px; height: 34px; object-fit: contain; }
.brand strong { display: block; font-size: 21px; letter-spacing: 5px; color: #fff; }
.brand span { display: block; margin-top: 2px; font-size: 11px; letter-spacing: 2px; color: rgba(139, 163, 194, .95); }

.slogan { max-width: 560px; }
.slogan .kicker {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 12px; letter-spacing: 3px; color: var(--qa-cyan);
  border: 1px solid rgba(34, 211, 238, .45); background: rgba(34, 211, 238, .1);
  padding: 5px 14px; border-radius: 999px; margin-bottom: 22px;
}
.slogan h1 {
  margin: 0;
  font-family: 'Noto Serif SC', serif; font-weight: 900;
  font-size: 40px; line-height: 1.35; color: #fff;
  text-shadow: 0 2px 24px rgba(0, 0, 0, .5);
}
.slogan h1 em { font-style: normal; color: var(--qa-cyan); }
.slogan p.sub { margin: 18px 0 0; font-size: 16px; line-height: 1.9; color: rgba(226, 238, 252, .85); }

.feats { display: grid; gap: 14px; max-width: 480px; }
.feat {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 16px; border-radius: 10px;
  background: rgba(10, 21, 38, .55); border: 1px solid rgba(44, 82, 124, .55);
  backdrop-filter: blur(6px); font-size: 14.5px; color: #dbe8f7;
}
.feat i {
  display: grid; place-items: center; width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 9px; font-style: normal; color: var(--qa-cyan);
  background: linear-gradient(160deg, rgba(34, 211, 238, .16), rgba(59, 130, 246, .1));
  border: 1px solid rgba(34, 211, 238, .45);
  box-shadow: inset 0 0 12px rgba(34, 211, 238, .12);
}
.feat i svg { width: 19px; height: 19px; filter: drop-shadow(0 0 5px rgba(34, 211, 238, .5)); }

/* ============ 右侧表单区 ============ */
.pane {
  display: flex; flex-direction: column;
  padding: 34px 64px 30px; background: var(--qa-panel);
  border-left: 1px solid var(--qa-border); overflow-y: auto;
  transition: background .3s;
}
.pane-top { display: flex; align-items: center; justify-content: space-between; }
.tabs {
  display: flex; padding: 4px; border-radius: 999px;
  background: var(--qa-panel-2); border: 1px solid var(--qa-border);
}
.tabs button {
  border: 0; cursor: pointer; border-radius: 999px;
  padding: 9px 26px; font-family: inherit; font-size: 14px;
  background: transparent; color: var(--qa-text-2);
}
.tabs button small { display: block; font-size: 10px; opacity: .7; font-style: italic; }
.tabs button.on {
  background: linear-gradient(135deg, var(--qa-blue), #2563eb);
  color: #fff; box-shadow: 0 4px 14px rgba(59, 130, 246, .4);
}
/* 与主页面顶栏 .icon-btn 一致的主题切换按钮风格 */
.theme-btn {
  position: relative; display: grid; place-items: center; width: 34px; height: 34px;
  border: 0; background: transparent; color: var(--qa-text-2); cursor: pointer;
  border-radius: 6px; font-size: 17px;
}
.theme-btn:hover { background: var(--qa-panel-3); color: var(--qa-text); }

.form-wrap { margin: auto 0; padding: 44px 0 24px; }
.form-wrap h2 { margin: 0; font-size: 32px; font-weight: 900; letter-spacing: 1px; color: var(--qa-text); }
.form-wrap .hint { margin: 10px 0 0; font-size: 14px; color: var(--qa-text-2); }

.field { margin-top: 26px; }
.field label { display: block; font-size: 13.5px; font-weight: 500; margin-bottom: 9px; color: var(--qa-text); }
.field label .opt { font-style: normal; font-weight: 400; margin-left: 8px; font-size: 11.5px; color: var(--qa-text-muted); }
.control {
  display: flex; align-items: center; gap: 10px;
  border: 1px solid var(--qa-border); background: var(--qa-bg-2);
  border-radius: 10px; padding: 0 16px; height: 50px;
  color: var(--qa-text-muted);
  transition: border-color .2s, box-shadow .2s;
}
.control:focus-within { border-color: var(--qa-blue); box-shadow: 0 0 0 3px rgba(59, 130, 246, .18); }
.control input {
  flex: 1; border: 0; outline: 0; background: transparent;
  font-family: inherit; font-size: 14.5px; color: var(--qa-text);
}
.control input::placeholder { color: var(--qa-text-muted); }
.control .eye { cursor: pointer; color: var(--qa-text-muted); }
.control .eye:hover { color: var(--qa-text-2); }

.row { display: flex; align-items: center; justify-content: space-between; margin-top: 18px; font-size: 13.5px; }
.remember { display: flex; align-items: center; gap: 8px; color: var(--qa-text-2); cursor: pointer; }
.remember input { accent-color: var(--qa-blue); width: 15px; height: 15px; }
.row a { color: var(--qa-blue); text-decoration: none; }

.submit {
  width: 100%; margin-top: 28px; height: 52px; cursor: pointer;
  border: 0; border-radius: 12px; font-family: inherit;
  font-size: 16.5px; font-weight: 700; letter-spacing: 6px; color: #fff;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 55%, #1d4ed8 100%);
  box-shadow: 0 8px 22px rgba(37, 99, 235, .38);
  transition: transform .15s, box-shadow .15s;
}
.submit:hover { transform: translateY(-1px); box-shadow: 0 10px 26px rgba(37, 99, 235, .5); }
.submit:disabled { opacity: .7; cursor: not-allowed; transform: none; }

.foot { margin: 0; text-align: center; font-size: 13.5px; color: var(--qa-text-2); }
.foot a { color: var(--qa-blue); text-decoration: none; font-weight: 600; }
.copyright { margin: 14px 0 0; text-align: center; font-size: 11.5px; color: var(--qa-text-muted); }

@media (max-width: 900px) {
  .split { grid-template-columns: 1fr; }
  .hero { display: none; }
  .pane { padding: 34px 28px 30px; }
}
</style>
