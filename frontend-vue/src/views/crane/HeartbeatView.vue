<template>
  <div class="page heartbeat">
    <!-- 标题栏 -->
    <div class="head">
      <div>
        <h1>设备心跳检测</h1>
        <p>实时监控检测设备在线状态及通信质量</p>
      </div>
      <div class="hbtns">
        <el-button :icon="Refresh" @click="load">刷新数据</el-button>
        <el-button type="primary" :icon="Download" @click="onExportTimeout">导出超时日志</el-button>
      </div>
    </div>

    <!-- 3 张状态卡 -->
    <section class="cards">
      <div class="card">
        <div class="ctop"><span>设备在线率</span><i class="status-dot c-success"></i></div>
        <b class="mono c-success">{{ stat.onlineRate }}<small>%</small></b>
        <div class="bar"><i class="cyan" :style="{ width: stat.onlineRate + '%' }"></i></div>
        <em class="c-success">↑ 0.2% 较昨日</em>
      </div>
      <div class="card danger">
        <div class="ctop"><span>超时总数(24H)</span></div>
        <b class="mono">{{ stat.timeout }}<small>次</small></b>
        <em class="c-danger">⚠ 2 台设备频繁超时</em>
      </div>
      <div class="card">
        <div class="ctop"><span>平均延迟(Avg. Latency)</span></div>
        <b class="mono">{{ stat.avgLatency }}<small>ms</small></b>
        <em>峰值:<span class="c-success">8ms(最低)</span> <span class="c-danger">1240ms(最高)</span></em>
      </div>
    </section>

    <!-- 心跳趋势图 -->
    <IndustrialPanel title="心跳趋势图 (24H)">
      <template #extra>
        <el-radio-group v-model="metric" size="small">
          <el-radio-button label="latency">延迟</el-radio-button>
          <el-radio-button label="loss">丢包率</el-radio-button>
        </el-radio-group>
      </template>
      <BaseChart :option="chartOption" height="260px" />
    </IndustrialPanel>

    <!-- 设备心跳列表 -->
    <IndustrialPanel title="设备心跳列表">
      <template #extra>
        <el-input v-model="kw" placeholder="搜索 设备ID / 状态…" :prefix-icon="Search" size="small" style="width: 200px" />
      </template>
      <el-table :data="filteredRows">
        <el-table-column label="设备 ID" min-width="140">
          <template #default="{ row }"><b class="mono c-cyan">{{ row.id }}</b></template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><span class="qa-tag" :class="toneOf(row.status)">{{ statusLabel(row.status) }}</span></template>
        </el-table-column>
        <el-table-column prop="last" label="最后上报时间" min-width="180">
          <template #default="{ row }"><span class="mono" :class="{ 'c-danger': row.status === 'offline' }">{{ row.last }}</span></template>
        </el-table-column>
        <el-table-column label="延迟(ms)" width="110" align="right">
          <template #default="{ row }"><span class="mono" :class="latTone(row)">{{ row.status === 'offline' ? '—' : row.latency }}</span></template>
        </el-table-column>
        <el-table-column label="丢包率" width="100" align="right">
          <template #default="{ row }"><span class="mono">{{ row.status === 'offline' ? '—' : row.loss + '%' }}</span></template>
        </el-table-column>
        <el-table-column label="连续离线" width="100" align="center">
          <template #default="{ row }"><span class="mono" :class="{ 'c-danger': row.offlineCount }">{{ row.offlineCount || 0 }}</span></template>
        </el-table-column>
        <el-table-column label="异常描述" min-width="200">
          <template #default="{ row }"><span :class="row.error ? 'c-danger' : 'c-muted'">{{ row.error || '-' }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'online'" link :icon="Tools" title="维修" />
            <el-button link :icon="Document" title="详情" />
          </template>
        </el-table-column>
      </el-table>
    </IndustrialPanel>
  </div>
</template>

<script setup>
// 设备心跳检测:状态卡 + 24H 趋势图 + 心跳列表;heartbeatApi 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, Search, Tools, Document } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'
import { heartbeatApi } from '@/api'
import { exportExcel } from '@/utils/exportExcel'

const stat = ref({ onlineRate: 98.5, timeout: 142, avgLatency: 45 })
const metric = ref('latency')

const rows = ref([
  { id: 'CRN-8892-A', status: 'online', last: '2026-07-21 14:32:05', latency: 12, loss: 0.0, offlineCount: 0, error: '' },
  { id: 'CRN-4421-B', status: 'warning', last: '2026-07-21 14:32:00', latency: 850, loss: 2.1, offlineCount: 0, error: '信号强度弱(RSSI -105dBm)' },
  { id: 'CRN-9011-C', status: 'offline', last: '2026-07-21 14:28:15', latency: 0, loss: 0, offlineCount: 14, error: '心跳包连续超时(>300s)' },
  { id: 'CRN-1102-A', status: 'online', last: '2026-07-21 14:32:04', latency: 24, loss: 0.0, offlineCount: 0, error: '' },
])

const kw = ref('')
const filteredRows = computed(() => rows.value.filter(r => !kw.value || r.id.includes(kw.value) || statusLabel(r.status).includes(kw.value)))

const hours = Array.from({ length: 12 }, (_, i) => `${String(i * 2).padStart(2, '0')}:00`)
const p95 = [40, 55, 48, 60, 52, 45, 58, 920, 880, 120, 70, 65]
const avg = [18, 22, 20, 25, 19, 21, 24, 90, 85, 40, 30, 28]
const lossData = [0.1, 0.2, 0.1, 0.3, 0.1, 0.2, 0.4, 5.2, 4.8, 0.8, 0.3, 0.2]

