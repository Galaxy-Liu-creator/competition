<template>
  <div class="page">
    <div class="head">
      <h1>录像机管理</h1>
      <div class="head-actions">
        <el-button @click="load"><el-icon><Refresh /></el-icon>&nbsp;同步设备</el-button>
        <el-button type="primary" @click="onAdd">+ 添加录像机</el-button>
      </div>
    </div>

    <div class="stat-row">
      <StatCard label="设备总数" :value="stats.total" suffix="台" accent="#22d3ee" />
      <StatCard label="在线率" :value="stats.onlineRate" suffix="%" accent="#22c55e" />
      <StatCard label="存储使用率" :value="stats.storageUsed" suffix="%" :hint="stats.storageHint" accent="#22d3ee" />
      <StatCard label="异常通道" :value="stats.abnormal" suffix="需处理" accent="#ef4444" />
    </div>

    <div class="main">
      <IndustrialPanel title="设备清单" class="list-panel">
        <template #extra>
          <el-input v-model="query.keyword" placeholder="搜索设备ID/IP..." size="small" style="width: 200px" clearable @keyup.enter="applyFilter" @clear="applyFilter" />
        </template>
        <div class="table-wrap">
          <el-table :data="list" highlight-current-row @current-change="onSelect" height="100%">
            <el-table-column label="设备ID / 名称" min-width="150">
              <template #default="{ row }">
                <b>{{ row.code }}</b><br /><small class="text-muted">{{ row.name }}</small>
              </template>
            </el-table-column>
            <el-table-column label="IP 地址" width="140">
              <template #default="{ row }"><span class="mono c-cyan">{{ row.ip }}</span></template>
            </el-table-column>
            <el-table-column label="通道 (在用/总数)" min-width="150">
              <template #default="{ row }">
                <div class="bar-cell">
                  <span class="mono">{{ row.usedCh }}/{{ row.totalCh }}</span>
                  <div class="bar"><i :style="{ width: pct(row.usedCh, row.totalCh) + '%' }" :class="{ danger: row.usedCh / row.totalCh > 0.9 }" /></div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="录像品质" width="90">
              <template #default="{ row }"><span class="mono">{{ row.totalCh >= 32 ? '4K' : '1080P' }}</span></template>
            </el-table-column>
            <el-table-column label="磁盘容量" min-width="130">
              <template #default="{ row }">
                <span class="mono" :class="{ 'c-danger': diskPct(row) > 90 }">{{ row.diskUsed }}TB / {{ row.diskTotal }}TB</span>
              </template>
            </el-table-column>
            <el-table-column label="保留时长" width="90">
              <template #default="{ row }"><span class="mono">{{ row.retain }} 天</span></template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <span class="qa-tag" :class="statusTag(row.status)">{{ statusText(row.status) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </IndustrialPanel>

      <aside class="right">
        <IndustrialPanel :title="(current?.code || 'NVR') + ' 详细信息'">
          <div v-if="current" class="detail">
            <div class="store-head"><span>存储空间分配</span><b class="mono" :class="diskPct(current) > 90 ? 'c-danger' : 'c-cyan'">{{ diskPct(current) }}% 满</b></div>
            <div class="store-bar">
              <i class="used" :style="{ width: diskPct(current) + '%' }" />
            </div>
            <div class="store-legend">
              <span><i class="dot c-cyan" />录像 (DATA)</span>
              <span><i class="dot c-danger" />系统 (SYSTEM)</span>
            </div>
            <div class="ch-title">通道视图 (在用 {{ current.usedCh }}/{{ current.totalCh }})</div>
            <div class="ch-grid">
              <span v-for="n in current.totalCh" :key="n" class="ch" :class="chClass(n, current)"
                :title="`通道 ${String(n).padStart(2, '0')} · ${chLabel(n, current)}`">{{ String(n).padStart(2, '0') }}</span>
            </div>
            <div class="ch-legend">
              <span><i class="ch mini active" />在用</span>
              <span><i class="ch mini danger" />异常</span>
              <span><i class="ch mini idle" />空闲</span>
            </div>
          </div>
          <el-empty v-else description="请选择录像机" :image-size="60" />
        </IndustrialPanel>

        <IndustrialPanel title="录像计划">
          <div class="plan">
            <div class="d-row"><span>持续录像</span><b class="mono c-cyan">00:00 - 23:59</b></div>
            <div class="d-row"><span>移动侦测</span><b class="c-success">已启用</b></div>
            <div class="d-row"><span>云端备份</span><b class="mono c-cyan">每日 02:00</b></div>
          </div>
        </IndustrialPanel>

        <IndustrialPanel title="最近日志">
          <ul class="logs">
            <li v-for="l in logs" :key="l.time"><i :class="l.color" /><div><span class="mono">{{ l.time }}</span><b>{{ l.text }}</b></div></li>
          </ul>
        </IndustrialPanel>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { nvrApi } from '@/api'

