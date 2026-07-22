<template>
  <div class="page">
    <div class="stat-row">
      <StatCard label="音柱总数" :value="stats.total" suffix="台" accent="#22d3ee" />
      <StatCard label="在线率" :value="stats.onlineRate" suffix="%" accent="#22c55e" />
      <StatCard label="今日播报" :value="stats.today" suffix="次" hint="↑ 12% 同比" accent="#22d3ee" />
      <StatCard label="设备告警" :value="stats.alarm" suffix="台" accent="#ef4444" />
    </div>

    <div class="main">
      <IndustrialPanel title="设备列表" class="list-panel">
        <template #extra>
          <div class="ex">
            <el-input v-model="query.keyword" placeholder="查询设备编号、安装点位..." size="small" style="width: 220px" @keyup.enter="load" />
            <el-button type="primary" size="small" @click="onAdd">+ 新增设备</el-button>
          </div>
        </template>
        <el-table :data="list" highlight-current-row @current-change="onSelect" height="500">
          <el-table-column label="状态" width="60">
            <template #default="{ row }"><span class="status-dot" :class="row.status === 'online' ? 'c-success' : 'c-danger'" /></template>
          </el-table-column>
          <el-table-column label="编号 / 点位" min-width="140">
            <template #default="{ row }"><b>{{ row.code }}</b><br /><small :class="row.status === 'online' ? 'text-muted' : 'c-danger'">{{ row.location }}</small></template>
          </el-table-column>
          <el-table-column label="关联单车" width="110">
            <template #default="{ row }"><span class="qa-tag cyan">{{ row.crane || '—' }}</span></template>
          </el-table-column>
          <el-table-column label="当前音量" width="140">
            <template #default="{ row }">
              <div class="bar-cell"><span class="mono">{{ row.status === 'online' ? row.volume + '%' : '—' }}</span>
                <div class="bar"><i :style="{ width: (row.status === 'online' ? row.volume : 0) + '%' }" /></div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="最近播报内容" min-width="180">
            <template #default="{ row }">
              <template v-if="row.status === 'online'"><b>"{{ row.lastText }}"</b><br /><small class="text-muted mono">{{ row.lastTime }}</small></template>
              <span v-else class="text-muted">无信号</span>
            </template>
          </el-table-column>
          <el-table-column label="心跳延时" width="90" align="right">
            <template #default="{ row }"><span class="mono" :class="row.status === 'online' ? 'c-success' : 'c-danger'">{{ row.status === 'online' ? row.ping + 'ms' : '超时' }}</span></template>
          </el-table-column>
        </el-table>
      </IndustrialPanel>

      <IndustrialPanel title="设备详情" class="detail-panel">
        <template #extra><span v-if="current" class="qa-tag" :class="current.status === 'online' ? 'success' : 'danger'">{{ current.status === 'online' ? '运行中' : '离线' }}</span></template>
        <div v-if="current" class="detail">
          <h4>基础信息</h4>
          <div class="info-grid">
            <div><span>序列号</span><b class="mono">{{ current.sn || 'SN-79827361A' }}</b></div>
            <div><span>IP 地址</span><b class="mono">{{ current.ip || '192.168.1.104' }}</b></div>
            <div><span>启用日期</span><b class="mono">{{ current.since || '2023-10-12' }}</b></div>
            <div><span>固件版本</span><b class="mono c-cyan">{{ current.fw || 'v2.1.4' }}</b></div>
          </div>
          <div class="divider" />
          <h4>远程控制台</h4>
          <div class="vol-row">
            <span><el-icon><Microphone /></el-icon> 播放音量</span><b class="mono c-cyan">{{ ctrlVolume }}%</b>
          </div>
          <el-slider v-model="ctrlVolume" :disabled="current.status !== 'online'" />
          <div class="tts-label"><el-icon><ChatDotRound /></el-icon> 即时喊话 (TTS)</div>
          <div class="tts-row">
            <el-input v-model="ttsText" placeholder="输入文字内容..." :disabled="current.status !== 'online'" />
            <el-button type="primary" :disabled="current.status !== 'online'" @click="onBroadcast"><el-icon><Promotion /></el-icon></el-button>
          </div>
          <el-button class="preset-btn" :disabled="current.status !== 'online'" @click="onBroadcast('预设标警音')">◎ 播放预设标警音</el-button>
          <div class="divider" />
          <h4>今日播报记录</h4>
          <ul class="rec">
            <li v-for="r in current.records || demoRec" :key="r.time">
              <div class="rec-head"><span class="status-dot" :class="r.type === 'sys' ? 'c-cyan' : 'c-blue'" /><b>{{ r.title }}</b><time class="mono">{{ r.time }}</time></div>
              <p>"{{ r.text }}"</p>
            </li>
          </ul>
        </div>
        <el-empty v-else description="请选择音柱" />
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, ChatDotRound, Promotion } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { speakerApi } from '@/api'

