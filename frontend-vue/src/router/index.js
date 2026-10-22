import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn, preferences } from '@/auth'

// 路由与侧边栏菜单共用的页面清单
// meta.title 用于顶栏标题与 document.title,meta.crumbs 用于面包屑
const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { title: '登录', public: true } },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/workbench',
    children: [
      { path: 'workbench', name: 'workbench', component: () => import('@/views/WorkbenchView.vue'), meta: { title: '工作台' } },

      { path: 'ledger/risk-events', name: 'risk-events', component: () => import('@/views/ledger/RiskEventView.vue'), meta: { title: '风险事件处置', crumbs: ['台账管理', '风险事件处置'] } },

      { path: 'crane/list', name: 'crane-list', component: () => import('@/views/crane/CraneListView.vue'), meta: { title: '吊车', crumbs: ['吊车管理', '吊车'] } },
      { path: 'crane/monitor', name: 'crane-monitor', component: () => import('@/views/crane/CraneMonitorView.vue'), meta: { title: '实时监控', crumbs: ['吊车管理', '实时监控'] } },
      { path: 'crane/perimeter-camera', name: 'perimeter-camera', component: () => import('@/views/crane/PerimeterCameraView.vue'), meta: { title: '周界摄像头', crumbs: ['吊车管理', '周界摄像头'] } },
      { path: 'crane/heartbeat', name: 'heartbeat', component: () => import('@/views/crane/HeartbeatView.vue'), meta: { title: '心跳检测', crumbs: ['吊车管理', '心跳检测'] } },
      { path: 'crane/device-link', name: 'device-link', component: () => import('@/views/crane/DeviceLinkView.vue'), meta: { title: '设备关联', crumbs: ['吊车管理', '设备关联'] } },
      { path: 'crane/device-type', name: 'device-type', component: () => import('@/views/crane/DeviceTypeView.vue'), meta: { title: '设备类型', crumbs: ['吊车管理', '设备类型'] } },
      { path: 'crane/edge-box', name: 'edge-box', component: () => import('@/views/crane/EdgeBoxView.vue'), meta: { title: '边缘盒子', crumbs: ['吊车管理', '边缘盒子'] } },
      { path: 'crane/radar', name: 'radar', component: () => import('@/views/crane/RadarView.vue'), meta: { title: '雷达传感器', crumbs: ['吊车管理', '雷达传感器'] } },
      { path: 'crane/radar-info', name: 'radar-info', component: () => import('@/views/crane/RadarInfoView.vue'), meta: { title: '雷达信息', crumbs: ['吊车管理', '雷达信息'] } },

      { path: 'camera', name: 'camera', component: () => import('@/views/device/CameraView.vue'), meta: { title: '摄像头管理' } },
      { path: 'nvr', name: 'nvr', component: () => import('@/views/device/NvrView.vue'), meta: { title: '录像机管理' } },
      { path: 'speaker/list', name: 'speaker', component: () => import('@/views/speaker/SpeakerView.vue'), meta: { title: '音柱', crumbs: ['音柱管理', '音柱'] } },
      { path: 'speaker/links', name: 'speaker-links', component: () => import('@/views/speaker/SpeakerLinkView.vue'), meta: { title: '音柱关联', crumbs: ['音柱管理', '音柱关联'] } },

      { path: 'fence', name: 'fence', component: () => import('@/views/FenceView.vue'), meta: { title: '电子围栏' } },
      { path: 'report', name: 'report', component: () => import('@/views/ReportView.vue'), meta: { title: '安全报表' } },
      { path: 'violation/categories', name: 'violation-categories', component: () => import('@/views/violation/ViolationCategoryView.vue'), meta: { title: '违章大类管理', crumbs: ['违章类型', '违章大类管理'] } },

      { path: 'config/system', name: 'config-system', component: () => import('@/views/config/SystemConfigView.vue'), meta: { title: '系统配置', crumbs: ['基础配置', '系统配置'] } },
      { path: 'config/approval', name: 'config-approval', component: () => import('@/views/config/ApprovalConfigView.vue'), meta: { title: '审批配置', crumbs: ['基础配置', '审批配置'] } },
      { path: 'config/threshold', name: 'config-threshold', component: () => import('@/views/config/ThresholdConfigView.vue'), meta: { title: '阈值配置', crumbs: ['基础配置', '阈值配置'] } },
      { path: 'config/push', name: 'config-push', component: () => import('@/views/config/PushConfigView.vue'), meta: { title: '推送策略配置', crumbs: ['基础配置', '推送策略配置'] } },

      { path: 'audit', name: 'audit', component: () => import('@/views/AuditLogView.vue'), meta: { title: '审计日志' } },

      { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { title: '个人设置', crumbs: ['个人中心', '个人设置'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/workbench' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 登录守卫:未登录一律去 /login;已登录访问 /login 则回默认落地页
router.beforeEach((to) => {
  if (!to.meta.public && !isLoggedIn()) {
    return { path: '/login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : {} }
  }
  if (to.path === '/login' && isLoggedIn()) {
    return preferences().landingPage || '/workbench'
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '油擎智安'}｜油擎智安`
})

export default router
