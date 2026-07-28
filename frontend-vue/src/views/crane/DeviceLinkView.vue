<template>
  <div class="page devlink">
    <!-- 标题 + 顶部统计 -->
    <div class="head">
      <div>
        <h1>设备关联配置</h1>
        <p>当前塔吊:<b class="mono">CR-8012</b> · 最后同步时间:<b class="mono">{{ lastSync }}</b></p>
      </div>
      <div class="hstat">
        <div class="hs"><span>已关联设备</span><b class="mono c-cyan">{{ linkedNodes.length }}</b></div>
        <div class="hs"><span>待关联设备</span><b class="mono">{{ pool.length }}</b></div>
        <div class="hs danger"><span>关联冲突</span><b class="mono c-danger">{{ conflictCount }}</b></div>
        <el-button type="primary" :icon="Refresh" :loading="syncing" @click="syncNow">立即同步</el-button>
      </div>
    </div>

    <section class="grid3">
      <!-- 左:未关联设备池 -->
      <IndustrialPanel title="未关联设备池">
        <el-input v-model="kw" placeholder="搜索设备名称/型号…" :prefix-icon="Search" class="mb" />
        <div class="pool">
          <button
            v-for="d in filteredPool" :key="d.id" type="button" class="pool-item"
            :class="{ conflict: d.conflict, picked: active?.id === d.id }" @click="select(d)"
          >
            <el-icon :class="d.conflict ? 'c-danger' : 'c-cyan'"><component :is="d.icon" /></el-icon>
            <div>
              <strong class="mono">{{ d.id }}</strong>
              <small :class="{ 'c-danger': d.conflict }">{{ d.conflict ? '已绑定至 ' + d.boundTo : d.type }}</small>
            </div>
            <el-icon v-if="d.conflict" class="c-danger warn"><WarningFilled /></el-icon>
          </button>
          <el-empty v-if="!filteredPool.length" description="暂无待关联设备" :image-size="60" />
        </div>
      </IndustrialPanel>

      <!-- 中:关联拓扑视图 -->
      <IndustrialPanel title="关联拓扑视图">
        <template #extra><span class="c-muted">CR-8012 拓扑</span></template>
        <div class="topo">
          <svg class="links" viewBox="0 0 400 320" preserveAspectRatio="none">
            <line
              v-for="n in linkedNodes" :key="n.id"
              x1="200" y1="179" :x2="n.pos.left * 4" :y2="n.pos.top * 3.2"
              :class="{ weak: n.weak }" :stroke-dasharray="n.weak ? '5 5' : undefined"
            />
          </svg>
          <div class="node center">CR-8012</div>
          <button
            v-for="n in linkedNodes" :key="n.id" type="button"
            class="node" :class="[n.tone, { active: active?.id === n.id }]"
            :style="{ left: n.pos.left + '%', top: n.pos.top + '%' }"
            @click="select(n)"
          >
            <el-icon><component :is="n.icon" /></el-icon><b>{{ n.id }}</b>
            <span v-if="n.weak" class="wk">信号弱</span>
          </button>
          <div v-if="conflictTip && conflictCount" class="conflict-tip">
            <el-icon><CircleClose /></el-icon>
            冲突:{{ conflictDevice?.id }} 已绑定到 {{ conflictDevice?.boundTo }}
            <el-icon class="x" @click="conflictTip = false"><Close /></el-icon>
          </div>
        </div>
      </IndustrialPanel>

      <!-- 右:设备属性详情 -->
      <IndustrialPanel title="设备属性详情">
        <div v-if="active" class="detail">
          <div class="dhead">
            <el-icon class="dico"><component :is="active.icon || Odometer" /></el-icon>
            <div>
              <strong class="mono">{{ active.id }}</strong>
              <small>{{ active.type }}</small>
            </div>
          </div>
          <span class="qa-tag" :class="active.conflict ? 'danger' : isLinked(active.id) ? 'success' : 'info'">
            {{ active.conflict ? '关联冲突' : isLinked(active.id) ? '已关联 · 在线' : '待关联' }}
          </span>

          <div class="kv">
            <div><span>IP 地址</span><b class="mono">{{ active.ip }}</b></div>
            <div><span>MAC 地址</span><b class="mono">{{ active.mac }}</b></div>
            <div><span>固件版本</span><b class="mono">{{ active.firmware }}</b></div>
            <div><span>运行时长</span><b class="mono">{{ active.uptime }}</b></div>
          </div>

          <div class="sub">监测状态</div>
          <div class="mon">
            <div><span>信号强度</span><b class="mono c-success">{{ active.rssi }} dBm</b></div>
            <div><span>丢包率</span><b class="mono">{{ active.loss }}%</b></div>
          </div>

          <div class="dbtns">
            <el-button v-if="isLinked(active.id)" type="danger" plain :icon="Close" @click="unlink(active)">解除关联</el-button>
            <el-button v-else type="primary" plain :icon="Link" @click="link(active)">建立关联</el-button>
            <el-button type="primary" :icon="Setting" @click="openConfig">参数配置</el-button>
          </div>
        </div>
        <el-empty v-else description="点击设备查看详情" :image-size="80" />
      </IndustrialPanel>
    </section>

    <!-- 底部:关联历史 -->
    <IndustrialPanel title="设备关联历史">
      <el-table :data="history">
        <el-table-column prop="time" label="时间戳" width="150"><template #default="{ row }"><span class="mono">{{ row.time }}</span></template></el-table-column>
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column label="动作类型" width="120">
          <template #default="{ row }"><span :class="row.action === '建立关联' ? 'c-success' : 'c-danger'">{{ row.action }}</span></template>
        </el-table-column>
        <el-table-column prop="device" label="关联设备" min-width="180" />
        <el-table-column prop="target" label="目标实体" width="120"><template #default="{ row }"><span class="mono c-cyan">{{ row.target }}</span></template></el-table-column>
      </el-table>
    </IndustrialPanel>

    <!-- 参数配置弹窗 -->
    <el-dialog v-model="configDialog" :title="`参数配置 · ${active?.id || ''}`" width="440px">
      <el-form :model="configForm" label-width="96px">
        <el-form-item label="IP 地址"><el-input v-model="configForm.ip" /></el-form-item>
        <el-form-item label="心跳周期(s)"><el-input-number v-model="configForm.heartbeat" :min="1" :max="60" style="width: 100%" /></el-form-item>
        <el-form-item label="上报频率(Hz)"><el-input-number v-model="configForm.freq" :min="1" :max="50" style="width: 100%" /></el-form-item>
        <el-form-item label="通信信道">
          <el-select v-model="configForm.channel" style="width: 100%">
            <el-option label="LoRa 470MHz" value="lora" />
            <el-option label="4G / 5G 专网" value="cellular" />
            <el-option label="工业以太网" value="ethernet" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">下发配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 设备关联:未关联池 + 动态拓扑 + 属性详情 + 关联历史;所有操作本地生效,deviceLinkApi 尽力同步
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, WarningFilled, Cpu, VideoCamera, Odometer, Box, CircleClose, Close, Setting, Link, Microphone } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { deviceLinkApi } from '@/api'

