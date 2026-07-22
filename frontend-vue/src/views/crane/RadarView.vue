<template>
  <div class="page radar">
    <section class="layout">
      <!-- 左:雷达资产列表 -->
      <IndustrialPanel title="雷达资产列表">
        <template #extra>
          <div class="toolbar">
            <el-input v-model="kw" placeholder="搜索设备 ID…" :prefix-icon="Search" size="small" style="width: 180px" />
            <el-button size="small" :icon="Filter">筛选</el-button>
          </div>
        </template>
        <el-table :data="pagedRows" highlight-current-row @current-change="r => r && (current = r)">
          <el-table-column label="设备 ID / 名称" min-width="150">
            <template #default="{ row }"><div class="idc"><b class="mono">{{ row.id }}</b><small>{{ row.name }}</small></div></template>
          </el-table-column>
          <el-table-column prop="model" label="型号" width="110"><template #default="{ row }"><span class="mono">{{ row.model }}</span></template></el-table-column>
          <el-table-column prop="position" label="安装位置" width="100" />
          <el-table-column prop="crane" label="关联吊车" width="110"><template #default="{ row }"><span class="c-blue mono">{{ row.crane }}</span></template></el-table-column>
          <el-table-column label="覆盖半径" width="90"><template #default="{ row }"><span class="mono">{{ row.radius }}m</span></template></el-table-column>
          <el-table-column label="在线状态" width="100">
            <template #default="{ row }"><span :class="toneClass(row.status)"><i class="status-dot" :class="toneClass(row.status)"></i> {{ statusLabel(row.status) }}</span></template>
          </el-table-column>
          <el-table-column label="标定状态" width="110">
            <template #default="{ row }"><span class="qa-tag" :class="calTone(row.calibration)">{{ row.calibration }}</span></template>
          </el-table-column>
        </el-table>
        <div class="pager">
          <span class="mono c-muted">显示 1 - {{ pagedRows.length }} 共 {{ filteredRows.length }} 个设备</span>
          <el-pagination layout="prev, pager, next" background small :total="filteredRows.length" :page-size="pageSize" v-model:current-page="page" />
        </div>
      </IndustrialPanel>

      <!-- 右:覆盖预览 + 参数配置 + 点云 -->
      <aside class="right">
        <IndustrialPanel title="雷达扇形覆盖预览">
          <template #extra><span class="c-cyan mono">{{ current?.id }}</span></template>
          <div class="scope">
            <div class="sweep"></div>
            <span class="blip red" style="left: 68%; top: 30%"></span>
            <span class="blip gold" style="left: 74%; top: 58%"></span>
            <div class="scope-foot"><span class="mono">半径:{{ current?.radius }}m</span><span class="mono">目标:2 个</span></div>
          </div>
        </IndustrialPanel>

        <IndustrialPanel title="参数配置">
          <div class="cfg">
            <label>探测灵敏度(高敏度) <b class="c-cyan">高敏</b></label>
            <el-slider v-model="sensitivity" />
            <div class="frow">
              <div><label>报警阈值距离</label><el-input v-model="threshold" class="mono"><template #suffix>m</template></el-input></div>
              <div><label>扫描频率</label><el-select v-model="freq"><el-option label="50 Hz" value="50" /><el-option label="30 Hz" value="30" /></el-select></div>
            </div>
            <div class="cbtns">
              <el-button @click="restore">恢复默认</el-button>
              <el-button type="primary" @click="apply">下发配置</el-button>
            </div>
          </div>
        </IndustrialPanel>

        <IndustrialPanel title="实时点云情况">
          <template #extra><span class="c-muted">同步窗口</span></template>
          <BaseChart :option="cloudOption" height="140px" />
          <div class="cloud-foot"><span class="mono c-muted">最后更新:2026-07-21 08:50</span><el-button link type="primary">查看更多</el-button></div>
        </IndustrialPanel>
      </aside>
    </section>
  </div>
</template>

<script setup>
// 雷达传感器:资产列表 + 覆盖预览 + 参数配置 + 点云;radarApi 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Filter } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'
import { radarApi } from '@/api'

