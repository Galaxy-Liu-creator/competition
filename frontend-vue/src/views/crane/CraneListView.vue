<template>
  <div class="page crane-list">
    <!-- 统计卡 -->
    <section class="stat-row four">
      <StatCard label="设备总数" :value="stat.total" suffix="台" :icon="Van" accent="#3b82f6" />
      <StatCard label="在线率" :value="stat.onlineRate" suffix="%" :icon="Connection" accent="#22c55e" />
      <StatCard label="作业中" :value="stat.working" suffix="台" :icon="Refresh" accent="#22d3ee" />
      <StatCard label="高风险告警" :value="stat.highRisk" suffix="项" :icon="WarningFilled" accent="#ef4444" />
    </section>

    <section class="body-grid page-fill">
      <!-- 左:工具栏 + 表格 -->
      <IndustrialPanel class="list-panel">
        <template #header>
          <div class="toolbar">
            <el-input v-model="keyword" placeholder="搜索 ID 或名称…" :prefix-icon="Search" clearable class="search" />
            <el-select v-model="statusFilter" placeholder="状态:全部" clearable class="sel">
              <el-option label="状态:全部" value="" />
              <el-option label="正常运行" value="normal" />
              <el-option label="一般预警" value="warning" />
              <el-option label="严重故障" value="danger" />
              <el-option label="离线" value="offline" />
            </el-select>
            <el-select v-model="areaFilter" placeholder="作业区:全部" clearable class="sel">
              <el-option label="作业区:全部" value="" />
              <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
            </el-select>
            <el-button type="primary" :icon="Plus" @click="openDialog()">新增吊车</el-button>
          </div>
        </template>

        <el-table
          :data="pagedRows" highlight-current-row row-key="id"
          @current-change="handleSelect" :current-row-key="current?.id"
        >
          <el-table-column label="状态" width="60">
            <template #default="{ row }">
              <span class="status-dot" :class="toneClass(row.risk)"></span>
            </template>
          </el-table-column>
          <el-table-column label="吊车 ID / 名称" min-width="160">
            <template #default="{ row }">
              <div class="idcell">
                <b class="mono c-blue">{{ row.id }}</b>
                <small>{{ row.name }}</small>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="model" label="型号" width="110" />
          <el-table-column prop="area" label="作业区" width="120" />
          <el-table-column label="风险状态" width="110">
            <template #default="{ row }">
              <span class="qa-tag" :class="toneClass(row.risk)">{{ riskLabel(row.risk) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="关联设备" width="120">
            <template #default="{ row }">
              <div class="dev-icons">
                <el-icon v-for="(d, i) in row.devices" :key="i" :class="'c-' + d.tone"><component :is="d.icon" /></el-icon>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pager">
          <el-pagination
            layout="prev, pager, next" background small
            :total="filteredRows.length" :page-size="pageSize"
            v-model:current-page="page"
          />
        </div>
      </IndustrialPanel>

      <!-- 右:详情 -->
      <IndustrialPanel v-if="current" class="detail">
        <template #header>
          <div class="dhead">
            <el-icon class="dico"><Van /></el-icon>
            <div>
              <strong class="mono">{{ current.id }}</strong>
              <span class="wstate"><i class="status-dot" :class="toneClass(current.risk)"></i>工作状态:{{ current.workState }}</span>
            </div>
            <el-icon class="close" @click="current = null"><Close /></el-icon>
          </div>
        </template>

        <div class="meta">
          <div><span>型号</span><b>{{ current.model }}</b></div>
          <div><span>安装日期</span><b class="mono">{{ current.installDate }}</b></div>
          <div><span>制造商</span><b>{{ current.maker }}</b></div>
        </div>

        <div class="sub-title">实时监测</div>
        <div class="mon">
          <div class="mrow">
            <span>当前载重</span>
            <b class="mono c-gold">{{ current.load }} t / {{ current.loadMax }} t</b>
          </div>
          <div class="bar"><i class="gold" :style="{ width: (current.load / current.loadMax * 100) + '%' }"></i></div>
          <div class="mrow">
            <span>吊钩高度</span>
            <b class="mono c-gold">{{ current.hookHeight }} m</b>
          </div>
          <div class="bar"><i class="blue" :style="{ width: (current.hookHeight / 80 * 100) + '%' }"></i></div>
        </div>

        <div class="mini-cards">
          <div class="mini">
            <el-icon><RefreshRight /></el-icon>
            <b class="mono">{{ current.rotation }}°</b>
            <span>回转角度</span>
          </div>
          <div class="mini">
            <el-icon><WindPower /></el-icon>
            <b class="mono">{{ current.wind }} m/s</b>
            <span>当前风速</span>
          </div>
        </div>

        <div class="sub-title">关联设备</div>
        <div class="link-list">
          <div v-for="d in current.linked" :key="d.name" class="link">
            <el-icon :class="'c-' + d.tone"><component :is="d.icon" /></el-icon>
            <span>{{ d.name }}</span>
            <i class="status-dot" :class="'c-' + d.tone"></i>
          </div>
        </div>

        <el-button class="track-btn" type="primary" plain :icon="Location" @click="openTrack">查看作业轨迹</el-button>
      </IndustrialPanel>
    </section>

    <!-- 作业轨迹弹窗 -->
    <el-dialog v-model="trackDialog" :title="`作业轨迹 · ${current?.id || ''}`" width="640px">
      <div class="track-meta">
        <span>作业区:<b>{{ current?.area }}</b></span>
        <span>轨迹时段:<b class="mono">08:00 - 10:45</b></span>
        <span>吊装循环:<b class="mono">{{ trackPoints.length }} 次</b></span>
      </div>
      <div class="track-map">
        <svg viewBox="0 0 560 300">
          <!-- 网格 -->
          <line v-for="i in 6" :key="'h' + i" class="grid" x1="0" :y1="i * 50 - 25" x2="560" :y2="i * 50 - 25" />
          <line v-for="i in 11" :key="'v' + i" class="grid" :x1="i * 50 - 25" y1="0" :x2="i * 50 - 25" y2="300" />
          <!-- 轨迹 -->
          <polyline class="path" :points="trackPath" />
          <g v-for="(p, i) in trackPoints" :key="i">
            <circle :cx="p.x" :cy="p.y" r="5" class="pt" :class="{ start: i === 0, end: i === trackPoints.length - 1 }" />
            <text :x="p.x + 9" :y="p.y - 8" class="pt-time mono">{{ p.time }}</text>
          </g>
        </svg>
      </div>
      <div class="track-legend">
        <span><i class="lg start"></i>起始位置</span>
        <span><i class="lg mid"></i>吊装停留点</span>
        <span><i class="lg end"></i>当前位置</span>
      </div>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialog" :title="form.id ? '编辑吊车' : '新增吊车'" width="480px">
      <el-form :model="form" label-width="88px">
        <el-form-item label="吊车 ID"><el-input v-model="form.id" :disabled="editing" placeholder="如 CR-8012" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="型号"><el-input v-model="form.model" /></el-form-item>
        <el-form-item label="作业区"><el-input v-model="form.area" /></el-form-item>
        <el-form-item label="制造商"><el-input v-model="form.maker" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 吊车管理:统计卡 + 表格 + 详情侧栏 + 新增/编辑;craneApi 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Van, Connection, Refresh, WarningFilled, Search, Plus, Close,
  RefreshRight, WindPower, Cpu, VideoCamera, Odometer, Microphone, Location,
} from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { craneApi } from '@/api'

const stat = ref({ total: 142, onlineRate: 94.5, working: 87, highRisk: 3 })

const demoDevices = [
  [{ icon: Cpu, tone: 'cyan' }, { icon: VideoCamera, tone: 'cyan' }, { icon: Odometer, tone: 'success' }],
  [{ icon: Cpu, tone: 'gold' }, { icon: VideoCamera, tone: 'gold' }],
  [{ icon: VideoCamera, tone: 'danger' }],
  [{ icon: Cpu, tone: 'muted' }],
]

const rows = ref([
  { id: 'CR-8012', name: '1号塔式起重机', model: 'TC6015', area: 'A区-东侧', risk: 'normal', workState: '正常运行',
    installDate: '2021-04-12', maker: '中联重科', load: 12.4, loadMax: 20.8, hookHeight: 45.2, rotation: 184, wind: 5.2,
    devices: demoDevices[0],
    linked: [{ name: '边缘计算盒 E-12', icon: Cpu, tone: 'success' }, { name: '球机摄像头 C-04', icon: VideoCamera, tone: 'success' }] },
  { id: 'CR-8015', name: '2号履带吊', model: 'QYS6K', area: 'B区-西侧', risk: 'warning', workState: '预警运行',
    installDate: '2020-09-01', maker: '徐工集团', load: 8.2, loadMax: 25, hookHeight: 32.6, rotation: 96, wind: 6.1,
    devices: demoDevices[1],
    linked: [{ name: '边缘计算盒 E-15', icon: Cpu, tone: 'warning' }, { name: '云台摄像头 C-08', icon: VideoCamera, tone: 'warning' }] },
  { id: 'CR-7022', name: '龙门式起重机', model: 'MG40', area: '堆场区', risk: 'danger', workState: '故障停机',
    installDate: '2019-12-20', maker: '三一重工', load: 0, loadMax: 40, hookHeight: 0, rotation: 0, wind: 4.8,
    devices: demoDevices[2],
    linked: [{ name: '球机摄像头 C-11', icon: VideoCamera, tone: 'danger' }] },
  { id: 'CR-8018', name: '3号塔式起重机', model: 'TC6015', area: 'A区-北侧', risk: 'offline', workState: '离线',
    installDate: '2022-03-08', maker: '中联重科', load: 0, loadMax: 20.8, hookHeight: 0, rotation: 0, wind: 0,
    devices: demoDevices[3],
    linked: [{ name: '边缘计算盒 E-18', icon: Cpu, tone: 'muted' }] },
])

const current = ref(null)
const keyword = ref('')
const statusFilter = ref('')
const areaFilter = ref('')
const page = ref(1)
const pageSize = 10

const areas = computed(() => [...new Set(rows.value.map(r => r.area))])
const filteredRows = computed(() => rows.value.filter(r =>
  (!keyword.value || r.id.includes(keyword.value) || r.name.includes(keyword.value)) &&
  (!statusFilter.value || r.risk === statusFilter.value) &&
  (!areaFilter.value || r.area === areaFilter.value)
))
const pagedRows = computed(() => filteredRows.value.slice((page.value - 1) * pageSize, page.value * pageSize))

function toneClass(risk) {
  return { normal: 'c-success success', warning: 'c-warning warning', danger: 'c-danger danger', offline: 'c-muted info' }[risk] || 'info'
}
function riskLabel(risk) {
  return { normal: '正常运行', warning: '一般预警', danger: '严重故障', offline: '离线' }[risk] || risk
}
function handleSelect(row) { if (row) current.value = row }

// 作业轨迹:按吊车 ID 生成确定性演示轨迹(无后端轨迹接口时保证可演示)
const trackDialog = ref(false)
const trackPoints = computed(() => {
  if (!current.value) return []
  const seed = [...current.value.id].reduce((s, ch) => s + ch.charCodeAt(0), 0)
  const times = ['08:00', '08:35', '09:10', '09:40', '10:15', '10:45']
  return times.map((time, i) => ({
    x: Math.round(60 + ((seed * 7 + i * 89) % 440)),
    y: Math.round(48 + ((seed * 13 + i * 67) % 210)),
    time,
  }))
})
const trackPath = computed(() => trackPoints.value.map(p => `${p.x},${p.y}`).join(' '))
function openTrack() { trackDialog.value = true }

// 弹窗
const dialog = ref(false)
const editing = ref(false)
const form = ref({})
function openDialog(row) {
  editing.value = !!row
  form.value = row ? { ...row } : { id: '', name: '', model: '', area: '', maker: '' }
  dialog.value = true
}
async function save() {
  if (!form.value.id || !form.value.name) { ElMessage.warning('请填写 ID 与名称'); return }
  try {
    if (editing.value) await craneApi.update(form.value.id, form.value)
    else await craneApi.create(form.value)
  } catch { /* 无后端时本地生效 */ }
  if (editing.value) {
    const i = rows.value.findIndex(r => r.id === form.value.id)
    if (i > -1) rows.value[i] = { ...rows.value[i], ...form.value }
    ElMessage.success('已保存修改')
  } else {
    rows.value.unshift({ ...form.value, risk: 'normal', workState: '正常运行', load: 0, loadMax: 20, hookHeight: 0, rotation: 0, wind: 0, devices: [], linked: [] })
    ElMessage.success('已新增吊车')
  }
  dialog.value = false
}

onMounted(async () => {
  try {
    const res = await craneApi.list({ page: 1, page_size: 100 })
    if (res?.list?.length) {
      // 后端字段(work_zone/manufacturer/install_date/realtime)映射为页面字段,缺省时补演示值
      const riskMap = { normal: 'normal', running: 'normal', online: 'normal', warning: 'warning', danger: 'danger', fault: 'danger', offline: 'offline' }
      rows.value = res.list.map((c, i) => {
        const rt = c.realtime || {}
        const risk = riskMap[c.risk || c.status] || 'normal'
        return {
          id: c.code || c.id, name: c.name || `${i + 1}号起重机`, model: c.model || 'TC6015',
          area: c.work_zone || c.area || ['A区-东侧', 'B区-西侧', '堆场区'][i % 3],
          risk, workState: riskLabel(risk),
          installDate: c.install_date || c.installDate || '2022-03-08',
          maker: c.manufacturer || c.maker || ['中联重科', '徐工集团', '三一重工'][i % 3],
          load: rt.load ?? c.load ?? (risk === 'offline' || risk === 'danger' ? 0 : Math.round((5 + (i * 3.7) % 12) * 10) / 10),
          loadMax: rt.load_max ?? c.loadMax ?? 20.8,
          hookHeight: rt.hook_height ?? c.hookHeight ?? (risk === 'offline' ? 0 : Math.round((20 + (i * 9) % 40) * 10) / 10),
          rotation: rt.rotation ?? c.rotation ?? (risk === 'offline' ? 0 : (40 + i * 37) % 360),
          wind: rt.wind ?? c.wind ?? (risk === 'offline' ? 0 : Math.round((3 + (i * 1.3) % 5) * 10) / 10),
          devices: demoDevices[i % demoDevices.length],
          linked: [
            { name: `边缘计算盒 E-${10 + i}`, icon: Cpu, tone: risk === 'danger' ? 'danger' : risk === 'warning' ? 'warning' : 'success' },
            { name: `球机摄像头 C-0${(i % 8) + 1}`, icon: VideoCamera, tone: risk === 'offline' ? 'muted' : 'success' },
          ],
        }
      })
    }
  } catch { /* 回退演示数据 */ }
  current.value = rows.value[0] || null
})
</script>

<style scoped>
.stat-row.four { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.body-grid { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 14px; align-items: stretch; }
.body-grid > .panel { display: flex; flex-direction: column; }
.body-grid > .panel :deep(.body) { flex: 1; }

.toolbar { display: flex; gap: 10px; width: 100%; padding: 8px 0; }
.toolbar .search { width: 240px; }
.toolbar .sel { width: 140px; }
.toolbar .el-button { margin-left: auto; }

.idcell { display: flex; flex-direction: column; }
.idcell small { color: var(--qa-text-muted); font-size: 12px; }
.dev-icons { display: flex; gap: 8px; font-size: 16px; }
.pager { display: flex; justify-content: flex-end; padding: 12px 4px 4px; }

/* 详情 */
.detail :deep(header) { align-items: flex-start; padding: 12px 14px; }
.dhead { display: flex; gap: 10px; width: 100%; }
.dico { font-size: 22px; color: var(--qa-blue); padding: 8px; background: var(--qa-blue-dim); border-radius: 8px; }
.dhead strong { display: block; font-size: 16px; }
.wstate { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--qa-text-2); margin-top: 4px; }
.close { margin-left: auto; cursor: pointer; color: var(--qa-text-muted); }
.close:hover { color: var(--qa-text); }

.meta { display: grid; gap: 10px; padding-bottom: 14px; border-bottom: 1px solid var(--qa-border); }
.meta div { display: flex; justify-content: space-between; font-size: 13px; }
.meta span { color: var(--qa-text-2); }
.sub-title { margin: 14px 0 10px; font-size: 13px; font-weight: 600; color: var(--qa-cyan); }
.mrow { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 12px; color: var(--qa-text-2); }
.mon .bar { height: 8px; border-radius: 4px; background: var(--qa-panel-2); overflow: hidden; margin-bottom: 12px; }
.mon .bar i { display: block; height: 100%; border-radius: 4px; }
.mon .bar i.gold { background: var(--qa-gold); }
.mon .bar i.blue { background: var(--qa-blue); }

.mini-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.mini { display: grid; place-items: center; gap: 4px; padding: 14px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.mini .el-icon { font-size: 18px; color: var(--qa-cyan); }
.mini b { font-size: 20px; }
.mini span { font-size: 11px; color: var(--qa-text-muted); }

.link-list { display: flex; flex-direction: column; gap: 8px; }
.link { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); font-size: 13px; }
.link i { margin-left: auto; }
.track-btn { width: 100%; margin-top: 14px; }

/* 作业轨迹弹窗 */
.track-meta { display: flex; gap: 24px; margin-bottom: 12px; font-size: 13px; color: var(--qa-text-2); }
.track-meta b { color: var(--qa-text); margin-left: 4px; }
.track-map { border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); overflow: hidden; }
.track-map svg { display: block; width: 100%; }
.track-map .grid { stroke: var(--qa-border); stroke-width: .5; opacity: .6; }
.track-map .path { fill: none; stroke: var(--qa-cyan); stroke-width: 2; stroke-dasharray: 6 4; }
.track-map .pt { fill: var(--qa-blue); }
.track-map .pt.start { fill: var(--qa-success); }
.track-map .pt.end { fill: var(--qa-danger); }
.track-map .pt-time { font-size: 10px; fill: var(--qa-text-muted); }
.track-legend { display: flex; gap: 18px; margin-top: 10px; font-size: 12px; color: var(--qa-text-2); }
.track-legend span { display: inline-flex; align-items: center; gap: 6px; }
.track-legend .lg { width: 8px; height: 8px; border-radius: 50%; }
.track-legend .lg.start { background: var(--qa-success); }
.track-legend .lg.mid { background: var(--qa-blue); }
.track-legend .lg.end { background: var(--qa-danger); }

@media (max-width: 1200px) {
  .stat-row.four { grid-template-columns: repeat(2, 1fr); }
  .body-grid { grid-template-columns: 1fr; }
}
</style>