const stats = reactive({ total: 0, onlineRate: 0, storageUsed: 0, storageHint: '', abnormal: 0 })
const query = reactive({ keyword: '' })
const allRows = ref([])
const list = ref([])
const current = ref(null)

const demo = [
  { id: 1, code: 'NVR-A01', name: 'A区主存储机', ip: '192.168.10.45', usedCh: 32, totalCh: 64, diskUsed: 12, diskTotal: 16, retain: 90, status: 'online' },
  { id: 2, code: 'NVR-B02', name: 'B区高清专用', ip: '192.168.10.46', usedCh: 60, totalCh: 64, diskUsed: 15.5, diskTotal: 16, retain: 45, status: 'warning' },
  { id: 3, code: 'NVR-C03', name: '门口备用', ip: '192.168.10.47', usedCh: 16, totalCh: 32, diskUsed: 4, diskTotal: 8, retain: 30, status: 'online' },
]
const logs = [
  { time: '10:42:15', text: '通道 03 视频丢失', color: 'c-danger' },
  { time: '10:41:02', text: '通道 10 视频丢失', color: 'c-danger' },
  { time: '08:00:00', text: '系统心跳正常', color: 'c-blue' },
  { time: '02:15:30', text: '云端备份完成 (3.2GB)', color: 'c-success' },
]

const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0)
const diskPct = (r) => (r.diskTotal ? Math.round((r.diskUsed / r.diskTotal) * 100) : 0)
// 演示规则:在用通道中每第 13 路标记为异常
const chClass = (n, r) => (n <= r.usedCh ? (n % 13 === 0 ? 'danger' : 'active') : 'idle')
const chLabel = (n, r) => (n <= r.usedCh ? (n % 13 === 0 ? '信号异常' : '在用') : '空闲')
const statusTag = (s) => ({ online: 'success', warning: 'warning', offline: 'info' }[s] || 'info')
const statusText = (s) => ({ online: '在线', warning: '预警', offline: '离线' }[s] || '未知')

async function load() {
  try {
    const res = await nvrApi.list({ page: 1, page_size: 200 })
    // 后端字段(channels_*/storage_*_gb/retention_days)映射为页面字段
    allRows.value = (res.list && res.list.length)
      ? res.list.map((r) => ({
          id: r.id,
          code: r.code,
          name: r.name,
          ip: r.ip,
          usedCh: r.usedCh ?? r.channels_used ?? 0,
          totalCh: r.totalCh ?? r.channels_total ?? 16,
          diskUsed: r.diskUsed ?? Math.round((r.storage_used_gb ?? 0) / 102.4) / 10,
          diskTotal: r.diskTotal ?? Math.round((r.storage_total_gb ?? 10240) / 102.4) / 10,
          retain: r.retain ?? r.retention_days ?? 30,
          status: r.status || 'online',
        })).sort((a, b) => String(a.code).localeCompare(String(b.code)))
      : demo
  } catch { allRows.value = demo }
  refreshStats()
  applyFilter()
  // 默认选中在用通道最多的一台,保证通道视图有内容展示
  current.value = [...list.value].sort((a, b) => b.usedCh - a.usedCh)[0] || null
}

