<template>
  <div class="shell" :class="{ collapsed }">
    <!-- ============ 侧边栏 ============ -->
    <aside>
      <div class="brand">
        <img src="/logo-512.png" alt="擎安智吊 Logo" />
        <div v-if="!collapsed">
          <strong>擎安智吊</strong>
          <span>吊装安全运营平台</span>
        </div>
      </div>

      <el-menu
        class="side-menu"
        :default-active="route.path"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        unique-opened
      >
        <template v-for="item in menu" :key="item.path || item.title">
          <el-sub-menu v-if="item.children" :index="item.title">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <el-menu-item v-for="child in item.children" :key="child.path" :index="child.path">
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>

      <div class="user-box">
        <span class="avatar">
          <img v-if="user?.avatar" :src="user.avatar" alt="头像" />
          <template v-else>{{ avatarChar }}</template>
        </span>
        <div v-if="!collapsed">
          <strong>{{ user?.name || '安全管理员' }}</strong>
          <span>{{ user?.role || '系统管理员' }}</span>
        </div>
        <el-icon v-if="!collapsed" class="logout" title="退出登录" @click="onLogout"><SwitchButton /></el-icon>
      </div>
    </aside>

    <!-- ============ 主工作区 ============ -->
    <section class="work">
      <header>
        <div class="heading">
          <button type="button" class="fold" :aria-label="collapsed ? '展开菜单' : '收起菜单'" @click="collapsed = !collapsed">
            <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </button>
          <nav class="crumbs" aria-label="面包屑">
            <template v-if="crumbs.length">
              <span v-for="(c, i) in crumbs" :key="c" :class="{ current: i === crumbs.length - 1 }">
                {{ c }}<em v-if="i < crumbs.length - 1"> / </em>
              </span>
            </template>
            <h1 v-else>{{ route.meta.title }}</h1>
          </nav>
        </div>

        <div class="actions">
          <button type="button" class="site">
            <el-icon><Location /></el-icon>
            一号能源基地 / 2#作业区
          </button>
          <span class="wind mono" title="实时风速">
            <el-icon><WindPower /></el-icon> 5.2 m/s
          </span>
          <span class="signal c-success" title="平台在线率">
            <el-icon><Odometer /></el-icon> 98%
          </span>
          <button type="button" class="icon-btn notice" aria-label="消息通知">
            <el-icon><Bell /></el-icon><i></i>
          </button>
          <button type="button" class="icon-btn" :aria-label="isDark ? '切换日间模式' : '切换夜间模式'" @click="toggleTheme">
            <el-icon><Sunny v-if="isDark" /><Moon v-else /></el-icon>
          </button>
          <el-dropdown trigger="click" popper-class="qa-user-dropdown" @command="onUserCommand">
            <button type="button" class="avatar-btn" aria-label="个人中心">
              <img v-if="user?.avatar" :src="user.avatar" alt="头像" />
              <template v-else>{{ avatarChar }}</template>
            </button>
            <template #dropdown>
              <div class="dd-head">
                <strong>{{ user?.name || '安全管理员' }}</strong>
                <span>{{ user?.email || 'admin@qingan.com' }}</span>
              </div>
              <el-dropdown-menu>
                <el-dropdown-item command="settings"><el-icon><Setting /></el-icon>个人设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided class="dd-danger"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main><router-view /></main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Grid, Notebook, Van, VideoCamera, Film, Microphone, Aim,
  DataAnalysis, WarningFilled, Setting, Document,
  Fold, Expand, Bell, Location, WindPower, Odometer, SwitchButton,
  Sunny, Moon,
} from '@element-plus/icons-vue'
import { auth, avatarFallback, loadMe, logout, preferences, savePreferences } from '@/auth'
import { activeTheme, applyTheme } from '@/theme'

const route = useRoute()
const router = useRouter()
const collapsed = ref(preferences().sidebarCollapsed)
const user = computed(() => auth.user)
const avatarChar = computed(() => avatarFallback(auth.user))
const isDark = computed(() => activeTheme.value === 'dark')

