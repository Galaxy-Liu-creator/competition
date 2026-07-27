<template>
  <div class="page workbench">
    <!-- 顶部 6 张统计卡 -->
    <section class="stat-row six">
      <StatCard label="在线吊车" :value="stat.craneOnline" :suffix="`/ ${stat.craneTotal} 台`" :icon="Van" accent="#3b82f6" hint="设备实时在线" />
      <StatCard label="设备在线率" :value="stat.onlineRate" suffix="%" :icon="Histogram" accent="#22c55e" hint="较昨日 +1.2%" />
      <StatCard label="今日告警" :value="stat.todayAlarm" suffix="次" :icon="WarningFilled" accent="#eab308" hint="含预警与提示" />
      <StatCard label="重大风险" :value="stat.majorRisk" suffix="个未闭环" :icon="CircleCloseFilled" accent="#ef4444" hint="需立即处置" />
      <StatCard label="进行中作业" :value="stat.workingTask" suffix="单" :icon="Files" accent="#3b82f6" hint="作业票已审批" />
      <StatCard label="电子围栏" :value="stat.fenceCount" suffix="条" :icon="Aim" accent="#22d3ee" hint="全部生效" />
    </section>

    <!-- 中部:鸟瞰图 + 告警队列 -->
    <section class="mid">
      <IndustrialPanel title="作业区实时鸟瞰" class="birdview">
        <template #extra>
          <div class="legend">
            <span><i class="dot ok"></i>正常区域</span>
            <span><i class="dot bad"></i>告警区域</span>
          </div>
        </template>
        <SiteMap />
      </IndustrialPanel>

      <IndustrialPanel title="实时告警队列" class="queue">
        <template #extra>共 {{ alarms.length }} 条</template>
        <div class="alarm-list">
          <article v-for="a in alarms" :key="a.id" class="alarm" :class="a.level">
            <header>
              <span class="tag">{{ a.levelLabel }}</span>
              <strong>{{ a.title }}</strong>
              <time class="mono">{{ a.time }}</time>
            </header>
            <p class="src"><el-icon><component :is="a.icon" /></el-icon>{{ a.source }}</p>
            <footer>
              <template v-if="a.level === 'danger'">
                <el-button size="small">查看告警</el-button>
                <el-button size="small" type="danger">发起喊话</el-button>
              </template>
              <el-button v-else-if="a.level === 'warning'" size="small" class="wfull">派单处置</el-button>
              <el-button v-else size="small" text class="wfull">查看维修工单</el-button>
            </footer>
          </article>
        </div>
      </IndustrialPanel>
    </section>

    <!-- 底部三面板 -->
    <section class="bottom">
      <IndustrialPanel title="设备健康状态">
        <div v-for="h in health" :key="h.label" class="health">
          <div class="hrow">
            <span>{{ h.label }}</span>
            <b class="mono" :class="h.tone">{{ h.value }}%</b>
          </div>
          <div class="bar"><i :style="{ width: h.value + '%', background: h.color }"></i></div>
        </div>
      </IndustrialPanel>

      <IndustrialPanel title="7日风险趋势">
        <BaseChart :option="trendOption" height="220px" />
      </IndustrialPanel>

      <IndustrialPanel title="高发违章类型">
        <div v-for="v in violations" :key="v.label" class="vrow">
          <span class="vname">{{ v.label }}</span>
          <div class="vbar"><i :style="{ width: v.pct + '%', background: v.color }"></i></div>
          <b class="mono">{{ v.count }}起</b>
        </div>
      </IndustrialPanel>
    </section>
  </div>
</template>

<script setup>
// 工作台:6 统计卡 + 鸟瞰图/告警队列 + 三分析面板;接口失败回退演示数据
import { markRaw, ref, onMounted } from 'vue'
import {
  Van, Histogram, WarningFilled, CircleCloseFilled, Files, Aim,
  Aim as AimIcon, VideoCamera, Odometer,
} from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'
import SiteMap from '@/components/map/SiteMap.vue'
import { dashboardApi, siteApi } from '@/api'

