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
        <el-input v-model="query.keyword" placeholder="搜索设备名称或编号" clearable @keyup.enter="applyFilter" @clear="applyFilter" />
        <el-select v-model="query.status" placeholder="所有状态" clearable @change="applyFilter">
          <el-option label="在线" value="online" />
          <el-option label="预警" value="warning" />
          <el-option label="离线" value="offline" />
        </el-select>
        <el-select v-model="query.type" placeholder="所有类型" clearable @change="applyFilter">
          <el-option label="周界枪机" value="perimeter" />
          <el-option label="吊钩球机" value="hook" />
          <el-option label="驾驶室摄像" value="cab" />
        </el-select>
        <el-button @click="applyFilter">筛选</el-button>
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
                  <small>{{ row.location }} · {{ typeText(row.type) }}</small>
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
          <div class="d-row"><span>设备编号</span><b class="mono">{{ current.code || '-' }}</b></div>
          <div class="d-row"><span>设备类型</span><b>{{ typeText(current.type) }}</b></div>
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
            <el-button type="primary" @click="openConfig">配置参数</el-button>
          </div>
        </div>
        <el-empty v-else description="请选择设备查看详情" />
      </IndustrialPanel>
    </div>

    <!-- 配置参数对话框 -->
    <el-dialog v-model="cfgVisible" title="摄像头参数配置" width="520px">
      <el-form ref="cfgFormRef" :model="cfgForm" :rules="camRules" label-width="92px">
        <el-form-item label="设备名称" prop="name"><el-input v-model="cfgForm.name" /></el-form-item>
        <el-form-item label="设备编号"><el-input v-model="cfgForm.code" disabled class="mono" /></el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="cfgForm.type" style="width: 100%">
            <el-option label="周界枪机" value="perimeter" />
            <el-option label="吊钩球机" value="hook" />
            <el-option label="驾驶室摄像" value="cab" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址" prop="ip"><el-input v-model="cfgForm.ip" class="mono" placeholder="192.168.1.10" /></el-form-item>
        <el-form-item label="所在区域"><el-input v-model="cfgForm.location" placeholder="如 A区-东侧" /></el-form-item>
        <el-form-item label="分辨率/型号"><el-input v-model="cfgForm.resolution" placeholder="如 DS-2CD3T46WDV3" /></el-form-item>
        <el-form-item label="RTSP 地址"><el-input v-model="cfgForm.rtsp" class="mono" placeholder="rtsp://…" /></el-form-item>
        <el-form-item label="运行状态">
          <el-radio-group v-model="cfgForm.status">
            <el-radio-button value="online">在线</el-radio-button>
            <el-radio-button value="warning">预警</el-radio-button>
            <el-radio-button value="offline">离线</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cfgVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveConfig">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 新增摄像头对话框 -->
    <el-dialog v-model="addVisible" title="新增摄像头" width="520px">
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="92px">
        <el-form-item label="设备编号" prop="code"><el-input v-model="addForm.code" class="mono" placeholder="如 CAM-13" /></el-form-item>
        <el-form-item label="设备名称" prop="name"><el-input v-model="addForm.name" placeholder="如 D区周界枪机" /></el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="addForm.type" style="width: 100%">
            <el-option label="周界枪机" value="perimeter" />
            <el-option label="吊钩球机" value="hook" />
            <el-option label="驾驶室摄像" value="cab" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址" prop="ip"><el-input v-model="addForm.ip" class="mono" placeholder="192.168.1.30" /></el-form-item>
        <el-form-item label="所在区域"><el-input v-model="addForm.location" placeholder="如 D区-北侧" /></el-form-item>
        <el-form-item label="分辨率/型号"><el-input v-model="addForm.resolution" placeholder="如 DS-2CD3T46WDV3" /></el-form-item>
        <el-form-item label="初始状态">
          <el-radio-group v-model="addForm.status">
            <el-radio-button value="online">在线</el-radio-button>
            <el-radio-button value="offline">离线</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAdd">确认新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoCamera } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { cameraApi } from '@/api'

