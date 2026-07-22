<template>
  <div class="page">
    <div class="risk-main">
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
          <!-- 证据影像占位 -->
          <div class="evidence">
            <div class="ev-head"><span class="mono">CAM-A-06 | {{ current.time }}</span><span class="rec"><i class="status-dot c-danger" />实时录制中</span></div>
            <div class="ev-box"><el-icon class="ev-ico"><Picture /></el-icon><span>AI 识别证据帧占位</span></div>
          </div>
          <div class="grid2">
            <div><span>发生区域</span><b>{{ current.area }} 作业半径内</b></div>
            <div><span>识别策略节点</span><b class="mono">AI_VISION_NODE_03</b></div>
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
            <li v-for="(t, i) in current.timeline || demoTimeline" :key="i">
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
import { Picture } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { riskEventApi } from '@/api'

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

const demo = [
  { id: 1, type: '人员违规闯入', code: 'EV-20231026-001', level: 'high', area: 'A区 塔吊01', time: '10/24 14:22:05', status: 'pending', owner: '第一施工队 - 张班组', deadline: '10/24 16:00:00 (-1h 30m)' },
  { id: 2, type: '安全帽未佩戴', code: 'EV-20231024-018', level: 'mid', area: 'B区 闸口', time: '10/24 13:15:22', status: 'resolved' },
  { id: 3, type: '违规超载告警', code: 'EV-20231024-033', level: 'high', area: 'C区 塔吊03', time: '10/24 11:05:10', status: 'processing' },
  { id: 4, type: '周界越界', code: 'EV-20231023-090', level: 'low', area: '电子围栏北侧', time: '10/23 22:45:00', status: 'closed' },
  { id: 5, type: '结构失稳', code: 'EV-20231023-076', level: 'high', area: 'A区 塔吊02', time: '10/23 16:38:11', status: 'closed' },
  { id: 6, type: '未系安全带', code: 'EV-20231023-055', level: 'mid', area: 'C区 高空作业台', time: '10/23 09:12:44', status: 'resolved' },
]
const demoTimeline = [
  { time: '10/24 16:22:05', title: 'AI 视觉分析触发告警', desc: '系统已自动生成工单,并同步触发联动广播喊话告警。' },
  { time: '10/24 16:25:13', title: '等待人工复核介入', desc: '等待班组安全负责人确认现场情况后下达进一步整改指令。' },
]

const riskTag = (l) => ({ high: 'danger', mid: 'warning', low: 'info' }[l] || 'info')
const riskText = (l) => ({ high: '高风险', mid: '中风险', low: '低风险' }[l] || '未知')
const canHandle = computed(() => current.value && ['pending', 'processing'].includes(current.value.status))

async function load() {
  try {
    const res = await riskEventApi.list({ ...query, page: 1, page_size: 50 })
    list.value = (res.list && res.list.length) ? res.list : demo
  } catch { list.value = demo }
  if (!current.value) onSelect(list.value[0])
}
function onSelect(row) { if (row) { current.value = row; handleForm.note = '' } }

async function doHandle(action, label) {
  const nextStatus = action === 'archive' ? 'closed' : action === 'submit' ? 'resolved' : 'processing'
  try { await riskEventApi.handle(current.value.id, { action, handler: '管理员', note: handleForm.note }) } catch { /* 演示忽略 */ }
  current.value.status = nextStatus
  ;(current.value.timeline = current.value.timeline || [...demoTimeline]).unshift({ time: new Date().toLocaleString('zh-CN'), title: label, desc: handleForm.note || '(无备注)' })
  ElMessage.success(`已${label}`)
  handleForm.note = ''
}
onMounted(load)
</script>

<style scoped>
.risk-main { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 16px; }
.filterbar { display: flex; gap: 10px; margin-bottom: 10px; }
.detail { display: flex; flex-direction: column; gap: 12px; }
.ev-id { font-size: 13px; }
.evidence { border: 1px solid var(--qa-border-strong); border-radius: 6px; overflow: hidden; }
.ev-head { display: flex; justify-content: space-between; padding: 8px 10px; font-size: 11px; background: var(--qa-panel-2); }
.ev-head .rec { display: flex; align-items: center; gap: 6px; color: var(--qa-danger); }
.ev-box { height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; background: #050b12; color: var(--qa-text-muted); }
.ev-ico { font-size: 40px; }
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
</style>
