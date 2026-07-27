<template>
  <div class="page">
    <IndustrialPanel title="审计日志" compact>
      <div class="filterbar">
        <el-input v-model="query.operator" placeholder="操作人" clearable style="width: 150px" />
        <el-select v-model="query.module" placeholder="全部模块" clearable style="width: 150px">
          <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
        </el-select>
        <el-date-picker v-model="query.dates" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width: 260px" />
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="onExport">导出</el-button>
      </div>
    </IndustrialPanel>

    <IndustrialPanel title="操作记录">
      <template #extra>共 {{ total }} 条</template>
      <el-table :data="list" height="560">
        <el-table-column prop="operator" label="操作人" width="140">
          <template #default="{ row }"><b>{{ row.operator }}</b></template>
        </el-table-column>
        <el-table-column label="动作" width="120">
          <template #default="{ row }"><span class="qa-tag" :class="actionTag(row.action)">{{ row.action }}</span></template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="140" />
        <el-table-column prop="detail" label="详情" min-width="280" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP 地址" width="150"><template #default="{ row }"><span class="mono">{{ row.ip }}</span></template></el-table-column>
        <el-table-column prop="time" label="时间" width="180"><template #default="{ row }"><span class="mono text-2">{{ row.time }}</span></template></el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination background layout="prev, pager, next, total" :total="total" :page-size="query.page_size" :current-page="query.page" @current-change="p => { query.page = p; load() }" />
      </div>
    </IndustrialPanel>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { auditLogApi } from '@/api'
import { exportExcel } from '@/utils/exportExcel'

const modules = ['设备管理', '风险处置', '基础配置', '违章类型', '音柱管理', '用户登录']
const query = reactive({ operator: '', module: '', dates: null, page: 1, page_size: 12 })
const list = ref([])
const total = ref(0)

const actions = ['新增', '修改', '删除', '登录', '下发', '审批']
const gen = () => Array.from({ length: 60 }, (_, i) => ({
  id: i + 1,
  operator: ['管理员', '张安全', '李工', '系统任务'][i % 4],
  action: actions[i % actions.length],
  module: modules[i % modules.length],
  detail: `${actions[i % actions.length]}操作:${modules[i % modules.length]} 记录 #${1000 + i}`,
  ip: `192.168.${1 + (i % 5)}.${100 + (i % 50)}`,
  time: `2026-07-${String(21 - (i % 10)).padStart(2, '0')} ${String(8 + (i % 12)).padStart(2, '0')}:${String(i % 60).padStart(2, '0')}:15`,
}))
const all = gen()

const actionTag = (a) => ({ 删除: 'danger', 修改: 'warning', 新增: 'success', 审批: 'cyan', 下发: 'blue' }[a] || 'info')

const fmtDate = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return undefined
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
// 后端行 created_at(ISO 或 "YYYY-MM-DD HH:MM")映射为页面 time 字段
const mapRow = (r) => ({ ...r, time: r.time || String(r.created_at || '').replace('T', ' ').slice(0, 19) })

const filterParams = () => ({
  operator: query.operator || undefined,
  module: query.module || undefined,
  start: query.dates?.[0] ? fmtDate(query.dates[0]) : undefined,
  end: query.dates?.[1] ? fmtDate(query.dates[1]) : undefined,
})

// 回退演示数据的客户端过滤(操作人/模块/日期区间)
function localFiltered() {
  let data = all
  if (query.operator) data = data.filter(i => i.operator.includes(query.operator))
  if (query.module) data = data.filter(i => i.module === query.module)
  if (query.dates?.length === 2) {
    const start = fmtDate(query.dates[0])
    const end = fmtDate(query.dates[1])
    data = data.filter(i => { const day = String(i.time).slice(0, 10); return day >= start && day <= end })
  }
  return data
}

async function load() {
  try {
    const res = await auditLogApi.list({ ...filterParams(), page: query.page, page_size: query.page_size })
    if (Array.isArray(res.list)) { list.value = res.list.map(mapRow); total.value = res.total; return }
    throw new Error('empty')
  } catch {
    const data = localFiltered()
    total.value = data.length
    const startIdx = (query.page - 1) * query.page_size
    list.value = data.slice(startIdx, startIdx + query.page_size)
  }
}

function onSearch() { query.page = 1; load() }

async function onExport() {
  let rows
  try {
    const res = await auditLogApi.list({ ...filterParams(), page: 1, page_size: 200 })
    if (!Array.isArray(res.list)) throw new Error('empty')
    rows = res.list.map(mapRow)
  } catch { rows = localFiltered() }
  if (!rows.length) { ElMessage.info('当前筛选条件下暂无日志可导出'); return }
  exportExcel({
    filename: '审计日志',
    sheets: [{
      name: '操作记录',
      columns: [
        { label: '操作人', key: 'operator', width: 14 },
        { label: '动作', key: 'action', width: 10 },
        { label: '模块', key: 'module', width: 14 },
        { label: '详情', key: 'detail', width: 44 },
        { label: 'IP 地址', key: 'ip', width: 16 },
        { label: '时间', key: 'time', width: 20 },
      ],
      rows,
    }],
  })
  ElMessage.success(`已导出 ${rows.length} 条审计日志`)
}
onMounted(load)
</script>

<style scoped>
.filterbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.pager { display: flex; justify-content: flex-end; margin-top: 14px; }
</style>