const rows = ref([
  { id: 'RDR-CR1-001', name: '主臂前向探测点', model: 'MMW-77G-Pro', position: '吊臂顶端', crane: 'CR-Tower-A', radius: 65, status: 'online', calibration: '已标定 [999d]' },
  { id: 'RDR-CR1-002', name: '副臂侧向探测点', model: 'MMW-77G-Std', position: '吊臂左侧', crane: 'CR-Tower-A', radius: 40, status: 'online', calibration: '已标定 [999d]' },
  { id: 'RDR-CR2-001', name: '主臂前向探测点', model: 'MMW-77G-Pro', position: '吊臂顶端', crane: 'CR-Tower-B', radius: 65, status: 'warning', calibration: '需复标 [超期]' },
  { id: 'RDR-CR3-001', name: '盲区补偿探测点', model: 'MMW-24G-Lite', position: '底盘后方', crane: 'CR-Gantry-1', radius: 15, status: 'offline', calibration: '失标' },
])
const current = ref(null)
const kw = ref('')
const page = ref(1)
const pageSize = 10
const filteredRows = computed(() => rows.value.filter(r => !kw.value || r.id.includes(kw.value)))
const pagedRows = computed(() => filteredRows.value.slice((page.value - 1) * pageSize, page.value * pageSize))

const sensitivity = ref(80)
const threshold = ref('15.0')
const freq = ref('50')

function toneClass(s) { return { online: 'c-success', warning: 'c-warning', offline: 'c-danger' }[s] || 'c-muted' }
function statusLabel(s) { return { online: '在线巡检', warning: '信号弱', offline: '离线' }[s] || s }
function calTone(c) { return c.includes('已标定') ? 'success' : c.includes('复标') ? 'warning' : 'danger' }
function restore() { sensitivity.value = 80; threshold.value = '15.0'; freq.value = '50'; ElMessage.info('已恢复默认参数') }
function apply() { ElMessage.success('配置已下发') }

const cloudOption = computed(() => ({
  grid: { top: 10, left: 6, right: 6, bottom: 6 },
  xAxis: { type: 'category', show: false, data: Array.from({ length: 12 }, (_, i) => i) },
  yAxis: { type: 'value', show: false },
  series: [{ type: 'bar', data: [30, 45, 60, 90, 70, 40, 35, 50, 100, 55, 40, 60].map((v, i) => ({ value: v, itemStyle: { color: i === 8 ? '#ef4444' : '#22d3ee', opacity: i === 8 ? 1 : .7 } })), barWidth: '55%' }],
}))

onMounted(async () => {
  try {
    const res = await radarApi.list({ page: 1, page_size: 100 })
    if (res?.list?.length) rows.value = res.list.map(r => ({
      id: r.id, name: r.name || '-', model: r.model || '-', position: r.position || '-', crane: r.crane || '-',
      radius: r.radius ?? 0, status: r.status || 'online', calibration: r.calibration || '已标定',
    }))
  } catch { /* 回退演示数据 */ }
  current.value = rows.value[0] || null
})
</script>

<style scoped>
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 14px; align-items: start; }
.toolbar { display: flex; gap: 8px; }
.idc { display: flex; flex-direction: column; }
.idc small { font-size: 11px; color: var(--qa-text-muted); }
.pager { display: flex; align-items: center; justify-content: space-between; padding: 12px 4px 4px; }

.right { display: grid; gap: 14px; align-content: start; }
.scope { position: relative; aspect-ratio: 1; border-radius: 8px; overflow: hidden; background: radial-gradient(circle at 50% 100%, rgba(34,211,238,.25), #071827 70%);
  border: 1px solid var(--qa-border-strong); background-image: repeating-radial-gradient(circle at 50% 100%, transparent 0 28px, rgba(34,211,238,.14) 29px 30px); }
.sweep { position: absolute; left: 0; bottom: 0; width: 100%; height: 100%;
  background: conic-gradient(from 270deg at 50% 100%, rgba(34,211,238,.35), transparent 90deg); }
.blip { position: absolute; width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 10px currentColor; }
.blip.red { background: var(--qa-danger); color: var(--qa-danger); }
.blip.gold { background: var(--qa-gold); color: var(--qa-gold); }
.scope-foot { position: absolute; left: 8px; right: 8px; bottom: 8px; display: flex; justify-content: space-between; font-size: 11px; color: var(--qa-text-2); }

.cfg label { display: block; margin-bottom: 8px; font-size: 12px; color: var(--qa-text-2); }
.cfg label b { float: right; font-weight: 600; }
.frow { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
.cbtns { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.cbtns .el-button { margin: 0; }
.cloud-foot { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; font-size: 11px; }

@media (max-width: 1200px) { .layout { grid-template-columns: 1fr; } }
</style>
