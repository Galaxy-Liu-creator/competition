<template>
  <div class="page">
    <div class="link-main">
      <!-- 左:设备池 -->
      <IndustrialPanel title="设备池" class="pool">
        <template #extra><el-icon><Search /></el-icon></template>
        <el-input v-model="poolKw" placeholder="搜索设备 ID / 名称..." size="small" class="pool-search" clearable />
        <div class="group-title">吊车 (CRANES) <b>{{ filteredCranes.length }}</b></div>
        <div v-for="c in filteredCranes" :key="c.id" class="pool-item crane" :class="{ active: c.id === current.id }" @click="selectCrane(c)">
          <el-icon><Tools /></el-icon><span>{{ c.name }}</span>
          <i class="status-dot" :class="c.online ? 'c-success' : 'c-danger'" />
        </div>
        <p v-if="!filteredCranes.length" class="pool-empty">无匹配吊车</p>
        <div class="group-title">音柱 (SPEAKERS) <b>{{ filteredSpeakers.length }}</b></div>
        <label v-for="s in filteredSpeakers" :key="s.id" class="pool-item spk" :class="{ checked: picked.includes(s.id) }">
          <el-checkbox :model-value="picked.includes(s.id)" @change="togglePick(s.id)" />
          <el-icon><Bell /></el-icon><span>{{ s.name }}</span>
        </label>
        <p v-if="!filteredSpeakers.length" class="pool-empty">无匹配音柱</p>
        <el-button type="primary" class="batch-btn" :disabled="!picked.length" @click="doLink">
          <el-icon><Connection /></el-icon>&nbsp;批量关联(已选 {{ picked.length }})
        </el-button>
      </IndustrialPanel>

      <!-- 中:绑定拓扑 -->
      <IndustrialPanel title="绑定拓扑" class="topo">
        <template #extra><span class="legend"><i class="solid" />已连接&nbsp;&nbsp;<i class="dash" />待连接</span></template>
        <div class="canvas">
          <div class="grid-bg" />
          <div class="center-node"><el-icon><Tools /></el-icon><label>{{ current.name }}</label></div>
          <div class="linked-row">
            <div v-for="s in linkedSpeakers" :key="s.id" class="node spk">
              <i class="unlink" title="解除关联" @click.stop="unlink(s)">✕</i>
              <el-icon><Bell /></el-icon><label>{{ s.name }}</label>
            </div>
          </div>
          <div v-if="pendingSpeaker" class="node pending"><el-icon><Bell /></el-icon><label>待关联 {{ pendingSpeaker.name }}</label></div>
          <p v-if="!linkedSpeakers.length && !pendingSpeaker" class="empty-hint">暂无关联音柱,请在左侧勾选后批量关联</p>
        </div>
      </IndustrialPanel>

      <!-- 右:配置属性 -->
      <IndustrialPanel title="配置属性" class="props">
        <div class="p-label">当前操作对象</div>
        <div class="target-card"><el-icon><Tools /></el-icon><div><b>{{ current.name }}</b><small>{{ current.zone || 'A区 / 重吊塔吊' }}</small></div></div>
        <div class="p-label">播报优先级</div>
        <div class="prio"><span>L1</span><el-slider v-model="prio" :min="1" :max="4" :step="1" /><span>L4</span></div>
        <p class="tip">高优先级将在告警时抢占播报队列。</p>
        <div class="p-label">联动音警触发</div>
        <el-checkbox v-model="triggers.overload">超载报警 (Overload)</el-checkbox>
        <el-checkbox v-model="triggers.wind">大风报警 (High Wind)</el-checkbox>
        <el-checkbox v-model="triggers.fence">越界报警 (Geofence)</el-checkbox>
        <div class="p-actions">
          <el-button :loading="playing" @click="playPreview">{{ playing ? '播报中…' : '◎ 播放试听' }}</el-button>
          <el-button type="primary" @click="applyConfig">应用关联配置</el-button>
        </div>
      </IndustrialPanel>
    </div>

    <!-- 底:关联历史 -->
    <IndustrialPanel title="关联历史">
      <template #extra><a class="export-link" @click="onExportHistory">导出记录</a></template>
      <el-table :data="history" height="200">
        <el-table-column prop="time" label="操作时间" width="180"><template #default="{ row }"><span class="mono">{{ row.time }}</span></template></el-table-column>
        <el-table-column prop="operator" label="操作人" width="160" />
        <el-table-column label="动作" width="120"><template #default="{ row }"><span :class="row.action === '解除关联' ? 'c-danger' : 'c-cyan'">{{ row.action }}</span></template></el-table-column>
        <el-table-column prop="detail" label="详情描述" min-width="240" />
        <el-table-column label="状态" width="90" align="right"><template #default="{ row }"><span class="qa-tag" :class="row.ok ? 'success' : 'danger'">{{ row.ok ? '成功' : '失败' }}</span></template></el-table-column>
      </el-table>
    </IndustrialPanel>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Tools, Bell, Connection } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { configApi } from '@/api'