const CRANE = 'CR-8012'
const kw = ref('')
const lastSync = ref('10:42:00')
const syncing = ref(false)
const conflictTip = ref(true)

// 拓扑节点槽位(最多 6 个卫星节点)
const SLOTS = [
  { left: 22, top: 22 }, { left: 72, top: 22 }, { left: 28, top: 74 },
  { left: 72, top: 74 }, { left: 10, top: 50 }, { left: 90, top: 50 },
]

const linkedNodes = ref([
  { id: 'EDG-01', type: '边缘计算盒', icon: Cpu, tone: 'cyan' },
  { id: 'CAM-02', type: '云台摄像机', icon: VideoCamera, tone: 'gold', weak: true },
  { id: 'RDR-01', type: '毫米波雷达传感器', icon: Odometer, tone: 'blue' },
  { id: 'MVR-04', type: '车载录像终端', icon: Box, tone: 'cyan' },
].map((n, i) => ({ ...n, pos: SLOTS[i] })))

const pool = ref([
  { id: 'CAM-05', type: '云台摄像机', icon: VideoCamera, conflict: false },
  { id: 'SPK-12', type: '广播号角', icon: Microphone, conflict: false },
  { id: 'RDR-02', type: '毫米波雷达', icon: Odometer, conflict: true, boundTo: 'CR-7022' },
])
const filteredPool = computed(() => pool.value.filter(d => !kw.value || d.id.includes(kw.value) || d.type.includes(kw.value)))
const conflictCount = computed(() => pool.value.filter(d => d.conflict).length)
const conflictDevice = computed(() => pool.value.find(d => d.conflict))

