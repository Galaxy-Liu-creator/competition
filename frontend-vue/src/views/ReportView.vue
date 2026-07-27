<template>
  <div class="page">
    <div class="head">
      <h1>安全报表</h1>
      <div class="head-actions">
        <el-radio-group v-model="range" size="small" @change="buildCharts">
          <el-radio-button value="7">近 7 日</el-radio-button>
          <el-radio-button value="30">近 30 日</el-radio-button>
        </el-radio-group>
        <el-date-picker v-model="dateRange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width: 240px" @change="buildCharts" />
        <el-button type="primary" size="small" @click="onExport"><el-icon><Download /></el-icon>&nbsp;导出报表</el-button>
      </div>
    </div>

    <div class="stat-row">
      <StatCard label="事件总数" :value="kpi.total" suffix="起" accent="#22d3ee" />
      <StatCard label="已闭环" :value="kpi.resolved" suffix="起" accent="#22c55e" />
      <StatCard label="高风险占比" :value="kpi.highRate" suffix="%" accent="#ef4444" />
      <StatCard label="待处置" :value="kpi.pending" suffix="起" accent="#eab308" />
    </div>

    <div class="chart-grid">
      <IndustrialPanel :title="`${range} 日事件趋势`"><BaseChart :option="trendOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="违章类型分布"><BaseChart :option="pieOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="各作业区事件对比"><BaseChart :option="barOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="处置状态统计"><BaseChart :option="timeOption" height="280px" /></IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'
import { riskEventApi } from '@/api'
import { exportExcel } from '@/utils/exportExcel'

const range = ref('7')
const dateRange = ref()
const kpi = reactive({ total: 36, resolved: 18, highRate: 33.3, pending: 18 })
const events = ref([])

const fallbackEvents = [
  { id: 1, type: '违规闯入', level: 'critical', status: 'pending', work_zone: 'A区-东侧', occurred_at: '2026-07-19T15:32:18+08:00' },
  { id: 2, type: '超载起吊', level: 'critical', status: 'processing', work_zone: 'B区-南侧', occurred_at: '2026-07-19T14:26:45+08:00' },
  { id: 3, type: '未佩戴安全帽', level: 'major', status: 'resolved', work_zone: 'C区-中央', occurred_at: '2026-07-18T13:42:10+08:00' },
  { id: 4, type: '设备离线', level: 'general', status: 'closed', work_zone: 'D区-北侧', occurred_at: '2026-07-17T11:21:02+08:00' },
  { id: 5, type: '斜拉斜吊', level: 'critical', status: 'closed', work_zone: 'A区-西侧', occurred_at: '2026-07-16T09:12:44+08:00' },
  { id: 6, type: '未系安全带', level: 'major', status: 'resolved', work_zone: 'E区-东侧', occurred_at: '2026-07-15T16:08:31+08:00' },
  { id: 7, type: '周界越界', level: 'general', status: 'processing', work_zone: 'F区-中央', occurred_at: '2026-07-14T20:44:18+08:00' },
  { id: 8, type: '设备离线', level: 'general', status: 'closed', work_zone: 'B区-北侧', occurred_at: '2026-07-13T08:20:05+08:00' },
]

const axis = { axisLine: { lineStyle: { color: '#1e3a5c' } }, axisLabel: { color: '#8ba3c2' }, splitLine: { lineStyle: { color: 'rgba(30,58,92,.5)' } } }
const grid = { left: 40, right: 20, top: 40, bottom: 30 }
const trendOption = ref({})
const pieOption = ref({})
const barOption = ref({})
const timeOption = ref({})

const dayKey = (value) => {
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value)) return value.slice(0, 10)
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
const shortDay = (value) => String(value).slice(5)
const addDays = (value, amount) => {
  const result = new Date(value)
  result.setDate(result.getDate() + amount)
  return result
}

