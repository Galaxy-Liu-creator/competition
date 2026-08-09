<template>
  <div class="page">
    <div class="risk-main page-fill">
      <!-- 左:事件列表 -->
      <IndustrialPanel title="风险事件列表" class="list-panel">
        <template #extra><span class="mono text-muted">更新于 {{ now }}</span></template>
        <div class="filterbar">
          <el-input v-model="query.keyword" placeholder="搜索事件/区域" size="small" style="width: 150px" @keyup.enter="load" />
          <el-select v-model="query.status" placeholder="全部状态" size="small" clearable style="width: 130px">
            <el-option v-for="(t, k) in statusMap" :key="k" :label="t.text" :value="k" />
          </el-select>
          <el-button size="small" @click="load">筛选</el-button>
        </div>
        <el-table :data="list" highlight-current-row @current-change="onSelect" height="520">
          <el-table-column label="风险类型" min-width="140">
            <template #default="{ row }"><b>{{ row.type }}</b><br /><small class="text-muted mono">{{ row.code }}</small></template>
          </el-table-column>
          <el-table-column label="风险等级" width="90">
            <template #default="{ row }"><span class="qa-tag" :class="riskTag(row.level)">{{ riskText(row.level) }}</span></template>
          </el-table-column>
          <el-table-column label="作业区域" width="110"><template #default="{ row }">{{ row.area }}</template></el-table-column>
          <el-table-column label="发生时间" width="150"><template #default="{ row }"><span class="mono">{{ row.time }}</span></template></el-table-column>
          <el-table-column label="处置状态" width="100" align="right">
            <template #default="{ row }"><span class="qa-tag" :class="statusMap[row.status].tag">{{ statusMap[row.status].text }}</span></template>
          </el-table-column>
        </el-table>
      </IndustrialPanel>

      <!-- 右:事件详情 -->
      <IndustrialPanel title="事件详情" class="detail-panel">
        <template #extra>
          <span v-if="current" class="qa-tag" :class="statusMap[current.status].tag">{{ statusMap[current.status].text }}</span>
        </template>
        <div v-if="current" class="detail">
          <div class="ev-id mono c-cyan">{{ current.code }}</div>
          <!-- 证据影像 -->
          <div class="evidence">
            <div class="ev-head">
              <span class="mono">{{ current.evidence.sourceNode }} | {{ current.time }}</span>
              <span class="capture" :class="current.evidence.evidenceMode"><i class="status-dot" />{{ current.evidence.captureLabel }}</span>
            </div>
            <div class="ev-box">
              <img class="ev-bg" :src="current.img || current.evidence.path" alt="" aria-hidden="true" />
              <img class="ev-img" :src="current.img || current.evidence.path" :alt="current.evidence.alt" />
              <span class="ev-tag mono">{{ current.evidence.evidenceLabel }} · {{ current.code }}</span>
            </div>
          </div>
          <div class="evidence-note">
            <span class="qa-tag info">{{ current.evidence.modeLabel }}</span>
            <p>{{ current.evidence.note }}</p>
          </div>
          <div class="grid2">
            <div><span>发生区域</span><b>{{ current.area }} 作业半径内</b></div>
            <div><span>判定来源</span><b class="mono">{{ current.evidence.sourceNode }}</b></div>
            <div><span>责任主体</span><b>{{ current.owner || '第一施工队 - 张班组' }}</b></div>
            <div><span>处置截止倒计时</span><b class="mono c-danger">{{ current.deadline || '16:00:00 (-1h 30m)' }}</b></div>
          </div>
          <div class="divider" />
          <h4>整改方案与处置</h4>
          <el-input v-model="handleForm.note" type="textarea" :rows="3" placeholder="请输入整改详细措施或指派具体执行人责任明确..." />
          <div class="handle-actions" v-if="canHandle">
            <el-button @click="doHandle('archive', '误报归档')">误报归档</el-button>
            <el-button type="warning" @click="doHandle('workorder', '重派整改工单')">重派整改工单</el-button>
            <el-button type="primary" @click="doHandle('submit', '提交审核处置')">提交审核处置</el-button>
          </div>
          <div v-else class="closed-tip">该事件已 {{ statusMap[current.status].text }},无需进一步处置。</div>
          <div class="divider" />
          <h4>处置追踪日志</h4>
          <ul class="timeline">
            <li v-for="(t, i) in current.timeline || defaultTimeline" :key="i">
              <span class="tl-dot" :class="i === 0 ? 'active' : ''" />
              <div><time class="mono">{{ t.time }}</time><b>{{ t.title }}</b><p>{{ t.desc }}</p></div>
            </li>
          </ul>
        </div>
        <el-empty v-else description="请选择事件查看详情" />
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { riskEventApi } from '@/api'
import { riskEvidenceFor } from '@/data/demoMedia'

