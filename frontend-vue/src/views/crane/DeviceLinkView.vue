<template>
  <div class="page devlink">
    <!-- 标题 + 顶部统计 -->
    <div class="head">
      <div>
        <h1>设备关联配置</h1>
        <p>当前塔吊:<b class="mono">CR-8012</b> · 最后同步时间:10:42 AM</p>
      </div>
      <div class="hstat">
        <div class="hs"><span>已关联设备</span><b class="mono c-cyan">{{ stat.linked }}</b></div>
        <div class="hs"><span>待关联设备</span><b class="mono">{{ stat.pending }}</b></div>
        <div class="hs danger"><span>关联冲突</span><b class="mono c-danger">{{ stat.conflict }}</b></div>
        <el-button type="primary" :icon="Refresh">立即同步</el-button>
      </div>
    </div>

    <section class="grid3">
      <!-- 左:未关联设备池 -->
      <IndustrialPanel title="未关联设备池">
        <el-input v-model="kw" placeholder="搜索设备名称/型号…" :prefix-icon="Search" class="mb" />
        <div class="pool">
          <button v-for="d in filteredPool" :key="d.id" type="button" class="pool-item" :class="{ conflict: d.conflict }" @click="select(d)">
            <el-icon :class="d.conflict ? 'c-danger' : 'c-cyan'"><component :is="d.icon" /></el-icon>
            <div>
              <strong class="mono">{{ d.id }}</strong>
              <small :class="{ 'c-danger': d.conflict }">{{ d.conflict ? '已绑定至 ' + d.boundTo : d.type }}</small>
            </div>
            <el-icon v-if="d.conflict" class="c-danger warn"><WarningFilled /></el-icon>
          </button>
        </div>
      </IndustrialPanel>

      <!-- 中:关联拓扑视图 -->
      <IndustrialPanel title="关联拓扑视图">
        <template #extra><span class="c-muted">CR-8012 拓扑</span></template>
        <div class="topo">
          <svg class="links" viewBox="0 0 400 320" preserveAspectRatio="none">
            <line x1="200" y1="180" x2="110" y2="90" />
            <line x1="200" y1="180" x2="130" y2="250" />
            <line x1="200" y1="180" x2="300" y2="250" />
            <line x1="200" y1="180" x2="300" y2="90" stroke-dasharray="5 5" class="weak" />
          </svg>
          <div class="node center">CR-8012</div>
          <div class="node cyan" style="left: 22%; top: 22%"><el-icon><Cpu /></el-icon><b>EDG-01</b></div>
          <div class="node gold" style="left: 72%; top: 22%"><el-icon><VideoCamera /></el-icon><b>CAM-02</b><span class="wk">信号弱</span></div>
          <div class="node blue active" style="left: 28%; top: 74%"><el-icon><Odometer /></el-icon><b>RDR-01</b></div>
          <div class="node cyan" style="left: 72%; top: 74%"><el-icon><Box /></el-icon><b>MVR-04</b></div>
          <div class="conflict-tip">
            <el-icon><CircleClose /></el-icon>
            冲突:CAM-03 已绑定到 CR-7022
            <el-icon class="x"><Close /></el-icon>
          </div>
        </div>
      </IndustrialPanel>

      <!-- 右:设备属性详情 -->
      <IndustrialPanel title="设备属性详情">
        <div class="detail">
          <div class="dhead">
            <el-icon class="dico"><Odometer /></el-icon>
            <div>
              <strong class="mono">{{ active.id }}</strong>
              <small>{{ active.type }}</small>
            </div>
          </div>
          <span class="qa-tag success">在线</span>

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
            <el-button type="danger" plain :icon="Close">解除关联</el-button>
            <el-button type="primary" :icon="Setting">参数配置</el-button>
          </div>
        </div>
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
  </div>
</template>

<script setup>
// 设备关联:未关联池 + 拓扑视图 + 属性详情 + 关联历史;deviceLinkApi 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { Refresh, Search, WarningFilled, Cpu, VideoCamera, Odometer, Box, CircleClose, Close, Setting, Microphone } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { deviceLinkApi } from '@/api'

const stat = ref({ linked: 5, pending: 12, conflict: 1 })
const kw = ref('')

const pool = ref([
  { id: 'CAM-05', type: '云台摄像机', icon: VideoCamera, conflict: false },
  { id: 'SPK-12', type: '广播号角', icon: Microphone, conflict: false },
  { id: 'RDR-02', type: '毫米波雷达', icon: Odometer, conflict: true, boundTo: 'CR-7022' },
])
const filteredPool = computed(() => pool.value.filter(d => !kw.value || d.id.includes(kw.value) || d.type.includes(kw.value)))

const active = ref({ id: 'RDR-01', type: '毫米波雷达传感器', ip: '192.168.10.44', mac: '00:1A:2B:3C', firmware: 'v2.1.4-stable', uptime: '14d 08h 22m', rssi: -42, loss: 0.01 })
function select(d) { active.value = { ...active.value, id: d.id, type: d.type } }

const history = ref([
  { time: '10:41:22 AM', operator: '管理员', action: '建立关联', device: 'SPK-01(广播音柱)', target: 'CR-8012' },
  { time: '09:15:05 AM', operator: '系统任务', action: '断开关联', device: 'CAM-02(摄像头)', target: 'CR-8012' },
  { time: '昨日', operator: 'Oper_22', action: '建立关联', device: 'EDG-01(边缘计算盒)', target: 'CR-8012' },
])

onMounted(async () => {
  try {
    const res = await deviceLinkApi.list({ crane: 'CR-8012' })
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
  width: 60px; height: 60px; border-radius: 8px; background: var(--qa-panel-2); border: 1px solid var(--qa-border-strong); z-index: 2; }
.node b { font-size: 11px; }
.node .el-icon { font-size: 18px; }
.node.center { left: 50%; top: 56%; background: var(--qa-blue-dim); border-color: var(--qa-blue); color: var(--qa-blue); font: 700 12px var(--qa-mono); }
.node.cyan { color: var(--qa-cyan); border-color: rgba(34, 211, 238, .5); }
.node.gold { color: var(--qa-gold); border-color: rgba(234, 179, 8, .5); }
.node.blue.active { color: var(--qa-blue); border-color: var(--qa-blue); box-shadow: 0 0 12px rgba(59, 130, 246, .4); }
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