function selectedEvents() {
  const source = events.value.length ? events.value : fallbackEvents
  if (!dateRange.value || dateRange.value.length !== 2) return source
  const start = new Date(dateRange.value[0]).setHours(0, 0, 0, 0)
  const end = new Date(dateRange.value[1]).setHours(23, 59, 59, 999)
  return source.filter((event) => {
    const timestamp = new Date(event.occurred_at).getTime()
    return timestamp >= start && timestamp <= end
  })
}

function buildCharts() {
  const rows = selectedEvents()
  const days = Number(range.value)
  const latest = rows.reduce((max, row) => {
    const date = new Date(row.occurred_at)
    return date > max ? date : max
  }, new Date('2026-07-19T23:59:59+08:00'))
  const labels = Array.from({ length: days }, (_, index) => dayKey(addDays(latest, index - days + 1)))
  const countByDay = Object.fromEntries(labels.map((label) => [label, 0]))
  const highByDay = Object.fromEntries(labels.map((label) => [label, 0]))
  rows.forEach((row) => {
    const key = dayKey(row.occurred_at)
    if (key in countByDay) {
      countByDay[key] += 1
      if (['critical', 'high', 'major'].includes(row.level)) highByDay[key] += 1
    }
  })

  const resolved = rows.filter((row) => ['resolved', 'closed'].includes(row.status)).length
  const high = rows.filter((row) => ['critical', 'high', 'major'].includes(row.level)).length
  kpi.total = rows.length
  kpi.resolved = resolved
  kpi.highRate = rows.length ? Math.round((high / rows.length) * 1000) / 10 : 0
  kpi.pending = rows.filter((row) => ['pending', 'processing'].includes(row.status)).length

  trendOption.value = {
    tooltip: { trigger: 'axis' }, legend: { data: ['风险事件', '高风险'], textStyle: { color: '#8ba3c2' }, top: 6 }, grid,
    xAxis: { type: 'category', data: labels.map(shortDay), ...axis }, yAxis: { type: 'value', ...axis },
    series: [
      { name: '风险事件', type: 'line', smooth: true, data: labels.map((label) => countByDay[label]), itemStyle: { color: '#22d3ee' }, areaStyle: { color: 'rgba(34,211,238,.12)' } },
      { name: '高风险', type: 'line', smooth: true, data: labels.map((label) => highByDay[label]), itemStyle: { color: '#ef4444' } },
    ],
  }

  const typeCounts = new Map()
  rows.forEach((row) => typeCounts.set(row.type || '其他风险', (typeCounts.get(row.type || '其他风险') || 0) + 1))
  pieOption.value = {
    tooltip: { trigger: 'item' }, legend: { bottom: 0, textStyle: { color: '#8ba3c2' } },
    series: [{ type: 'pie', radius: ['45%', '68%'], center: ['50%', '44%'], label: { color: '#e8f1fd' }, data: [...typeCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5).map(([name, value], index) => ({ value, name, itemStyle: { color: ['#ef4444', '#f59e0b', '#22d3ee', '#3b82f6', '#8b5cf6'][index] } })) }],
  }

  const zoneCounts = new Map()
  rows.forEach((row) => zoneCounts.set(row.work_zone || '未分区', (zoneCounts.get(row.work_zone || '未分区') || 0) + 1))
  const zones = [...zoneCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
  barOption.value = {
    tooltip: { trigger: 'axis' }, grid,
    xAxis: { type: 'category', data: zones.map(([name]) => name.replace('区-', '·')), ...axis }, yAxis: { type: 'value', ...axis },
    series: [{ type: 'bar', barWidth: '46%', data: zones.map(([, value]) => value), itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] } }],
  }

  const statuses = [
    ['待处置', 'pending'], ['处理中', 'processing'], ['已解决', 'resolved'], ['已关闭', 'closed'],
  ]
  timeOption.value = {
    tooltip: { trigger: 'axis' }, grid,
    xAxis: { type: 'category', data: statuses.map(([label]) => label), ...axis }, yAxis: { type: 'value', ...axis },
    series: [{ type: 'bar', barWidth: '46%', data: statuses.map(([, status]) => rows.filter((row) => row.status === status).length), itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] } }],
  }
}