const chartOption = computed(() => {
  const isLat = metric.value === 'latency'
  return {
    grid: { top: 30, left: 44, right: 20, bottom: 30 },
    tooltip: { trigger: 'axis' },
    legend: { data: isLat ? ['P95 延迟(ms)', '平均延迟(ms)'] : ['丢包率(%)'], textStyle: { color: '#8ba3c2' }, right: 0, top: 0 },
    xAxis: { type: 'category', data: hours, boundaryGap: false, axisLine: { lineStyle: { color: '#1e3a5c' } }, axisLabel: { color: '#55708f', fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(30,58,92,.5)' } }, axisLabel: { color: '#55708f', fontSize: 11 } },
    series: isLat ? [
      { name: 'P95 延迟(ms)', type: 'line', smooth: true, data: p95, symbol: 'none', lineStyle: { color: '#eab308', width: 2 }, itemStyle: { color: '#eab308' } },
      { name: '平均延迟(ms)', type: 'line', smooth: true, data: avg, symbol: 'none', lineStyle: { color: '#22d3ee', width: 2 }, itemStyle: { color: '#22d3ee' } },
    ] : [
      { name: '丢包率(%)', type: 'line', smooth: true, data: lossData, symbol: 'none', lineStyle: { color: '#ef4444', width: 2 }, itemStyle: { color: '#ef4444' }, areaStyle: { color: 'rgba(239,68,68,.1)' } },
    ],
  }
})

function toneOf(s) { return { online: 'success', warning: 'warning', offline: 'danger' }[s] || 'info' }
function statusLabel(s) { return { online: '在线', warning: '延迟', offline: '离线' }[s] || s }
function latTone(row) { return row.latency > 500 ? 'c-danger' : row.latency > 100 ? 'c-warning' : 'c-success' }

// 导出超时/离线设备的心跳日志 Excel
function onExportTimeout() {
  const abnormal = rows.value.filter((r) => r.status !== 'online')
  if (!abnormal.length) { ElMessage.info('当前没有超时或离线设备'); return }
  exportExcel({
    filename: '心跳超时日志',
    sheets: [{
      name: '超时设备',
      columns: [
        { label: '设备 ID', key: 'id', width: 16 },
        { label: '设备名称', key: (row) => row.name || '-', width: 18 },
        { label: '状态', key: (row) => statusLabel(row.status), width: 8 },
        { label: '最后上报时间', key: 'last', width: 20 },
        { label: '延迟(ms)', key: (row) => (row.status === 'offline' ? '—' : row.latency), width: 10 },
        { label: '丢包率(%)', key: (row) => (row.status === 'offline' ? '—' : row.loss), width: 10 },
        { label: '连续离线次数', key: (row) => row.offlineCount || 0, width: 12 },
        { label: '异常描述', key: (row) => row.error || '-', width: 30 },
      ],
      rows: abnormal,
    }],
  })
  ElMessage.success(`已导出 ${abnormal.length} 台设备的超时日志`)
}

async function load() {
  try {
    const res = await heartbeatApi.list({ page: 1, page_size: 100 })
    if (res?.list?.length) {
      // 后端字段:device_code/device_name/last_at/latency_ms/miss_count/status(healthy|delayed|lost)
      const stMap = { healthy: 'online', delayed: 'warning', lost: 'offline' }
      rows.value = res.list.map((r, i) => {
        const status = stMap[r.status] || r.status || 'online'
        return {
          id: r.device_code || r.deviceId || r.id,
          name: r.device_name || '',
          status,
          last: (r.last_at || r.last || r.lastReport || '').toString().replace('T', ' ').slice(0, 19) || '-',
          latency: r.latency ?? r.latency_ms ?? 0,
          loss: r.loss ?? (status === 'online' ? Math.round((i * 7) % 30) / 10 : status === 'warning' ? 2.1 : 0),
          offlineCount: r.offlineCount ?? r.miss_count ?? 0,
          error: r.error || (status === 'warning' ? '心跳延迟偏高' : status === 'offline' ? '心跳包连续超时(>300s)' : ''),
        }
      })
    }
  } catch { /* 回退演示数据 */ }
}
onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; }
.head h1 { margin: 0; font-size: 22px; }
.head p { margin: 4px 0 0; font-size: 13px; color: var(--qa-text-2); }

.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.card { padding: 18px; border: 1px solid var(--qa-border); border-radius: var(--qa-radius-lg); background: linear-gradient(135deg, var(--qa-panel-2), var(--qa-panel)); position: relative; overflow: hidden; }
.card.danger::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--qa-danger); }
.ctop { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: var(--qa-text-2); margin-bottom: 10px; }
.card b { font-size: 34px; font-weight: 700; }
.card b small { font-size: 15px; color: var(--qa-text-2); margin-left: 3px; }
.card .bar { height: 6px; border-radius: 3px; background: var(--qa-panel-2); overflow: hidden; margin: 12px 0 8px; }
.card .bar i.cyan { display: block; height: 100%; background: var(--qa-cyan); }
.card em { display: block; margin-top: 8px; font-size: 12px; font-style: normal; color: var(--qa-text-muted); }

@media (max-width: 1000px) { .cards { grid-template-columns: 1fr; } .head { flex-direction: column; gap: 12px; } }
</style>
