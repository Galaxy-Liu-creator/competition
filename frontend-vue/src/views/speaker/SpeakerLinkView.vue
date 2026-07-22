<template>
  <div class="page">
    <div class="link-main">
      <!-- 左:设备池 -->
      <IndustrialPanel title="设备池" class="pool">
        <template #extra><el-icon><Search /></el-icon></template>
        <el-input v-model="poolKw" placeholder="搜索设备 ID / 名称..." size="small" class="pool-search" />
        <div class="group-title">吊车 (CRANES) <b>{{ cranes.length }}</b></div>
        <div v-for="c in cranes" :key="c.id" class="pool-item crane" :class="{ active: c.id === current.id }" @click="selectCrane(c)">
          <el-icon><Tools /></el-icon><span>{{ c.name }}</span>
          <i class="status-dot" :class="c.online ? 'c-success' : 'c-danger'" />
        </div>
        <div class="group-title">音柱 (SPEAKERS) <b>{{ speakers.length }}</b></div>
        <label v-for="s in speakers" :key="s.id" class="pool-item spk" :class="{ checked: picked.includes(s.id) }">
          <el-checkbox :model-value="picked.includes(s.id)" @change="togglePick(s.id)" />
          <el-icon><Bell /></el-icon><span>{{ s.name }}</span>
        </label>
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
            <div v-for="s in linkedSpeakers" :key="s.id" class="node spk"><el-icon><Bell /></el-icon><label>{{ s.name }}</label></div>
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
          <el-button @click="ElMessage.success('已发起播报试听')">◎ 播放试听</el-button>
          <el-button type="primary" @click="applyConfig">应用关联配置</el-button>
        </div>
      </IndustrialPanel>
    </div>

    <!-- 底:关联历史 -->
    <IndustrialPanel title="关联历史">
      <template #extra><a>导出记录</a></template>
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
import { speakerLinkApi } from '@/api'

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
const links = reactive({ 'CR-12': ['SPK-001'] })

const history = ref([
  { time: '2023-10-27 14:22:09', operator: '管理员 (Admin)', action: '建立关联', detail: 'CR-12-Tower ↔ SPK-Z1-001 (优先级 3)', ok: true },
  { time: '2023-10-27 14:30:12', operator: '管理员 (Admin)', action: '建立关联', detail: 'CR-12-Tower ↔ SPK-Z1-010 (优先级 3)', ok: true },
  { time: '2023-10-27 09:15:00', operator: '系统任务', action: '解除关联', detail: 'CR-08-Heavy ↔ SPK-Z2-099 (设备离线)', ok: false },
])

const linkedSpeakers = computed(() => (links[current.value.id] || []).map(id => speakers.value.find(s => s.id === id)).filter(Boolean))
const pendingSpeaker = computed(() => { const id = picked.value.find(p => !(links[current.value.id] || []).includes(p)); return id ? speakers.value.find(s => s.id === id) : null })

function selectCrane(c) { current.value = c; picked.value = [] }
function togglePick(id) { const i = picked.value.indexOf(id); i > -1 ? picked.value.splice(i, 1) : picked.value.push(id) }

async function doLink() {
  try { for (const sid of picked.value) await speakerLinkApi.create({ crane_id: current.value.id, speaker_id: sid }) } catch { /* 演示忽略 */ }
  links[current.value.id] = Array.from(new Set([...(links[current.value.id] || []), ...picked.value]))
  history.value.unshift({ time: new Date().toLocaleString('zh-CN'), operator: '管理员 (Admin)', action: '建立关联', detail: `${current.value.name} ↔ ${picked.value.join('、')}`, ok: true })
  ElMessage.success(`已关联 ${picked.value.length} 个音柱`)
  picked.value = []
}
function applyConfig() { ElMessage.success(`已应用关联配置(优先级 L${prio.value})`) }
onMounted(async () => { try { const r = await speakerLinkApi.list({ page: 1, page_size: 20 }); if (r.list?.length) history.value = r.list } catch { /* keep demo */ } })
</script>

<style scoped>
.link-main { display: grid; grid-template-columns: 300px minmax(0, 1fr) 300px; gap: 16px; }
.pool-search { margin-bottom: 10px; }
.group-title { display: flex; justify-content: space-between; font-size: 11px; color: var(--qa-text-muted); letter-spacing: .05em; margin: 12px 0 8px; }
.pool-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; margin-bottom: 6px; border: 1px solid var(--qa-border); border-radius: 6px; cursor: pointer; font-size: 13px; }
.pool-item .status-dot { margin-left: auto; }
.pool-item.active { border-color: var(--qa-border-active); background: var(--qa-panel-3); }
.pool-item.checked { border-color: var(--qa-cyan); background: var(--qa-cyan-dim); }
.batch-btn { width: 100%; margin-top: 14px; }
.canvas { position: relative; min-height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 40px; }
.grid-bg { position: absolute; inset: 0; background-image: radial-gradient(rgba(56,119,157,.2) 1px, transparent 1px); background-size: 22px 22px; }
.center-node, .node { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 18px; border: 1px solid var(--qa-cyan); border-radius: 8px; background: var(--qa-panel-2); font-size: 12px; }
.center-node .el-icon, .node .el-icon { font-size: 22px; color: var(--qa-cyan); }
.center-node { box-shadow: 0 0 18px rgba(34,211,238,.25); }
.linked-row { display: flex; gap: 32px; z-index: 2; }
.node.pending { border-style: dashed; opacity: .8; }
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
.p-actions { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
@media (max-width: 1200px) { .link-main { grid-template-columns: 1fr; } .canvas { min-height: 320px; } }
</style>
