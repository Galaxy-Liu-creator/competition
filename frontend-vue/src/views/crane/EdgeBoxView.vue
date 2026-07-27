<template>
  <div class="page edgebox">
    <section class="stat-row four">
      <StatCard label="盒子总数" :value="stat.total" :icon="Box" accent="#3b82f6" hint="+12 本月" />
      <StatCard label="在线率" :value="stat.onlineRate" suffix="%" :icon="Connection" accent="#22c55e" hint="↑ 0.2%" />
      <StatCard label="CPU 异常警告" :value="stat.cpuAlarm" suffix="台设备超载" :icon="Cpu" accent="#ef4444" />
      <StatCard label="消息积压总量" :value="stat.backlog" :icon="WarningFilled" accent="#eab308" hint="需要注意" />
    </section>

    <section class="body-grid">
      <IndustrialPanel title="边缘设备监查列表">
        <template #extra>
          <div class="toolbar">
            <el-input v-model="kw" placeholder="搜索 ID / IP…" :prefix-icon="Search" size="small" style="width: 180px" />
            <el-button size="small" :icon="Filter" />
          </div>
        </template>
        <el-table :data="filteredRows" highlight-current-row @current-change="r => r && (current = r)">
          <el-table-column label="状态" width="60"><template #default="{ row }"><span class="status-dot" :class="toneOf(row.status)"></span></template></el-table-column>
          <el-table-column label="ID / 名称" min-width="130">
            <template #default="{ row }"><div class="idc"><b class="mono">{{ row.id }}</b><small>{{ row.name }}</small></div></template>
          </el-table-column>
          <el-table-column label="IP 地址" width="130"><template #default="{ row }"><span class="mono c-cyan">{{ row.ip }}</span></template></el-table-column>
          <el-table-column prop="firmware" label="固件版本" width="110"><template #default="{ row }"><span class="mono">{{ row.firmware }}</span></template></el-table-column>
          <el-table-column label="CPU 用量" min-width="140">
            <template #default="{ row }">
              <div class="cpu"><div class="cbar"><i :style="{ width: row.cpu + '%', background: barColor(row.cpu) }"></i></div><span class="mono" :class="{ 'c-danger': row.cpu > 90 }">{{ row.cpu }}%</span></div>
            </template>
          </el-table-column>
          <el-table-column prop="mem" label="内存" width="100"><template #default="{ row }"><span class="mono">{{ row.mem }}</span></template></el-table-column>
          <el-table-column label="温度" width="80"><template #default="{ row }"><span class="mono" :class="{ 'c-danger': row.temp > 75 }">{{ row.temp }}°C</span></template></el-table-column>
          <el-table-column label="网络延迟" width="90"><template #default="{ row }"><span class="mono" :class="row.latency > 100 ? 'c-danger' : 'c-success'">{{ row.latency }}ms</span></template></el-table-column>
        </el-table>
      </IndustrialPanel>

      <IndustrialPanel v-if="current" class="detail">
        <template #header>
          <div class="dh">
            <div><strong class="mono">{{ current.id }}</strong><span v-if="current.cpu > 90" class="qa-tag danger">CPU 过载</span></div>
            <el-icon v-if="current.status === 'danger'" class="c-danger"><WarningFilled /></el-icon>
          </div>
        </template>
        <p class="sub-info mono">{{ current.ip }} | 运行时间:{{ current.uptime }}</p>

        <div class="sect">实时资源趋势(近 15 分钟)</div>
        <BaseChart :option="resOption" height="160px" />

        <div class="sect">核心进程状态</div>
        <div class="proc" v-for="p in current.procs" :key="p.name">
          <span class="mono">{{ p.name }}</span>
          <b class="mono" :class="p.tone">{{ p.value }}</b>
        </div>

        <div class="sect">远程维护操作</div>
        <div class="ops">
          <el-button :icon="Upload">远程升级</el-button>
          <el-button :icon="Document">查看日志</el-button>
        </div>
        <el-button type="danger" plain class="reboot" :icon="RefreshRight" @click="reboot">强制重启设备</el-button>
      </IndustrialPanel>
    </section>
  </div>
</template>

<script setup>
// 边缘盒子:统计卡 + 监查列表 + 详情(资源趋势/进程/远程运维);edgeBoxApi 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Connection, Cpu, WarningFilled, Search, Filter, Upload, Document, RefreshRight } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'
import { edgeBoxApi } from '@/api'

const stat = ref({ total: 1248, onlineRate: 98.5, cpuAlarm: 3, backlog: '14.2k' })

const procsA = [{ name: 'edge_infer_engine', value: '12% CPU', tone: 'c-success' }, { name: 'video_stream_mux', value: '0.5% CPU', tone: 'c-cyan' }, { name: 'sensor_data_agg', value: '0.1% CPU', tone: 'c-cyan' }, { name: 'mqtt_client_pub', value: '运行中', tone: 'c-success' }]
const procsB = [{ name: 'edge_infer_engine', value: '94.2% CPU', tone: 'c-danger' }, { name: 'video_stream_mux', value: '0.5% CPU', tone: 'c-cyan' }, { name: 'sensor_data_agg', value: '0.1% CPU', tone: 'c-cyan' }, { name: 'mqtt_client_pub', value: '等待中', tone: 'c-warning' }]