const stats = reactive({ total: 0, onlineRate: 0, alarm: 3, storage: 100 })
const query = reactive({ keyword: '', status: '', type: '' })
const allRows = ref([])
const list = ref([])
const current = ref(null)

const demo = [
  { id: 1, name: '塔吊主吊臂摄像头', location: '2# 作业区 · 主臂', code: 'CAM-HJ-0921', type: 'hook', resolution: 'DS-2DC7523IW', ip: '192.168.18.101', status: 'online', runtime: '正常', alarms: [{ text: '闯入人员告警', level: 'danger', time: '2026-07-21 10:30:12' }, { text: '识别恢复正常', level: 'success', time: '2026-07-21 09:42:15' }] },
  { id: 2, name: '南侧围栏球机', location: '南侧围栏 · 周界', code: 'CAM-HJ-0722', type: 'perimeter', resolution: 'DS-2CD3T46WDV3', ip: '192.168.18.104', status: 'online', runtime: '正常' },
  { id: 3, name: '落区枪机', location: 'C区 落区', code: 'CAM-HJ-0733', type: 'perimeter', resolution: 'DS-2CD3T46WDV3', ip: '192.168.18.117', status: 'warning', runtime: '信号弱' },
  { id: 4, name: '车辆通道全景机', location: '车辆通道 · 出入口', code: 'CAM-HJ-0644', type: 'cab', resolution: 'DS-2CD2T47G2', ip: '192.168.18.203', status: 'offline', runtime: '离线' },
]
const demoAlarms = [{ text: '闯入人员告警', level: 'danger', time: '2026-07-21 10:30:12' }, { text: '识别恢复正常', level: 'success', time: '2026-07-21 09:42:15' }]

const dotColor = (s) => ({ online: 'c-success', warning: 'c-warning', offline: 'c-muted' }[s] || 'c-muted')
const tagType = (s) => ({ online: 'success', warning: 'warning', offline: 'info' }[s] || 'info')
const statusText = (s) => ({ online: '在线', warning: '预警', offline: '离线' }[s] || '未知')
const typeText = (t) => ({ perimeter: '周界枪机', hook: '吊钩球机', cab: '驾驶室摄像' }[t] || '通用')
const runtimeText = (s) => ({ online: '正常', warning: '信号弱', offline: '离线' }[s] || '正常')

// 后端行(work_zone/rtsp_url)与演示行统一映射为页面字段
const mapRow = (r) => ({
  id: r.id,
  name: r.name,
  code: r.code || '',
  type: r.type || 'perimeter',
  location: r.location || r.work_zone || '未分区',
  ip: r.ip || '',
  resolution: r.resolution || '',
  rtsp: r.rtsp || r.rtsp_url || '',
  status: r.status || 'online',
  runtime: r.runtime || runtimeText(r.status),
  alarms: r.alarms,
})

async function load() {
  try {
    const res = await cameraApi.list({ page: 1, page_size: 200 })
    allRows.value = (res.list && res.list.length) ? res.list.map(mapRow) : demo.map(mapRow)
  } catch { allRows.value = demo.map(mapRow) }
  refreshStats()
  applyFilter()
}

// 统一客户端过滤:后端在线与纯前端回退两种模式下筛选均生效
function applyFilter() {
  const kw = query.keyword.trim().toLowerCase()
  list.value = allRows.value.filter((r) =>
    (!kw || `${r.name} ${r.code} ${r.ip} ${r.location}`.toLowerCase().includes(kw)) &&
    (!query.status || r.status === query.status) &&
    (!query.type || r.type === query.type))
  if (!list.value.includes(current.value)) current.value = list.value[0] || null
}

function refreshStats() {
  stats.total = allRows.value.length
  const online = allRows.value.filter((r) => r.status === 'online').length
  stats.onlineRate = stats.total ? Math.round((online / stats.total) * 1000) / 10 : 0
  const alarmCount = allRows.value.reduce((n, r) => n + (r.alarms ? r.alarms.filter((a) => a.level === 'danger').length : 0), 0)
  stats.alarm = alarmCount || 3
}