const now = new Date().toLocaleString('zh-CN')
const statusMap = {
  pending: { text: '待处置', tag: 'danger' },
  processing: { text: '处置中', tag: 'warning' },
  resolved: { text: '已解决', tag: 'success' },
  closed: { text: '已关闭', tag: 'info' },
}
const query = reactive({ keyword: '', status: '' })
const list = ref([])
const current = ref(null)
const handleForm = reactive({ note: '' })

const attachEvidence = (item) => {
  const evidence = riskEvidenceFor(item.type)
  return { ...item, evidence, img: item.img || evidence.path }
}
const demo = [
  { id: 1, type: '违规闯入', code: 'EV-20231026-001', level: 'high', area: 'A区 塔吊01', time: '10/24 14:22:05', status: 'pending', owner: '第一施工队 - 张班组', deadline: '10/24 16:00:00 (-1h 30m)' },
  { id: 2, type: '未佩戴安全帽', code: 'EV-20231024-018', level: 'mid', area: 'B区 闸口', time: '10/24 13:15:22', status: 'resolved' },
  { id: 3, type: '超载起吊', code: 'EV-20231024-033', level: 'high', area: 'C区 塔吊03', time: '10/24 11:05:10', status: 'processing' },
  { id: 4, type: '设备离线', code: 'EV-20231023-090', level: 'low', area: '电子围栏北侧', time: '10/23 22:45:00', status: 'closed' },
  { id: 5, type: '大风超阈值起吊', code: 'EV-20231023-076', level: 'high', area: 'A区 塔吊02', time: '10/23 16:38:11', status: 'closed' },
  { id: 6, type: '未系安全带', code: 'EV-20231023-055', level: 'mid', area: 'C区 高空作业台', time: '10/23 09:12:44', status: 'resolved' },
].map(attachEvidence)

const riskTag = (l) => ({ high: 'danger', mid: 'warning', low: 'info' }[l] || 'info')
const riskText = (l) => ({ high: '高风险', mid: '中风险', low: '低风险' }[l] || '未知')
const canHandle = computed(() => current.value && ['pending', 'processing'].includes(current.value.status))
const defaultTimeline = computed(() => {
  const evidence = current.value?.evidence || riskEvidenceFor('')
  const first = {
    'direct-visual': {
      title: `${evidence.evidenceLabel}触发告警`,
      desc: '证据帧中的可见风险已写入事件工单，并进入人工复核流程。',
    },
    'overlay-assisted': {
      title: `${evidence.evidenceLabel}触发告警`,
      desc: '系统结合画面目标与演示危险区/电子围栏关系生成事件工单。',
    },
    'sensor-context': {
      title: `${evidence.evidenceLabel}触发告警`,
      desc: '系统根据确定性演示遥测判定异常；图片仅用于提供对应设备与作业场景。',
    },
  }[evidence.evidenceMode]
  return [
    { time: current.value?.time || '10/24 16:22:05', ...first },
    { time: '10/24 16:25:13', title: '等待人工复核介入', desc: '等待班组安全负责人确认现场情况后下达进一步整改指令。' },
  ]
})

const levelMap = { critical: 'high', severe: 'high', high: 'high', major: 'mid', general: 'low', mid: 'mid', minor: 'low', low: 'low' }
const fmtTime = (t) => (t ? String(t).replace('T', ' ').slice(5, 16) : '')
const validEvidencePath = (value) => [
  '/dataset/construction/', '/dataset/ppe/', '/dataset/violations/',
  '/dataset/lifting/', '/dataset/equipment/', '/dataset/access-control/',
]
  .some((prefix) => String(value || '').startsWith(prefix))

// 回退演示数据的客户端过滤:保证后端不可用时筛选仍生效
function demoFiltered() {
  const kw = query.keyword.trim().toLowerCase()
  return demo.filter((r) =>
    (!kw || `${r.type} ${r.code} ${r.area}`.toLowerCase().includes(kw)) &&
    (!query.status || r.status === query.status))
}

async function load() {
  try {
    const res = await riskEventApi.list({ ...query, page: 1, page_size: 50 })
    // 后端字段(event_no/work_zone/occurred_at/...)映射为页面字段,缺省时补演示值
    list.value = (res.list && res.list.length)
      ? res.list.map((r, i) => attachEvidence({
          id: r.id,
          type: r.type || '风险事件',
          code: r.event_no || r.code || `EV-${1000 + i}`,
          level: levelMap[r.level] || 'mid',
          area: r.work_zone || r.area || ['A区 塔吊01', 'B区 闸口', 'C区 塔吊03'][i % 3],
          time: fmtTime(r.occurred_at || r.time),
          status: statusMap[r.status] ? r.status : 'pending',
          owner: r.handler || '第一施工队 - 张班组',
          img: validEvidencePath(r.image_url) ? r.image_url : undefined,
        }))
      : demoFiltered()
  } catch { list.value = demoFiltered() }
  if (!list.value.includes(current.value)) onSelect(list.value[0])
}
function onSelect(row) { if (row) { current.value = row; handleForm.note = '' } }