import { exportExcel } from '@/utils/exportExcel'

// 本页为演示型本地数据模型:关联关系/配置/历史均持久化到 localStorage
const LINKS_KEY = 'qa-speaker-links'
const CONFIG_KEY = 'qa-speaker-link-config'
const HISTORY_KEY = 'qa-speaker-link-history'

const poolKw = ref('')
const cranes = ref([
  { id: 'CR-08', name: 'CR-08-Heavy', online: true, zone: 'A区 / 重吊塔吊' },
  { id: 'CR-12', name: 'CR-12-Tower', online: true, zone: 'A区 / 直臂塔吊' },
  { id: 'CR-15', name: 'CR-15-Gantry', online: false, zone: 'B区 / 龙门吊' },
])
const speakers = ref([
  { id: 'SPK-001', name: 'SPK-Z1-001' },
  { id: 'SPK-045', name: 'SPK-Z1-045' },
  { id: 'SPK-112', name: 'SPK-Z2-112' },
])
const current = ref(cranes.value[1])
const picked = ref(['SPK-045'])
const prio = ref(1)
const triggers = reactive({ overload: true, wind: true, fence: false })
const links = reactive({ 'CR-08': ['SPK-112'], 'CR-12': ['SPK-001', 'SPK-045'], 'CR-15': ['SPK-045'] })
const configs = reactive({})
const playing = ref(false)

const history = ref([
  { time: '2026-07-20 14:22:09', operator: '管理员 (Admin)', action: '建立关联', detail: 'CR-12-Tower ↔ SPK-Z1-001 (优先级 L3)', ok: true },
  { time: '2026-07-20 14:30:12', operator: '管理员 (Admin)', action: '建立关联', detail: 'CR-12-Tower ↔ SPK-Z1-045 (优先级 L3)', ok: true },
  { time: '2026-07-20 09:15:00', operator: '系统任务', action: '解除关联', detail: 'CR-08-Heavy ↔ SPK-Z2-099 (设备离线)', ok: false },
])

const kwMatch = (item) => {
  const kw = poolKw.value.trim().toLowerCase()
  return !kw || `${item.id} ${item.name}`.toLowerCase().includes(kw)
}
const filteredCranes = computed(() => cranes.value.filter(kwMatch))
const filteredSpeakers = computed(() => speakers.value.filter(kwMatch))

const linkedSpeakers = computed(() => (links[current.value.id] || []).map(id => speakers.value.find(s => s.id === id)).filter(Boolean))
const pendingSpeaker = computed(() => { const id = picked.value.find(p => !(links[current.value.id] || []).includes(p)); return id ? speakers.value.find(s => s.id === id) : null })