const stat = ref({
  craneOnline: 24, craneTotal: 28, onlineRate: 85.7, todayAlarm: 12,
  majorRisk: 3, workingTask: 5, fenceCount: 8,
})

const alarms = ref([
  { id: 1, level: 'danger', levelLabel: '严重告警', title: '违规闯入电子围栏', time: '10:42:15', source: '2#汽车吊 · B区闯入', icon: markRaw(AimIcon) },
  { id: 2, level: 'warning', levelLabel: '一般预警', title: '起吊重量接近极限', time: '10:38:06', source: '1#塔吊 · 载重 12.5t', icon: markRaw(Van) },
  { id: 3, level: 'info', levelLabel: '系统提示', title: '传感器离线', time: '09:15:22', source: '雷达-04 · 通信中断', icon: markRaw(Odometer) },
])

const health = ref([
  { label: '车联终端 (28/28)', value: 100, color: '#22c55e', tone: 'c-success' },
  { label: '防碰撞雷达 (14/14)', value: 96.4, color: '#eab308', tone: 'c-gold' },
  { label: 'AI 边缘计算盒 (5/6)', value: 83.3, color: '#22c55e', tone: 'c-success' },
])

const violations = ref([
  { label: '非法闯入', count: 42, pct: 100, color: '#ef4444' },
  { label: '超载吊装', count: 28, pct: 67, color: '#eab308' },
  { label: '未戴安全帽', count: 19, pct: 45, color: '#3b82f6' },
  { label: '疲劳驾驶', count: 12, pct: 29, color: '#22d3ee' },
])

const trendOption = ref(buildTrend([5, 8, 6, 12, 9, 7, 11], [2, 3, 1, 5, 3, 2, 4]))

function buildTrend(risk, major, dates = ['1日', '2日', '3日', '4日', '5日', '6日', '今日']) {
  return {
    grid: { top: 20, left: 36, right: 16, bottom: 26 },
    tooltip: { trigger: 'axis' },
    legend: { data: ['风险事件', '重大风险'], textStyle: { color: '#8ba3c2' }, right: 0, top: 0, itemWidth: 12, itemHeight: 8 },
    xAxis: {
      type: 'category', boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: '#1e3a5c' } },
      axisLabel: { color: '#55708f', fontSize: 11 },
    },
    yAxis: {
      type: 'value', splitLine: { lineStyle: { color: 'rgba(30,58,92,.5)' } },
      axisLabel: { color: '#55708f', fontSize: 11 },
    },
    series: [
      { name: '风险事件', type: 'line', smooth: true, data: risk, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#22d3ee', width: 2 }, itemStyle: { color: '#22d3ee' },
        areaStyle: { color: 'rgba(34,211,238,.12)' } },
      { name: '重大风险', type: 'line', smooth: true, data: major, symbol: 'circle', symbolSize: 6,
        lineStyle: { color: '#ef4444', width: 2 }, itemStyle: { color: '#ef4444' } },
    ],
  }
}