const onSelect = (row) => { if (row) current.value = row }

// ---------- 配置参数 ----------
const cfgVisible = ref(false)
const cfgFormRef = ref()
const saving = ref(false)
const cfgForm = reactive({ id: null, name: '', code: '', type: 'perimeter', ip: '', location: '', resolution: '', rtsp: '', status: 'online' })
const ipRule = { pattern: /^(\d{1,3}\.){3}\d{1,3}$/, message: 'IP 地址格式不正确', trigger: 'blur' }
const camRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  ip: [{ required: true, message: '请输入 IP 地址', trigger: 'blur' }, ipRule],
}

function openConfig() {
  if (!current.value) return
  Object.assign(cfgForm, {
    id: current.value.id,
    name: current.value.name,
    code: current.value.code,
    type: current.value.type,
    ip: current.value.ip,
    location: current.value.location,
    resolution: current.value.resolution,
    rtsp: current.value.rtsp,
    status: current.value.status,
  })
  cfgVisible.value = true
}

async function saveConfig() {
  await cfgFormRef.value.validate()
  saving.value = true
  try {
    await cameraApi.update(cfgForm.id, {
      name: cfgForm.name, type: cfgForm.type, ip: cfgForm.ip,
      work_zone: cfgForm.location, resolution: cfgForm.resolution,
      rtsp_url: cfgForm.rtsp, status: cfgForm.status,
    })
  } catch { /* 后端不可用时仅更新本地演示数据 */ }
  const row = allRows.value.find((r) => r.id === cfgForm.id)
  if (row) {
    Object.assign(row, {
      name: cfgForm.name, type: cfgForm.type, ip: cfgForm.ip,
      location: cfgForm.location, resolution: cfgForm.resolution,
      rtsp: cfgForm.rtsp, status: cfgForm.status, runtime: runtimeText(cfgForm.status),
    })
  }
  refreshStats()
  applyFilter()
  saving.value = false
  cfgVisible.value = false
  ElMessage.success('配置已保存并下发')
}

// ---------- 新增摄像头 ----------
const addVisible = ref(false)
const addFormRef = ref()
const addForm = reactive({ code: '', name: '', type: 'perimeter', ip: '', location: '', resolution: '', status: 'online' })
const addRules = {
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  ip: [{ required: true, message: '请输入 IP 地址', trigger: 'blur' }, ipRule],
}

function onAdd() {
  Object.assign(addForm, {
    code: `CAM-${String(allRows.value.length + 1).padStart(2, '0')}`,
    name: '', type: 'perimeter', ip: '', location: '', resolution: '', status: 'online',
  })
  addVisible.value = true
}

async function saveAdd() {
  await addFormRef.value.validate()
  saving.value = true
  const payload = {
    code: addForm.code, name: addForm.name, type: addForm.type, ip: addForm.ip,
    work_zone: addForm.location, resolution: addForm.resolution,
    rtsp_url: addForm.ip ? `rtsp://${addForm.ip}:554/Streaming/Channels/101` : '',
    status: addForm.status,
  }
  let created = null
  try { created = await cameraApi.create(payload) } catch (e) {
    if (e?.response?.status === 409) {
      saving.value = false
      ElMessage.error('设备编号已存在，请更换编号')
      return
    }
    /* 后端不可用时本地插入演示数据 */
  }
  const row = mapRow(created || { ...payload, id: Date.now() })
  allRows.value.unshift(row)
  refreshStats()
  applyFilter()
  current.value = row
  saving.value = false
  addVisible.value = false
  ElMessage.success(`摄像头「${row.name}」已接入`)
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确认删除摄像头「${row.name}」?`, '删除确认', { type: 'warning' })
  try { await cameraApi.remove(row.id) } catch { /* 演示忽略 */ }
  allRows.value = allRows.value.filter((i) => i.id !== row.id)
  refreshStats()
  applyFilter()
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