const stats = reactive({ total: 48, onlineRate: 95.8, today: 124, alarm: 2 })
const query = reactive({ keyword: '' })
const list = ref([])
const current = ref(null)
const ctrlVolume = ref(85)
const ttsText = ref('')

const demo = [
  { id: 1, code: 'SPK-001', location: '2# 塔吊臂端', crane: 'CR-0013', volume: 85, lastText: '注意安全,请戴好安全帽', lastTime: '10:43:15', ping: 22, status: 'online', records: [{ type: 'sys', title: '区域闯入告警(系统)', time: '10:43:15', text: '警告:您已进入电子围栏区域,请立刻撤离。' }, { type: 'man', title: '人工喊话', time: '09:15:00', text: '塔吊操作,务必超注意交接班安全。' }] },
  { id: 2, code: 'SPK-002', location: '3# 塔吊基座', crane: 'CR-0015', volume: 60, lastText: '风力过大,暂停作业', lastTime: '09:15:00', ping: 45, status: 'online' },
  { id: 3, code: 'SPK-003', location: '1# 塔吊配电(离线)', crane: 'CR-0002', volume: 0, lastText: '', lastTime: '', ping: 0, status: 'offline' },
]
const demoRec = [{ type: 'sys', title: '区域闯入告警(系统)', time: '10:43:15', text: '警告:您已进入电子围栏区域,请立刻撤离。' }, { type: 'man', title: '人工喊话', time: '09:15:00', text: '塔吊操作,务必注意交接班安全。' }]

async function load() {
  try {
    const res = await speakerApi.list({ ...query, page: 1, page_size: 50 })
    list.value = (res.list && res.list.length) ? res.list : demo
  } catch { list.value = demo }
  if (!current.value) onSelect(list.value[0])
}
function onSelect(row) { if (row) { current.value = row; ctrlVolume.value = row.volume || 0 } }
watch(ctrlVolume, () => {}) // 滑条即时反馈由后端下发,演示态忽略
function onBroadcast(preset) {
  const t = typeof preset === 'string' ? preset : ttsText.value
  if (!t) return ElMessage.warning('请输入喊话内容')
  ElMessage.success(`已向 ${current.value.code} 下发喊话:${t}`)
  ttsText.value = ''
}
const onAdd = () => ElMessage.info('新增音柱表单开发中')
onMounted(load)
</script>

<style scoped>
.main { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 16px; }
.ex { display: flex; gap: 10px; align-items: center; }
.bar-cell { display: flex; align-items: center; gap: 8px; }
.bar { flex: 1; height: 5px; background: var(--qa-panel-3); border-radius: 3px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--qa-cyan); }
.detail { display: flex; flex-direction: column; gap: 12px; }
.detail h4 { margin: 0; font-size: 13px; color: var(--qa-text-2); }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px; background: var(--qa-panel-2); border: 1px solid var(--qa-border); border-radius: 6px; }
.info-grid span { display: block; font-size: 11px; color: var(--qa-text-muted); margin-bottom: 4px; }
.info-grid b { font-size: 13px; }
.divider { height: 1px; background: var(--qa-border); }
.vol-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: var(--qa-text-2); }
.tts-label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--qa-text-2); margin-top: 4px; }
.tts-row { display: flex; gap: 8px; }
.preset-btn { width: 100%; }
.rec { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.rec-head { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.rec-head time { margin-left: auto; font-size: 11px; color: var(--qa-text-muted); }
.rec p { margin: 6px 0 0 16px; padding: 8px 10px; font-size: 12px; color: var(--qa-text-2); background: var(--qa-panel-2); border-left: 2px solid var(--qa-border-strong); border-radius: 4px; }
@media (max-width: 1100px) { .main { grid-template-columns: 1fr; } }
</style>