onMounted(loadMe)

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  applyTheme(next)
  // 同步到账号偏好,保证个人设置页与后端记录一致
  savePreferences({ theme: next }).catch(() => {})
}

async function onLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch { return }
  logout()
  router.replace('/login')
}

function onUserCommand(command) {
  if (command === 'settings') router.push('/settings')
  else if (command === 'logout') onLogout()
}

// 与设计稿侧边栏一致的菜单结构
const menu = [
  { path: '/workbench', title: '工作台', icon: Grid },
  { title: '台账管理', icon: Notebook, children: [{ path: '/ledger/risk-events', title: '风险事件处置' }] },
  {
    title: '吊车管理', icon: Van,
    children: [
      { path: '/crane/list', title: '吊车' },
      { path: '/crane/monitor', title: '实时监控' },
      { path: '/crane/perimeter-camera', title: '周界摄像头' },
      { path: '/crane/heartbeat', title: '心跳检测' },
      { path: '/crane/device-link', title: '设备关联' },
      { path: '/crane/device-type', title: '设备类型' },
      { path: '/crane/edge-box', title: '边缘盒子' },
      { path: '/crane/radar', title: '雷达传感器' },
      { path: '/crane/radar-info', title: '雷达信息' },
    ],
  },
  { path: '/camera', title: '摄像头管理', icon: VideoCamera },
  { path: '/nvr', title: '录像机管理', icon: Film },
  {
    title: '音柱管理', icon: Microphone,
    children: [
      { path: '/speaker/list', title: '音柱' },
      { path: '/speaker/links', title: '音柱关联' },
    ],
  },
  { path: '/fence', title: '电子围栏', icon: Aim },
  { path: '/report', title: '安全报表', icon: DataAnalysis },
  { title: '违章类型', icon: WarningFilled, children: [{ path: '/violation/categories', title: '违章大类管理' }] },
  {
    title: '基础配置', icon: Setting,
    children: [
      { path: '/config/system', title: '系统配置' },
      { path: '/config/approval', title: '审批配置' },
      { path: '/config/threshold', title: '阈值配置' },
      { path: '/config/push', title: '推送策略配置' },
    ],
  },
  { path: '/audit', title: '审计日志', icon: Document },
]

const crumbs = computed(() => route.meta.crumbs || [])
</script>

<style scoped>
.shell {
  display: grid;
  grid-template-columns: var(--qa-sidebar-w) minmax(0, 1fr);
  height: 100vh;
  transition: grid-template-columns .2s;
}
.shell.collapsed { grid-template-columns: 64px minmax(0, 1fr); }

/* ---------- 侧边栏 ---------- */
aside {
  display: flex; flex-direction: column; overflow: hidden;
  background: var(--qa-sidebar);
  border-right: 1px solid var(--qa-border);
}
.brand {
  height: var(--qa-header-h); flex-shrink: 0;
  display: flex; align-items: center; gap: 10px; padding: 0 14px;
  border-bottom: 1px solid var(--qa-border);
}
.brand img {
  width: 36px; height: 36px; padding: 4px; object-fit: contain;
  background: var(--qa-panel-2); border: 1px solid var(--qa-border-strong); border-radius: 8px;
}
.brand strong { display: block; font-size: 17px; letter-spacing: 3px; color: var(--qa-text); }
.brand span { display: block; margin-top: 2px; font-size: 10px; color: var(--qa-text-muted); letter-spacing: 1px; white-space: nowrap; }