// 详情:按设备 ID 生成确定性演示属性
function detailOf(d) {
  const seed = [...d.id].reduce((s, ch) => s + ch.charCodeAt(0), 0)
  return {
    ...d,
    ip: `192.168.10.${30 + seed % 60}`,
    mac: `00:1A:2B:${(seed % 90 + 10)}`,
    firmware: `v2.${seed % 4}.${seed % 8}-stable`,
    uptime: `${seed % 40 + 3}d ${seed % 24}h ${seed % 60}m`,
    rssi: -(38 + seed % 20),
    loss: Math.round((seed % 5) * 0.01 * 100) / 100,
  }
}
const active = ref(null)
function select(d) { active.value = detailOf(d) }
function isLinked(id) { return linkedNodes.value.some(n => n.id === id) }

function nowTime() {
  return new Date().toTimeString().slice(0, 8)
}
const history = ref([
  { time: '10:41:22', operator: '管理员', action: '建立关联', device: 'SPK-01(广播音柱)', target: CRANE },
  { time: '09:15:05', operator: '系统任务', action: '断开关联', device: 'CAM-02(摄像头)', target: CRANE },
  { time: '昨日', operator: 'Oper_22', action: '建立关联', device: 'EDG-01(边缘计算盒)', target: CRANE },
])
function pushHistory(action, d) {
  history.value.unshift({ time: nowTime(), operator: '管理员', action, device: `${d.id}(${d.type})`, target: CRANE })
}

// 建立关联:冲突设备需确认强制迁移;拓扑槽位满则提示
async function link(d) {
  if (d.conflict) {
    try {
      await ElMessageBox.confirm(`${d.id} 已绑定至 ${d.boundTo},是否强制迁移至 ${CRANE}?迁移后原绑定将自动解除。`, '关联冲突', { type: 'warning', confirmButtonText: '强制迁移' })
    } catch { return }
  }
  if (linkedNodes.value.length >= SLOTS.length) { ElMessage.warning('当前塔吊关联设备已达上限'); return }
  // 演示设备无后端整型 ID(DeviceLinkCreate 需 crane_id/device_id),关联关系仅本地生效
  pool.value = pool.value.filter(p => p.id !== d.id)
  const usedPos = new Set(linkedNodes.value.map(n => `${n.pos.left},${n.pos.top}`))
  const pos = SLOTS.find(s => !usedPos.has(`${s.left},${s.top}`)) || SLOTS[0]
  linkedNodes.value.push({ id: d.id, type: d.type, icon: d.icon, tone: 'cyan', pos })
  pushHistory('建立关联', d)
  active.value = detailOf(d)
  ElMessage.success(`${d.id} 已关联至 ${CRANE}`)
}

async function unlink(d) {
  try {
    await ElMessageBox.confirm(`确认解除 ${d.id} 与 ${CRANE} 的关联?解除后设备将回到未关联设备池。`, '解除关联', { type: 'warning' })
  } catch { return }
  linkedNodes.value = linkedNodes.value.filter(n => n.id !== d.id)
  pool.value.unshift({ id: d.id, type: d.type, icon: d.icon || Odometer, conflict: false })
  pushHistory('断开关联', d)
  active.value = detailOf(d)
  ElMessage.success(`已解除 ${d.id} 的关联`)
}

// 立即同步:刷新历史并更新同步时间
async function syncNow() {
  syncing.value = true
  try {
    const res = await deviceLinkApi.list({ crane: CRANE })
    if (res?.list?.length && res.list[0]?.time) history.value = res.list
  } catch { /* 回退演示数据 */ }
  setTimeout(() => {
    syncing.value = false
    lastSync.value = nowTime()
    ElMessage.success(`拓扑同步完成,已关联 ${linkedNodes.value.length} 台设备`)
  }, 600)
}

// 参数配置
const configDialog = ref(false)
const configForm = ref({ ip: '', heartbeat: 5, freq: 10, channel: 'lora' })
function openConfig() {
  configForm.value = { ip: active.value?.ip || '', heartbeat: 5, freq: 10, channel: 'lora' }
  configDialog.value = true
}
function saveConfig() {
  configDialog.value = false
  ElMessage.success(`配置已下发至 ${active.value?.id},设备将在下个心跳周期生效`)
}