async function loadEvents() {
  try {
    const response = await riskEventApi.list({ page: 1, page_size: 200 })
    events.value = response?.list?.length ? response.list : fallbackEvents
  } catch {
    events.value = fallbackEvents
  }
  buildCharts()
}

const levelLabel = (level) => ({ critical: '严重', high: '高风险', major: '较大', general: '一般' }[level] || level || '一般')
const statusLabel = (status) => ({ pending: '待处置', processing: '处理中', resolved: '已解决', closed: '已关闭' }[status] || status || '-')
const rangeLabel = () => {
  if (dateRange.value?.length === 2) return `${dayKey(dateRange.value[0])} 至 ${dayKey(dateRange.value[1])}`
  return `近 ${range.value} 日`
}

function onExport() {
  const rows = selectedEvents()
  const countBy = (keyFn) => {
    const map = new Map()
    rows.forEach((row) => { const key = keyFn(row); map.set(key, (map.get(key) || 0) + 1) })
    return [...map.entries()].sort((a, b) => b[1] - a[1]).map(([name, count]) => ({ name, count }))
  }
  exportExcel({
    filename: '安全报表',
    sheets: [
      {
        name: '概览',
        columns: [{ label: '指标', key: 'metric', width: 18 }, { label: '数值', key: 'value', width: 24 }],
        rows: [
          { metric: '统计范围', value: rangeLabel() },
          { metric: '事件总数', value: `${kpi.total} 起` },
          { metric: '已闭环', value: `${kpi.resolved} 起` },
          { metric: '高风险占比', value: `${kpi.highRate}%` },
          { metric: '待处置', value: `${kpi.pending} 起` },
        ],
      },
      {
        name: '事件明细',
        columns: [
          { label: '序号', key: (row) => rows.indexOf(row) + 1, width: 6 },
          { label: '事件编号', key: (row) => row.event_no || row.code || `EV-${row.id}`, width: 20 },
          { label: '风险类型', key: 'type', width: 16 },
          { label: '等级', key: (row) => levelLabel(row.level), width: 10 },
          { label: '处置状态', key: (row) => statusLabel(row.status), width: 10 },
          { label: '作业区域', key: (row) => row.work_zone || '未分区', width: 14 },
          { label: '设备编号', key: (row) => row.device_code || '-', width: 14 },
          { label: '发生时间', key: (row) => String(row.occurred_at || '').replace('T', ' ').slice(0, 19), width: 20 },
          { label: '处理人', key: (row) => row.handler || '-', width: 10 },
        ],
        rows,
      },
      {
        name: '类型分布',
        columns: [{ label: '违章类型', key: 'name', width: 20 }, { label: '数量', key: 'count', width: 10 }],
        rows: countBy((row) => row.type || '其他风险'),
      },
      {
        name: '区域分布',
        columns: [{ label: '作业区域', key: 'name', width: 20 }, { label: '数量', key: 'count', width: 10 }],
        rows: countBy((row) => row.work_zone || '未分区'),
      },
      {
        name: '处置状态',
        columns: [{ label: '状态', key: 'name', width: 16 }, { label: '数量', key: 'count', width: 10 }],
        rows: countBy((row) => statusLabel(row.status)),
      },
    ],
  })
  ElMessage.success(`已导出 Excel 报表(${rangeLabel()},共 ${rows.length} 起事件)`)
}

onMounted(loadEvents)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.head h1 { margin: 0; font-size: 20px; }
.head-actions { display: flex; gap: 10px; align-items: center; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 1000px) { .chart-grid { grid-template-columns: 1fr; } }
</style>