.side-menu {
  flex: 1; overflow-y: auto; border-right: none;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: var(--qa-text-2);
  --el-menu-hover-text-color: var(--qa-text);
  --el-menu-hover-bg-color: rgba(59, 130, 246, .08);
  --el-menu-active-color: var(--qa-text);
  --el-menu-item-height: 44px;
  --el-menu-sub-item-height: 38px;
  padding: 10px 8px;
}
.side-menu:not(.el-menu--collapse) { width: 100%; }
.side-menu :deep(.el-menu-item),
.side-menu :deep(.el-sub-menu__title) { border-radius: 6px; margin-bottom: 2px; }
.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(59, 130, 246, .25), rgba(59, 130, 246, .08));
  box-shadow: inset 2px 0 0 var(--qa-cyan);
}
.side-menu :deep(.el-menu .el-menu-item) { padding-left: 46px !important; }

.user-box {
  flex-shrink: 0; display: flex; align-items: center; gap: 10px;
  margin: 10px; padding: 10px;
  background: var(--qa-panel); border: 1px solid var(--qa-border); border-radius: 8px;
}
.avatar {
  display: grid; place-items: center; width: 32px; height: 32px; flex-shrink: 0;
  background: var(--qa-blue); color: #fff; border-radius: 50%; font-size: 14px;
  overflow: hidden;
}
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.user-box div { min-width: 0; }
.user-box strong { display: block; font-size: 13px; white-space: nowrap; }
.user-box div span { display: block; font-size: 11px; color: var(--qa-text-muted); white-space: nowrap; }
.logout { margin-left: auto; color: var(--qa-text-muted); cursor: pointer; }
.logout:hover { color: var(--qa-danger); }

/* ---------- 顶栏 ---------- */
.work { display: grid; grid-template-rows: var(--qa-header-h) minmax(0, 1fr); min-width: 0; }
.work > header {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 0 20px;
  background: var(--qa-bg-2);
  border-bottom: 1px solid var(--qa-border);
}
.heading { display: flex; align-items: center; gap: 12px; min-width: 0; }
.fold {
  display: grid; place-items: center; width: 32px; height: 32px;
  border: 0; background: transparent; color: var(--qa-text-2); cursor: pointer; border-radius: 6px;
}
.fold:hover { background: var(--qa-panel-3); color: var(--qa-text); }
.crumbs { font-size: 14px; color: var(--qa-text-muted); white-space: nowrap; overflow: hidden; }
.crumbs .current { color: var(--qa-text); font-weight: 600; }
.crumbs em { font-style: normal; margin: 0 2px; }
.crumbs h1 { margin: 0; font-size: 16px; font-weight: 600; color: var(--qa-text); }

.actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.site {
  display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  color: var(--qa-cyan); font-size: 13px; cursor: pointer;
  background: var(--qa-cyan-dim); border: 1px solid rgba(34, 211, 238, .4); border-radius: 6px;
}
.wind, .signal { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; color: var(--qa-text-2); }
.icon-btn {
  position: relative; display: grid; place-items: center; width: 34px; height: 34px;
  border: 0; background: transparent; color: var(--qa-text-2); cursor: pointer; border-radius: 6px; font-size: 17px;
}
.icon-btn:hover { background: var(--qa-panel-3); color: var(--qa-text); }
.notice i {
  position: absolute; right: 7px; top: 6px; width: 6px; height: 6px;
  border-radius: 50%; background: var(--qa-danger);
}
.avatar-btn {
  width: 34px; height: 34px; display: grid; place-items: center;
  background: var(--qa-blue); color: #fff; border-radius: 50%; font-size: 14px;
  cursor: pointer; border: 2px solid transparent; outline: none;
  overflow: hidden; padding: 0;
}
.avatar-btn img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.avatar-btn:hover { border-color: var(--qa-cyan); }

main {
  min-width: 0; overflow: auto;
  background-color: var(--qa-bg);
  background-image:
    linear-gradient(rgba(34, 211, 238, .022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34, 211, 238, .018) 1px, transparent 1px);
  background-size: 48px 48px;
}

@media (max-width: 1100px) {
  .site, .wind, .signal { display: none; }
}
@media (max-width: 760px) {
  .shell { grid-template-columns: 64px minmax(0, 1fr); }
}
</style>
