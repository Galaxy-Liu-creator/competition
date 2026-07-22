<template>
  <div class="page devtype">
    <section class="grid3">
      <!-- 左:分类目录 -->
      <IndustrialPanel>
        <template #header>
          <div class="ph"><h2><i></i>分类目录</h2><el-button link :icon="Plus" /></div>
        </template>
        <el-input v-model="treeKw" placeholder="搜索分类…" :prefix-icon="Search" class="mb" />
        <el-tree
          :data="tree" :props="{ label: 'label', children: 'children' }"
          :filter-node-method="filterNode" ref="treeRef" node-key="id"
          default-expand-all highlight-current @node-click="onNode"
        >
          <template #default="{ data }">
            <span class="tnode"><el-icon><component :is="data.icon || Folder" /></el-icon>{{ data.label }}</span>
          </template>
        </el-tree>
      </IndustrialPanel>

      <!-- 中:类型列表 -->
      <IndustrialPanel title="类型列表">
        <template #extra>
          <div class="toolbar">
            <el-input v-model="kw" placeholder="搜索类型…" :prefix-icon="Search" size="small" style="width: 160px" />
            <el-button size="small" :icon="Sort" />
            <el-button size="small" type="primary" :icon="Plus" @click="edit()" />
          </div>
        </template>
        <el-table :data="filteredTypes" highlight-current-row @current-change="r => r && edit(r)">
          <el-table-column label="类型编码" min-width="130"><template #default="{ row }"><b class="mono c-cyan">{{ row.code }}</b></template></el-table-column>
          <el-table-column prop="name" label="名称" min-width="130" />
          <el-table-column label="协议" width="130"><template #default="{ row }"><span class="qa-tag info">{{ row.protocol }}</span></template></el-table-column>
        </el-table>
      </IndustrialPanel>

      <!-- 右:编辑设备类型 -->
      <IndustrialPanel title="编辑设备类型">
        <template #extra><el-icon class="close" @click="form = null"><Close /></el-icon></template>
        <template v-if="form">
          <div class="sub"><i class="mk"></i>基础配置</div>
          <el-form :model="form" label-position="top">
            <el-form-item label="类型编码"><el-input v-model="form.code" disabled /></el-form-item>
            <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
            <div class="frow">
              <el-form-item label="协议">
                <el-select v-model="form.protocol">
                  <el-option label="MQTT-SN" value="MQTT-SN" />
                  <el-option label="MODBUS-TCP" value="MODBUS-TCP" />
                  <el-option label="HTTP-REST" value="HTTP-REST" />
                </el-select>
              </el-form-item>
              <el-form-item label="心跳(ms)"><el-input v-model="form.heartbeat" /></el-form-item>
            </div>
            <div class="sub"><i class="mk"></i>遥测数据模板<span class="raw">{ } 原始编辑</span></div>
            <el-input v-model="form.template" type="textarea" :rows="12" class="mono json" />
          </el-form>
          <div class="fbtns">
            <el-button @click="form = null">取消</el-button>
            <el-button type="primary" @click="save">保存修改</el-button>
          </div>
        </template>
        <el-empty v-else description="选择类型以编辑" :image-size="80" />
      </IndustrialPanel>
    </section>
  </div>
</template>

<script setup>
// 设备类型:分类树 + 类型列表 + 编辑面板;deviceTypeApi 失败回退演示数据
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Sort, Close, Folder } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { deviceTypeApi } from '@/api'

const tree = [
  { id: 1, label: '所有设备', children: [
    { id: 2, label: '重型机械', children: [
      { id: 3, label: '塔式起重机' },
      { id: 4, label: '龙门吊' },
      { id: 5, label: '移动式吊车' },
    ] },
    { id: 6, label: '传感器网络', children: [] },
  ] },
]
const treeRef = ref()
const treeKw = ref('')
watch(treeKw, v => treeRef.value?.filter(v))
function filterNode(value, data) { return !value || data.label.includes(value) }
function onNode() { /* 可按分类过滤 */ }

const kw = ref('')
const types = ref([
  { code: 'GC-9000-AX', name: '重型龙门吊 90T', protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('GC-9000-AX') },
  { code: 'GC-4500-BX', name: '中型龙门吊 45T', protocol: 'MODBUS-TCP', heartbeat: 5000, template: defaultJson('GC-4500-BX') },
  { code: 'GC-1200-CX', name: '轻型龙门吊 12T', protocol: 'HTTP-REST', heartbeat: 3000, template: defaultJson('GC-1200-CX') },
])
const filteredTypes = computed(() => types.value.filter(t => !kw.value || t.code.includes(kw.value) || t.name.includes(kw.value)))

function defaultJson(id) {
  return JSON.stringify({
    typeId: id, timestamp: 'ISO8601',
    payload: { load_weight_t: 'float32', wind_speed_ms: 'float32', hoist_height_m: 'float32', status: { is_overload: 'boolean', error_code: 'int16' } },
  }, null, 2)
}

const form = ref(null)
function edit(row) {
  form.value = row ? { ...row } : { code: '', name: '', protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('NEW-TYPE') }
}
async function save() {
  if (!form.value.name) { ElMessage.warning('请填写名称'); return }
  try {
    if (form.value.code) await deviceTypeApi.update(form.value.code, form.value)
    else await deviceTypeApi.create(form.value)
  } catch { /* 无后端本地生效 */ }
  const i = types.value.findIndex(t => t.code === form.value.code)
  if (i > -1) types.value[i] = { ...form.value }
  else types.value.unshift({ ...form.value, code: form.value.code || 'NEW-' + Date.now() })
  ElMessage.success('已保存修改')
}

onMounted(async () => {
  try {
    const res = await deviceTypeApi.list({ page: 1, page_size: 100 })
    if (res?.list?.length) types.value = res.list.map(t => ({
      code: t.code || t.id, name: t.name, protocol: t.protocol || 'MQTT-SN', heartbeat: t.heartbeat ?? 5000, template: t.template || defaultJson(t.code || t.id),
    }))
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.grid3 { display: grid; grid-template-columns: 280px minmax(0, 1fr) 380px; gap: 14px; align-items: start; }
.ph { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.ph h2 { display: flex; align-items: center; gap: 9px; margin: 0; font-size: 14px; }
.ph h2 i { width: 4px; height: 17px; background: linear-gradient(var(--qa-cyan), var(--qa-blue)); }
.mb { margin-bottom: 12px; }
.tnode { display: inline-flex; align-items: center; gap: 6px; }
:deep(.el-tree) { background: transparent; --el-tree-node-hover-bg-color: var(--qa-panel-3); color: var(--qa-text-2); }
:deep(.el-tree-node.is-current > .el-tree-node__content) { background: var(--qa-blue-dim); color: var(--qa-text); }

.toolbar { display: flex; gap: 8px; }
.close { cursor: pointer; color: var(--qa-text-muted); }
.close:hover { color: var(--qa-text); }
.sub { display: flex; align-items: center; gap: 8px; margin: 6px 0 14px; font-size: 13px; font-weight: 600; }
.sub .mk { width: 3px; height: 14px; background: var(--qa-cyan); }
.sub .raw { margin-left: auto; font-weight: 400; font-size: 12px; color: var(--qa-cyan); cursor: pointer; }
.frow { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.json :deep(.el-textarea__inner) { font-family: var(--qa-mono); font-size: 12px; background: #081426; }
.fbtns { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }

@media (max-width: 1300px) { .grid3 { grid-template-columns: 1fr; } }
</style>