const rows = ref([
  { id: 'EB-202-A1', name: '主机房 A侧', ip: '192.168.10.45', firmware: 'v2.4.1-stable', cpu: 24, mem: '4GB (8.6G)', temp: 42, latency: 12, status: 'online', uptime: '45d 12h', procs: procsA },
  { id: 'EB-105-B1', name: '1号塔吊 机柜侧', ip: '192.168.12.11', firmware: 'v2.4.1-stable', cpu: 99, mem: '6GB (7.6G)', temp: 82, latency: 210, status: 'danger', uptime: '45d 12h', procs: procsB },
])
const current = ref(null)
const kw = ref('')
const filteredRows = computed(() => rows.value.filter(r => !kw.value || r.id.includes(kw.value) || r.ip.includes(kw.value)))

function toneOf(s) { return { online: 'c-success', danger: 'c-danger', offline: 'c-muted' }[s] || 'c-muted' }
function barColor(v) { return v > 90 ? '#ef4444' : v > 60 ? '#eab308' : '#22d3ee' }

const resOption = computed(() => ({
  grid: { top: 24, left: 30, right: 12, bottom: 20 },
  tooltip: { trigger: 'axis' },
  legend: { data: ['CPU', '内存'], textStyle: { color: '#8ba3c2' }, right: 0, top: 0, itemWidth: 10, itemHeight: 6 },
  xAxis: { type: 'category', data: Array.from({ length: 15 }, (_, i) => i), show: false, boundaryGap: false },
  yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: 'rgba(30,58,92,.4)' } }, axisLabel: { color: '#55708f', fontSize: 10 } },
  series: [
    { name: 'CPU', type: 'line', smooth: true, symbol: 'none', data: current.value?.status === 'danger' ? [40, 55, 45, 80, 60, 70, 55, 40, 30, 25, 20, 18, 15, 12, 10] : [22, 25, 20, 24, 21, 23, 22, 24, 20, 22, 24, 21, 23, 22, 24], lineStyle: { color: '#ef4444', width: 2 }, itemStyle: { color: '#ef4444' } },
    { name: '内存', type: 'line', smooth: true, symbol: 'none', data: [70, 68, 66, 64, 62, 60, 58, 55, 52, 50, 48, 46, 45, 44, 43], lineStyle: { color: '#22d3ee', width: 2 }, itemStyle: { color: '#22d3ee' } },
  ],
}))

async function reboot() {
  await ElMessageBox.confirm('确认强制重启该边缘设备?重启期间将短暂中断数据采集。', '强制重启', { type: 'warning' })
  ElMessage.success('已下发重启指令')
}

onMounted(async () => {
  try {
    const res = await edgeBoxApi.list({ page: 1, page_size: 100 })
    // 后端字段(version/cpu_percent/mem_percent/temperature)映射为页面字段,缺省时补演示值
    if (res?.list?.length) rows.value = res.list.map((r, i) => {
      const cpu = r.cpu ?? r.cpu_percent ?? (18 + (i * 13) % 60)
      const status = r.status === 'fault' || cpu > 90 ? 'danger' : (r.status || 'online')
      return {
        id: r.code || r.id, name: r.name || `边缘盒 ${i + 1}#`, ip: r.ip || `192.168.10.${40 + i}`,
        firmware: r.version || r.firmware || 'v2.4.1-stable', cpu,
        mem: r.mem || (r.mem_percent != null ? `${Math.round(r.mem_percent * 0.08 * 10) / 10}GB (8G)` : `${4 + (i % 3)}GB (8G)`),
        temp: r.temp ?? r.temperature ?? (38 + (i * 7) % 30),
        latency: r.latency ?? (10 + (i * 11) % 90),
        status, uptime: r.uptime || `${20 + (i * 9) % 60}d ${(i * 5) % 24}h`,
        procs: status === 'danger' ? procsB : procsA,
      }
    })
  } catch { /* 回退演示数据 */ }
  current.value = rows.value.find(r => r.status === 'danger') || rows.value[0] || null
})
</script>

<style scoped>
.stat-row.four { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.body-grid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 14px; align-items: stretch; }
.body-grid > .panel { display: flex; flex-direction: column; }
.body-grid > .panel :deep(.body) { flex: 1; }
.toolbar { display: flex; gap: 8px; }
.idc { display: flex; flex-direction: column; }
.idc small { font-size: 11px; color: var(--qa-text-muted); }
.cpu { display: flex; align-items: center; gap: 8px; }
.cbar { flex: 1; height: 6px; border-radius: 3px; background: var(--qa-panel-2); overflow: hidden; }
.cbar i { display: block; height: 100%; }

.dh { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.dh div { display: flex; align-items: center; gap: 8px; }
.dh strong { font-size: 16px; }
.sub-info { margin: 0 0 14px; font-size: 12px; color: var(--qa-text-2); }
.sect { margin: 16px 0 10px; font-size: 13px; font-weight: 600; color: var(--qa-cyan); }
.proc { display: flex; justify-content: space-between; padding: 9px 12px; margin-bottom: 6px; font-size: 12px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.ops { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.ops .el-button { margin: 0; }
.reboot { width: 100%; margin-top: 10px; }

@media (max-width: 1200px) { .stat-row.four { grid-template-columns: repeat(2, 1fr); } .body-grid { grid-template-columns: 1fr; } }
</style>