onMounted(async () => {
  select(linkedNodes.value[2])
  try {
    const res = await deviceLinkApi.list({ crane: CRANE })
    // 后端返回的是按吊车分组的关联关系,仅当结构含历史字段时才替换演示数据
    if (res?.list?.length && res.list[0]?.time) history.value = res.list
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.head h1 { margin: 0; font-size: 20px; }
.head p { margin: 4px 0 0; font-size: 13px; color: var(--qa-text-2); }
.hstat { display: flex; align-items: center; gap: 12px; }
.hs { display: grid; gap: 4px; padding: 8px 16px; text-align: center; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.hs.danger { border-color: rgba(239, 68, 68, .4); }
.hs span { font-size: 11px; color: var(--qa-text-2); }
.hs b { font-size: 20px; }

.grid3 { display: grid; grid-template-columns: 280px minmax(0, 1fr) 300px; gap: 14px; align-items: stretch; }
.grid3 > .panel { display: flex; flex-direction: column; }
.grid3 > .panel :deep(.body) { flex: 1; }
.mb { margin-bottom: 12px; }
.pool { display: flex; flex-direction: column; gap: 10px; }
.pool-item { display: flex; align-items: center; gap: 10px; width: 100%; padding: 12px; text-align: left; cursor: pointer;
  background: var(--qa-panel-2); border: 1px solid var(--qa-border); border-radius: 6px; color: var(--qa-text); }
.pool-item:hover { border-color: var(--qa-border-strong); }
.pool-item.picked { border-color: var(--qa-blue); box-shadow: 0 0 8px rgba(59, 130, 246, .3); }
.pool-item.conflict { border-color: rgba(239, 68, 68, .5); }
.pool-item .el-icon { font-size: 20px; }
.pool-item strong { display: block; font-size: 14px; }
.pool-item small { font-size: 11px; color: var(--qa-text-muted); }
.pool-item .warn { margin-left: auto; }

/* 拓扑 */
.topo { position: relative; height: 360px; }
.links { position: absolute; inset: 0; width: 100%; height: 100%; }
.links line { stroke: var(--qa-blue); stroke-width: 1.5; }
.links line.weak { stroke: var(--qa-gold); opacity: .6; }
.node { position: absolute; transform: translate(-50%, -50%); display: grid; place-items: center; gap: 2px;
  width: 60px; height: 60px; border-radius: 8px; background: var(--qa-panel-2); border: 1px solid var(--qa-border-strong);
  z-index: 2; color: var(--qa-text); cursor: pointer; }
.node b { font-size: 11px; }
.node .el-icon { font-size: 18px; }
.node.center { left: 50%; top: 56%; background: var(--qa-blue-dim); border-color: var(--qa-blue); color: var(--qa-blue); font: 700 12px var(--qa-mono); cursor: default; }
.node.cyan { color: var(--qa-cyan); border-color: rgba(34, 211, 238, .5); }
.node.gold { color: var(--qa-gold); border-color: rgba(234, 179, 8, .5); }
.node.blue { color: var(--qa-blue); border-color: rgba(59, 130, 246, .5); }
.node.active { border-color: var(--qa-blue); box-shadow: 0 0 12px rgba(59, 130, 246, .4); }
.node .wk { position: absolute; bottom: -16px; font-size: 10px; color: var(--qa-gold); white-space: nowrap; }
.conflict-tip { position: absolute; left: 50%; bottom: 4px; transform: translateX(-50%); display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; font-size: 12px; color: var(--qa-danger); background: var(--qa-danger-dim); border: 1px solid rgba(239, 68, 68, .4); border-radius: 6px; white-space: nowrap; }
.conflict-tip .x { cursor: pointer; }

/* 详情 */
.dhead { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.dico { font-size: 22px; color: var(--qa-blue); padding: 8px; background: var(--qa-blue-dim); border-radius: 8px; }
.dhead strong { display: block; font-size: 15px; }
.dhead small { font-size: 12px; color: var(--qa-text-2); }
.kv { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
.kv > div { display: grid; gap: 4px; }
.kv span { font-size: 11px; color: var(--qa-text-2); }
.kv b { font-size: 12px; word-break: break-all; }
.sub { font-size: 13px; font-weight: 600; color: var(--qa-cyan); margin: 12px 0 10px; }
.mon > div { display: flex; justify-content: space-between; padding: 10px 12px; margin-bottom: 8px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); font-size: 12px; }
.dbtns { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.dbtns .el-button { margin: 0; }

@media (max-width: 1300px) { .grid3 { grid-template-columns: 1fr; } }
</style>