async function doHandle(action, label) {
  const nextStatus = action === 'archive' ? 'closed' : action === 'submit' ? 'resolved' : 'processing'
  // 页面按钮文案与后端处置动作保持独立：后端只接受 accept/process/resolve/close。
  const apiAction = { archive: 'close', workorder: 'process', submit: 'resolve' }[action] || action
  try { await riskEventApi.handle(current.value.id, { action: apiAction, handler: '管理员', note: handleForm.note }) } catch { /* 演示忽略 */ }
  current.value.status = nextStatus
  ;(current.value.timeline = current.value.timeline || [...defaultTimeline.value]).unshift({ time: new Date().toLocaleString('zh-CN'), title: label, desc: handleForm.note || '(无备注)' })
  ElMessage.success(`已${label}`)
  handleForm.note = ''
}
onMounted(load)
</script>

<style scoped>
.risk-main { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 16px; align-items: stretch; }
.risk-main > .panel :deep(.body) { flex: 1; min-height: 0; }
.list-panel :deep(.body) { display: flex; flex-direction: column; }
.filterbar { display: flex; gap: 10px; margin-bottom: 10px; }
.detail { display: flex; flex-direction: column; gap: 12px; }
.ev-id { font-size: 13px; }
.evidence { border: 1px solid var(--qa-border-strong); border-radius: 6px; overflow: hidden; }
.ev-head { display: flex; justify-content: space-between; padding: 8px 10px; font-size: 11px; background: var(--qa-panel-2); }
.ev-head .capture { display: flex; align-items: center; gap: 6px; }
.ev-head .capture.direct-visual { color: var(--qa-danger); }
.ev-head .capture.overlay-assisted { color: var(--qa-cyan); }
.ev-head .capture.sensor-context { color: var(--qa-gold); }
.ev-head .capture .status-dot { background: currentColor; }
.ev-box { position: relative; height: 230px; background: #050b12; overflow: hidden; }
.ev-box .ev-bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: blur(16px) brightness(.4) saturate(.7); transform: scale(1.12); }
.ev-box .ev-img { position: relative; width: 100%; height: 100%; object-fit: contain; filter: brightness(.82); }
.ev-tag { position: absolute; left: 8px; bottom: 8px; padding: 3px 8px; font-size: 10px; color: var(--qa-cyan); background: rgba(4,13,24,.75); border-radius: 3px; }
.evidence-note { display: flex; align-items: flex-start; gap: 9px; padding: 9px 10px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.evidence-note p { margin: 0; font-size: 11px; line-height: 1.6; color: var(--qa-text-2); }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.grid2 span { display: block; font-size: 11px; color: var(--qa-text-muted); margin-bottom: 4px; }
.grid2 b { font-size: 13px; }
.divider { height: 1px; background: var(--qa-border); }
.detail h4 { margin: 0; font-size: 13px; color: var(--qa-text-2); }
.handle-actions { display: flex; gap: 10px; }
.handle-actions .el-button { flex: 1; }
.closed-tip { font-size: 12px; color: var(--qa-text-muted); padding: 8px; background: var(--qa-panel-2); border-radius: 6px; }
.timeline { list-style: none; margin: 0; padding: 0 0 0 6px; display: flex; flex-direction: column; gap: 16px; }
.timeline li { position: relative; display: flex; gap: 14px; }
.tl-dot { width: 12px; height: 12px; margin-top: 3px; border-radius: 50%; border: 2px solid var(--qa-border-strong); flex-shrink: 0; }
.tl-dot.active { border-color: var(--qa-cyan); background: var(--qa-cyan); box-shadow: 0 0 8px var(--qa-cyan); }
.timeline time { display: block; font-size: 11px; color: var(--qa-text-muted); }
.timeline b { display: block; font-size: 13px; margin: 3px 0; color: var(--qa-cyan); }
.timeline p { margin: 0; font-size: 12px; color: var(--qa-text-2); }
@media (max-width: 1100px) { .risk-main { grid-template-columns: 1fr; } }
@media (max-width: 620px) { .grid2 { grid-template-columns: 1fr; } .evidence-note { flex-direction: column; } }
</style>
