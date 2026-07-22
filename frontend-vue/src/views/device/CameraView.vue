<template>
  <div class="page">
    <!-- 顶部统计卡 -->
    <div class="stat-row">
      <StatCard label="摄像头总数" :value="stats.total" suffix="台" accent="#22d3ee" />
      <StatCard label="在线率" :value="stats.onlineRate" suffix="%" accent="#22c55e" />
      <StatCard label="今日告警" :value="stats.alarm" suffix="起" accent="#ef4444" />
      <StatCard label="存储状态" :value="stats.storage" suffix="正常" accent="#22c55e" />
    </div>

    <!-- 筛选栏 -->
    <IndustrialPanel compact>
      <div class="filterbar">
        <el-input v-model="query.keyword" placeholder="搜索设备名称或编号" clearable @keyup.enter="load" />
        <el-select v-model="query.status" placeholder="所有状态" clearable>
          <el-option label="在线" value="online" />
          <el-option label="预警" value="warning" />
          <el-option label="离线" value="offline" />
        </el-select>
        <el-select v-model="query.type" placeholder="所有类型" clearable>
          <el-option label="枪机" value="bullet" />
          <el-option label="球机" value="dome" />
          <el-option label="全景" value="panoramic" />
        </el-select>
        <el-button @click="load">筛选</el-button>
        <div class="spacer" />
        <el-button type="primary" @click="onAdd">+ 新增摄像头</el-button>
      </div>
    </IndustrialPanel>

    <!-- 主体:列表 + 详情 -->
    <div class="main">
      <IndustrialPanel title="设备列表" class="list-panel">
        <template #extra>显示 {{ list.length }}/{{ stats.total }} 台</template>
        <el-table :data="list" highlight-current-row @current-change="onSelect" height="520">
          <el-table-column label="状态" width="72">
            <template #default="{ row }">
              <span class="status-dot" :class="dotColor(row.status)" />
            </template>
          </el-table-column>
          <el-table-column label="设备名称" min-width="180">
            <template #default="{ row }">
              <div class="cam-cell">
                <el-icon class="cam-ico" :class="dotColor(row.status)"><VideoCamera /></el-icon>
                <div>
                  <b>{{ row.name }}</b>
                  <small>{{ row.location }}</small>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="连接状态" width="120">
            <template #default="{ row }">
              <span class="qa-tag" :class="tagType(row.status)">{{ statusText(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="IP 地址" width="150">
            <template #default="{ row }"><span class="mono">{{ row.ip }}</span></template>
          </el-table-column>
          <el-table-column label="运行状态" min-width="120">
            <template #default="{ row }"><span class="text-2">{{ row.runtime || '正常运行' }}</span></template>
          </el-table-column>
          <el-table-column label="操作" width="130" align="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="onSelect(row)">详情</el-button>
              <el-button link type="danger" @click="onDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </IndustrialPanel>

      <!-- 右侧详情 -->
      <IndustrialPanel title="设备详情与状态" class="detail-panel">
        <div v-if="current" class="detail">
          <div class="d-row"><span>设备名称</span><b>{{ current.name }}</b></div>
          <div class="d-row"><span>设备编号</span><b class="mono">{{ current.code || 'CAM-HJ-0921' }}</b></div>
          <div class="d-row"><span>IP 地址</span><b class="mono">{{ current.ip }}</b></div>
          <div class="d-row"><span>运行状态</span>
            <span class="qa-tag" :class="tagType(current.status)">{{ statusText(current.status) }} · {{ current.runtime || '正常' }}</span>
          </div>
          <div class="divider" />
          <h4>最近告警</h4>
          <ul class="alarm-list">
            <li v-for="a in current.alarms || demoAlarms" :key="a.time">
              <span class="status-dot" :class="a.level === 'danger' ? 'c-danger' : 'c-success'" />
              <div><b>{{ a.text }}</b><small class="mono">{{ a.time }}</small></div>
            </li>
          </ul>
          <div class="detail-actions">
            <el-button @click="ElMessage.success('已下发重启指令')">重启设备</el-button>
            <el-button type="primary" @click="ElMessage.info('配置面板开发中')">配置参数</el-button>
          </div>
        </div>
        <el-empty v-else description="请选择设备查看详情" />
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { cameraApi } from '@/api'

const stats = reactive({ total: 156, onlineRate: 97.4, alarm: 3, storage: 100 })
const query = reactive({ keyword: '', status: '', type: '' })
const list = ref([])
const current = ref(null)

const demo = [
  { id: 1, name: '塔吊主吊臂摄像头', location: '2# 作业区 · 主臂', code: 'CAM-HJ-0921', ip: '192.168.18.101', status: 'online', runtime: '正常', alarms: [{ text: '闯入人员告警', level: 'danger', time: '2026-07-21 10:30:12' }, { text: '识别恢复正常', level: 'success', time: '2026-07-21 09:42:15' }] },
  { id: 2, name: '南侧围栏球机', location: '南侧围栏 · 周界', code: 'CAM-HJ-0722', ip: '192.168.18.104', status: 'online', runtime: '正常' },
  { id: 3, name: '落区枪机', location: 'C区 落区', code: 'CAM-HJ-0733', ip: '192.168.18.117', status: 'warning', runtime: '信号弱' },
  { id: 4, name: '车辆通道全景机', location: '车辆通道 · 出入口', code: 'CAM-HJ-0644', ip: '192.168.18.203', status: 'offline', runtime: '离线' },
]
const demoAlarms = [{ text: '闯入人员告警', level: 'danger', time: '2026-07-21 10:30:12' }, { text: '识别恢复正常', level: 'success', time: '2026-07-21 09:42:15' }]

const dotColor = (s) => ({ online: 'c-success', warning: 'c-warning', offline: 'c-muted' }[s] || 'c-muted')
const tagType = (s) => ({ online: 'success', warning: 'warning', offline: 'info' }[s] || 'info')
const statusText = (s) => ({ online: '在线', warning: '预警', offline: '离线' }[s] || '未知')

async function load() {
  try {
    const res = await cameraApi.list({ ...query, page: 1, page_size: 50 })
    list.value = (res.list && res.list.length) ? res.list : demo
  } catch { list.value = demo }
  if (!current.value) current.value = list.value[0]
}
const onSelect = (row) => { if (row) current.value = row }
function onAdd() { ElMessage.info('新增摄像头表单开发中') }
async function onDelete(row) {
  await ElMessageBox.confirm(`确认删除摄像头「${row.name}」?`, '删除确认', { type: 'warning' })
  try { await cameraApi.remove(row.id) } catch { /* 演示忽略 */ }
  list.value = list.value.filter(i => i.id !== row.id)
  ElMessage.success('已删除')
}
onMounted(load)
</script>

<style scoped>
.main { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; }
.filterbar { display: flex; align-items: center; gap: 12px; }
.filterbar .el-input { max-width: 300px; }
.filterbar .el-select { width: 150px; }
.spacer { flex: 1; }
.cam-cell { display: flex; align-items: center; gap: 10px; }
.cam-ico { font-size: 20px; }
.cam-cell b { display: block; font-size: 13px; }
.cam-cell small { color: var(--qa-text-muted); font-size: 11px; }
.detail { display: flex; flex-direction: column; gap: 12px; }
.d-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.d-row span { color: var(--qa-text-2); }
.divider { height: 1px; background: var(--qa-border); margin: 4px 0; }
.detail h4 { margin: 0; font-size: 13px; color: var(--qa-text-2); }
.alarm-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.alarm-list li { display: flex; gap: 10px; align-items: flex-start; }
.alarm-list b { display: block; font-size: 13px; }
.alarm-list small { color: var(--qa-text-muted); font-size: 11px; }
.detail-actions { display: flex; gap: 10px; margin-top: 8px; }
.detail-actions .el-button { flex: 1; }
@media (max-width: 1100px) { .main { grid-template-columns: 1fr; } }
</style>