// ---------- 本地持久化 ----------
function readJson(key) {
  try { return JSON.parse(localStorage.getItem(key)) } catch { return null }
}
function persist() {
  localStorage.setItem(LINKS_KEY, JSON.stringify(links))
  localStorage.setItem(CONFIG_KEY, JSON.stringify(configs))
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value.slice(0, 100)))
}
function restore() {
  const savedLinks = readJson(LINKS_KEY)
  if (savedLinks) Object.assign(links, savedLinks)
  const savedConfigs = readJson(CONFIG_KEY)
  if (savedConfigs) Object.assign(configs, savedConfigs)
  const savedHistory = readJson(HISTORY_KEY)
  if (Array.isArray(savedHistory) && savedHistory.length) history.value = savedHistory
}

function pushHistory(action, detail, ok = true) {
  history.value.unshift({ time: new Date().toLocaleString('zh-CN', { hour12: false }), operator: '管理员 (Admin)', action, detail, ok })
  persist()
}

function loadCraneConfig() {
  const cfg = configs[current.value.id]
  prio.value = cfg?.prio ?? 1
  Object.assign(triggers, { overload: true, wind: true, fence: false, ...(cfg?.triggers || {}) })
}

function selectCrane(c) { current.value = c; picked.value = []; loadCraneConfig() }
function togglePick(id) { const i = picked.value.indexOf(id); i > -1 ? picked.value.splice(i, 1) : picked.value.push(id) }

function doLink() {
  const names = picked.value.map(id => speakers.value.find(s => s.id === id)?.name || id)
  links[current.value.id] = Array.from(new Set([...(links[current.value.id] || []), ...picked.value]))
  pushHistory('建立关联', `${current.value.name} ↔ ${names.join('、')} (优先级 L${prio.value})`)
  ElMessage.success(`已关联 ${picked.value.length} 个音柱`)
  picked.value = []
}

function unlink(speaker) {
  links[current.value.id] = (links[current.value.id] || []).filter(id => id !== speaker.id)
  pushHistory('解除关联', `${current.value.name} ↔ ${speaker.name} (手动解除)`)
  ElMessage.success(`已解除与 ${speaker.name} 的关联`)
}

async function applyConfig() {
  configs[current.value.id] = { prio: prio.value, triggers: { ...triggers } }
  persist()
  try { await configApi.save('speaker_link', { ...configs }) } catch { /* 后端不可用时仅保留本地配置 */ }
  const enabled = [triggers.overload && '超载', triggers.wind && '大风', triggers.fence && '越界'].filter(Boolean)
  pushHistory('应用配置', `${current.value.name} 优先级 L${prio.value},联动触发:${enabled.join('、') || '无'}`)
  ElMessage.success(`已应用关联配置(优先级 L${prio.value})`)
}

// 播放试听:浏览器语音合成真实播报警示语
function playPreview() {
  if (!('speechSynthesis' in window)) {
    ElMessage.warning('当前浏览器不支持语音播报,已模拟下发试听指令')
    return
  }
  const enabled = [triggers.overload && '超载', triggers.wind && '大风', triggers.fence && '越界'].filter(Boolean)
  const text = `安全警示。${current.value.name} 音柱播报试听。当前联动${enabled.join('、') || '常规'}报警,优先级 ${prio.value} 级,请现场人员注意吊装作业安全。`
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'zh-CN'
  utter.rate = 1.05
  playing.value = true
  utter.onend = () => { playing.value = false }
  utter.onerror = () => { playing.value = false }
  window.speechSynthesis.cancel()
  window.speechSynthesis.speak(utter)
  ElMessage.success('已发起播报试听')
}

function onExportHistory() {
  exportExcel({
    filename: '音柱关联历史',
    sheets: [{
      name: '关联历史',
      columns: [
        { label: '操作时间', key: 'time', width: 20 },
        { label: '操作人', key: 'operator', width: 16 },
        { label: '动作', key: 'action', width: 10 },
        { label: '详情描述', key: 'detail', width: 46 },
        { label: '状态', key: (row) => (row.ok ? '成功' : '失败'), width: 8 },
      ],
      rows: history.value,
    }],
  })
  ElMessage.success(`已导出 ${history.value.length} 条关联历史`)
}