// 客户端关键词过滤:后端在线与纯前端回退两种模式下均生效
function applyFilter() {
  const kw = query.keyword.trim().toLowerCase()
  list.value = allRows.value.filter((r) =>
    !kw || `${r.code} ${r.name} ${r.ip}`.toLowerCase().includes(kw))
  if (!list.value.includes(current.value)) current.value = list.value[0] || null
}

function refreshStats() {
  const rows = allRows.value
  stats.total = rows.length
  const online = rows.filter((r) => r.status === 'online').length
  stats.onlineRate = rows.length ? Math.round((online / rows.length) * 1000) / 10 : 0
  const used = rows.reduce((n, r) => n + r.diskUsed, 0)
  const total = rows.reduce((n, r) => n + r.diskTotal, 0)
  stats.storageUsed = total ? Math.round((used / total) * 100) : 0
  stats.storageHint = `${Math.round(used * 10) / 10}TB/${Math.round(total * 10) / 10}TB`
  // 与通道视图的异常格子规则一致:每第 13 路在用通道计为异常
  stats.abnormal = rows.reduce((n, r) => n + Math.floor(r.usedCh / 13), 0)
}

const onSelect = (row) => { if (row) current.value = row }
const onAdd = () => ElMessage.info('添加录像机表单开发中')
onMounted(load)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.head h1 { margin: 0; font-size: 20px; }
.head-actions { display: flex; gap: 10px; }
/* 左侧设备清单卡片通过 flex 拉伸,与右列三卡总高保持一致 */
.main { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 16px; align-items: stretch; }
.list-panel { display: flex; flex-direction: column; }
.list-panel :deep(.body) { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.table-wrap { flex: 1; min-height: 420px; }
.right { display: flex; flex-direction: column; gap: 16px; }
.bar-cell { display: flex; align-items: center; gap: 8px; }
.bar { flex: 1; height: 5px; background: var(--qa-panel-3); border-radius: 3px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--qa-cyan); }
.bar i.danger { background: var(--qa-danger); }
.detail { display: flex; flex-direction: column; gap: 10px; }
.store-head { display: flex; justify-content: space-between; font-size: 12px; color: var(--qa-text-2); }
.store-bar { height: 8px; border-radius: 4px; background: var(--qa-danger); overflow: hidden; }
.store-bar .used { display: block; height: 100%; background: var(--qa-cyan); }
.store-legend { display: flex; gap: 16px; font-size: 11px; color: var(--qa-text-2); }
.store-legend .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: currentColor; margin-right: 5px; }
.ch-title { font-size: 12px; color: var(--qa-text-2); margin-top: 6px; }
.ch-grid { display: grid; grid-template-columns: repeat(8, 1fr); gap: 5px; }
.ch { display: flex; align-items: center; justify-content: center; aspect-ratio: 1; border-radius: 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 10px; cursor: default; }
.ch.active { background: rgba(34, 197, 94, .16); border: 1px solid rgba(34, 197, 94, .55); color: var(--qa-success); }
.ch.danger { background: rgba(239, 68, 68, .18); border: 1px solid rgba(239, 68, 68, .6); color: var(--qa-danger); }
.ch.idle { background: transparent; border: 1px dashed var(--qa-border); color: var(--qa-text-muted); }
.ch-legend { display: flex; gap: 14px; font-size: 11px; color: var(--qa-text-2); margin-top: 2px; }
.ch-legend span { display: flex; align-items: center; gap: 6px; }
.ch.mini { width: 12px; height: 12px; aspect-ratio: auto; }
.plan, .detail { font-size: 13px; }
.d-row { display: flex; justify-content: space-between; padding: 7px 0; }
.d-row span { color: var(--qa-text-2); }
.logs { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.logs li { display: flex; gap: 10px; }
.logs li i { width: 3px; border-radius: 2px; background: currentColor; }
.logs li i.c-danger { color: var(--qa-danger); } .logs li i.c-blue { color: var(--qa-blue); } .logs li i.c-success { color: var(--qa-success); }
.logs span { display: block; font-size: 11px; color: var(--qa-text-muted); }
.logs b { font-size: 13px; font-weight: 500; }
@media (max-width: 1100px) { .main { grid-template-columns: 1fr; } .table-wrap { min-height: 360px; } }
</style>