onMounted(async () => {
  // 接口成功则覆盖演示数据；结构化数字来自后端，失败时保留固定回退。
  try {
    const ov = await dashboardApi.overview()
    const stats = ov?.stats || {}
    stat.value.todayAlarm = stats.todayAlerts ?? stat.value.todayAlarm
    stat.value.majorRisk = stats.criticalAlarms ?? stat.value.majorRisk
    if (stats.totalDevices) {
      stat.value.onlineRate = Math.round((stats.onlineDevices / stats.totalDevices) * 1000) / 10
    }
    const series = ov?.trend?.series || []
    if (series.length) {
      trendOption.value = buildTrend(
        series[0]?.data || [],
        series[1]?.data || [],
        ov.trend.dates || undefined,
      )
    }
    if (Array.isArray(ov?.recentAlarms) && ov.recentAlarms.length) {
      const levelMap = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info' }
      alarms.value = ov.recentAlarms.slice(0, 3).map((alarm, i) => ({
        id: alarm.id ?? i,
        level: levelMap[alarm.level] || 'info',
        levelLabel: alarm.levelLabel || '系统提示',
        title: alarm.title || alarm.typeLabel || '风险事件',
        time: alarm.occurredAt ? String(alarm.occurredAt).slice(11, 19) : '--:--:--',
        source: [alarm.deviceId, alarm.description].filter(Boolean).join(' · ') || '现场监测节点',
        icon: markRaw(AimIcon),
      }))
    }
  } catch { /* 回退演示数据 */ }

  try {
    const map = await siteApi.mapOverview('site-001')
    const devices = map?.devices || []
    const cranes = devices.filter((device) => device.type === 'crane')
    stat.value.craneTotal = cranes.length || stat.value.craneTotal
    stat.value.craneOnline = cranes.filter((device) => device.status !== 'offline').length || 0
    stat.value.workingTask = devices.filter((device) => device.status === 'working').length
    stat.value.fenceCount = (map?.fences || []).length || stat.value.fenceCount
  } catch { /* 回退演示数据 */ }

  try {
    const categories = await dashboardApi.categoryDistribution()
    if (Array.isArray(categories) && categories.length) {
      const max = Math.max(...categories.map((item) => Number(item.value) || 0), 1)
      violations.value = categories.slice(0, 4).map((item, i) => ({
        label: item.name || '其他风险',
        count: item.value || 0,
        pct: Math.round(((item.value || 0) / max) * 100),
        color: ['#ef4444', '#eab308', '#3b82f6', '#22d3ee'][i],
      }))
    }
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.workbench { gap: 14px; }
.stat-row.six { grid-template-columns: repeat(6, minmax(0, 1fr)); }

/* 中部布局 */
.mid { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 14px; }
.birdview :deep(.body) { padding: 0; height: 520px; }
.legend { display: flex; gap: 14px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; color: var(--qa-text-2); }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.ok { background: var(--qa-success); box-shadow: 0 0 8px var(--qa-success); }
.dot.bad { background: var(--qa-danger); box-shadow: 0 0 8px var(--qa-danger); }

/* 告警队列 */
.queue :deep(.body) { padding: 12px; }
.alarm-list { display: flex; flex-direction: column; gap: 12px; }
.alarm { padding: 12px; border-radius: 6px; border-left: 3px solid; background: var(--qa-panel-2); }
.alarm.danger { border-color: var(--qa-danger); }
.alarm.warning { border-color: var(--qa-warning); }
.alarm.info { border-color: var(--qa-blue); }
.alarm header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.alarm .tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; color: #fff; }
.alarm.danger .tag { background: var(--qa-danger); }
.alarm.warning .tag { background: var(--qa-warning); color: #1a1200; }
.alarm.info .tag { background: var(--qa-blue); }
.alarm header strong { font-size: 13px; }
.alarm time { margin-left: auto; font-size: 11px; color: var(--qa-text-muted); }
.alarm .src { display: flex; align-items: center; gap: 6px; margin: 0 0 10px; font-size: 12px; color: var(--qa-text-2); }
.alarm footer { display: flex; gap: 8px; }
.alarm footer :deep(.wfull) { flex: 1; }

/* 底部三面板 */
.bottom { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.health { margin-bottom: 16px; }
.health:last-child { margin-bottom: 0; }
.hrow { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; color: var(--qa-text-2); }
.bar { height: 8px; border-radius: 4px; background: var(--qa-panel-2); overflow: hidden; }
.bar i { display: block; height: 100%; border-radius: 4px; }
.vrow { display: grid; grid-template-columns: 76px 1fr 44px; align-items: center; gap: 10px; margin-bottom: 14px; }
.vrow:last-child { margin-bottom: 0; }
.vname { font-size: 12px; color: var(--qa-text-2); }
.vbar { height: 10px; border-radius: 5px; background: var(--qa-panel-2); overflow: hidden; }
.vbar i { display: block; height: 100%; border-radius: 5px; }
.vrow b { text-align: right; font-size: 12px; }

@media (max-width: 1400px) { .stat-row.six { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 1200px) { .mid { grid-template-columns: 1fr; } .bottom { grid-template-columns: 1fr; } }
</style>