onMounted(() => { restore(); loadCraneConfig() })
</script>

<style scoped>
.link-main { display: grid; grid-template-columns: 300px minmax(0, 1fr) 300px; gap: 16px; }
.pool-search { margin-bottom: 10px; }
.group-title { display: flex; justify-content: space-between; font-size: 11px; color: var(--qa-text-muted); letter-spacing: .05em; margin: 12px 0 8px; }
.pool-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; margin-bottom: 6px; border: 1px solid var(--qa-border); border-radius: 6px; cursor: pointer; font-size: 13px; }
.pool-item .status-dot { margin-left: auto; }
.pool-item.active { border-color: var(--qa-border-active); background: var(--qa-panel-3); }
.pool-item.checked { border-color: var(--qa-cyan); background: var(--qa-cyan-dim); }
.pool-empty { margin: 0 0 6px; font-size: 12px; color: var(--qa-text-muted); text-align: center; }
.batch-btn { width: 100%; margin-top: 14px; }
.canvas { position: relative; min-height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 40px; }
.grid-bg { position: absolute; inset: 0; background-image: radial-gradient(rgba(56,119,157,.2) 1px, transparent 1px); background-size: 22px 22px; }
.center-node, .node { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 18px; border: 1px solid var(--qa-cyan); border-radius: 8px; background: var(--qa-panel-2); font-size: 12px; }
.center-node .el-icon, .node .el-icon { font-size: 22px; color: var(--qa-cyan); }
.center-node { box-shadow: 0 0 18px rgba(34,211,238,.25); }
.linked-row { display: flex; gap: 32px; z-index: 2; }
.node.pending { border-style: dashed; opacity: .8; }
.node .unlink { position: absolute; top: -8px; right: -8px; width: 18px; height: 18px; display: none; align-items: center; justify-content: center; border-radius: 50%; border: 1px solid var(--qa-danger); background: var(--qa-panel-2); color: var(--qa-danger); font-size: 10px; font-style: normal; cursor: pointer; }
.node:hover .unlink { display: flex; }
.empty-hint { position: relative; z-index: 2; color: var(--qa-text-muted); font-size: 13px; }
.legend { font-size: 11px; color: var(--qa-text-2); }
.legend i { display: inline-block; width: 16px; height: 2px; vertical-align: middle; margin-right: 4px; }
.legend .solid { background: var(--qa-cyan); }
.legend .dash { background: repeating-linear-gradient(90deg, var(--qa-text-muted) 0 4px, transparent 4px 8px); }
.p-label { font-size: 12px; color: var(--qa-text-2); margin: 14px 0 8px; }
.target-card { display: flex; align-items: center; gap: 10px; padding: 12px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.target-card .el-icon { font-size: 20px; color: var(--qa-cyan); }
.target-card b { display: block; font-size: 13px; } .target-card small { color: var(--qa-text-muted); font-size: 11px; }
.prio { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--qa-text-2); }
.prio .el-slider { flex: 1; }
.tip { font-size: 11px; color: var(--qa-text-muted); margin: 6px 0 0; }
.props :deep(.el-checkbox) { display: flex; margin: 4px 0; }
/* 两个操作按钮纵向排列:覆盖 Element Plus 相邻按钮默认 margin-left,保证左对齐等宽 */
.p-actions { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
.p-actions .el-button { width: 100%; }
.p-actions .el-button + .el-button { margin-left: 0; }
.export-link { cursor: pointer; color: var(--qa-cyan); }
.export-link:hover { text-decoration: underline; }
@media (max-width: 1200px) { .link-main { grid-template-columns: 1fr; } .canvas { min-height: 320px; } }
</style>
