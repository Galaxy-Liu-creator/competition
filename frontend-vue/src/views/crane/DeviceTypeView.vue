<template>
  <div class="page devtype">
    <section class="grid3 page-fill">
      <!-- 左:分类目录 -->
      <IndustrialPanel>
        <template #header>
          <div class="ph"><h2><i></i>分类目录</h2><el-button link :icon="Plus" @click="addCategory" /></div>
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
      <IndustrialPanel :title="'类型列表' + (activeCategory ? ' · ' + activeCategory : '')">
        <template #extra>
          <div class="toolbar">
            <el-input v-model="kw" placeholder="搜索类型…" :prefix-icon="Search" size="small" style="width: 160px" />
            <el-tooltip :content="sortTips[sortMode]" placement="top">
              <el-button size="small" :type="sortMode ? 'primary' : ''" :icon="Sort" @click="toggleSort" />
            </el-tooltip>
            <el-tooltip content="新增设备类型" placement="top">
              <el-button size="small" type="primary" :icon="Plus" @click="edit()" />
            </el-tooltip>
          </div>
        </template>
        <el-table :data="filteredTypes" highlight-current-row @current-change="r => r && edit(r)">
          <el-table-column label="类型编码" min-width="130"><template #default="{ row }"><b class="mono c-cyan">{{ row.code }}</b></template></el-table-column>
          <el-table-column prop="name" label="名称" min-width="130" />
          <el-table-column prop="category" label="分类" width="110" />
          <el-table-column label="协议" width="130"><template #default="{ row }"><span class="qa-tag info">{{ row.protocol }}</span></template></el-table-column>
        </el-table>
      </IndustrialPanel>

      <!-- 右:编辑设备类型 -->
      <IndustrialPanel :title="isNew ? '新增设备类型' : '编辑设备类型'">
        <template #extra><el-icon class="close" @click="form = null"><Close /></el-icon></template>
        <template v-if="form">
          <div class="sub"><i class="mk"></i>基础配置</div>
          <el-form :model="form" label-position="top">
            <el-form-item label="类型编码" required>
              <el-input v-model="form.code" :disabled="!isNew" placeholder="如 GC-6000-DX" />
            </el-form-item>
            <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="所属分类">
              <el-select v-model="form.category">
                <el-option v-for="c in leafCategories" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
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
            <el-button type="primary" @click="save">{{ isNew ? '创建类型' : '保存修改' }}</el-button>
          </div>
        </template>
        <el-empty v-else description="选择类型以编辑" :image-size="80" />
      </IndustrialPanel>
    </section>
  </div>
</template>

<script setup>
// 设备类型:分类树(可筛选) + 类型列表(排序/新增) + 编辑面板;deviceTypeApi 失败回退演示数据
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Sort, Close, Folder } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { deviceTypeApi } from '@/api'

const tree = ref([{ id: 1, label: '所有设备', children: [] }])
const treeRef = ref()
const treeKw = ref('')
watch(treeKw, v => treeRef.value?.filter(v))
function filterNode(value, data) { return !value || data.label.includes(value) }

// 分类树由类型数据的 category 动态重建,保证与列表分类一致(起重机类归入"重型机械")
const MACHINE_CATS = ['塔式起重机', '龙门吊', '移动式吊车']
let nextTreeId = 2
function rebuildTree() {
  const cats = [...new Set(types.value.map(t => t.category).filter(Boolean))]
  const machine = cats.filter(c => MACHINE_CATS.includes(c))
  const others = cats.filter(c => !MACHINE_CATS.includes(c))
  const children = []
  if (machine.length) children.push({ id: nextTreeId++, label: '重型机械', children: machine.map(l => ({ id: nextTreeId++, label: l })) })
  children.push(...others.map(l => ({ id: nextTreeId++, label: l })))
  tree.value = [{ id: 1, label: '所有设备', children }]
}

// 分类筛选:点父节点时匹配其全部子孙分类,点"所有设备"清除筛选
const activeCategory = ref('')
const activeCategorySet = ref(null)
function labelsUnder(node) {
  return [node.label, ...(node.children || []).flatMap(labelsUnder)]
}
function onNode(data) {
  if (data.label === '所有设备') {
    activeCategory.value = ''
    activeCategorySet.value = null
  } else {
    activeCategory.value = data.label
    activeCategorySet.value = new Set(labelsUnder(data))
  }
}
const leafCategories = computed(() => {
  const walk = n => (n.children?.length ? n.children.flatMap(walk) : n.label === '所有设备' ? [] : [n.label])
  return tree.value.flatMap(walk)
})

let nextTreeId2 = 1000
async function addCategory() {
  try {
    const { value } = await ElMessageBox.prompt('输入新分类名称', '新增分类', { inputPattern: /\S+/, inputErrorMessage: '分类名称不能为空' })
    const name = value.trim()
    tree.value[0].children.push({ id: nextTreeId2++, label: name, children: [] })
    ElMessage.success(`已新增分类「${name}」`)
  } catch { /* 取消 */ }
}

// 类型列表:关键字 + 分类筛选 + 排序(无 → 编码升序 → 编码降序)
const kw = ref('')
const sortMode = ref(0)
const sortTips = ['排序:默认', '排序:编码升序', '排序:编码降序']
function toggleSort() {
  sortMode.value = (sortMode.value + 1) % 3
  ElMessage.info(sortTips[sortMode.value])
}
const types = ref([
  { code: 'GC-9000-AX', name: '重型龙门吊 90T', category: '龙门吊', protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('GC-9000-AX') },
  { code: 'GC-4500-BX', name: '中型龙门吊 45T', category: '龙门吊', protocol: 'MODBUS-TCP', heartbeat: 5000, template: defaultJson('GC-4500-BX') },
  { code: 'GC-1200-CX', name: '轻型龙门吊 12T', category: '龙门吊', protocol: 'HTTP-REST', heartbeat: 3000, template: defaultJson('GC-1200-CX') },
  { code: 'TC-6015-A', name: '塔式起重机 60m', category: '塔式起重机', protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('TC-6015-A') },
  { code: 'TC-7020-B', name: '塔式起重机 70m', category: '塔式起重机', protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('TC-7020-B') },
  { code: 'QY-25K-M', name: '25T 汽车起重机', category: '移动式吊车', protocol: 'MODBUS-TCP', heartbeat: 5000, template: defaultJson('QY-25K-M') },
  { code: 'SN-RDR-77', name: '77GHz 毫米波雷达', category: '传感器网络', protocol: 'MQTT-SN', heartbeat: 3000, template: defaultJson('SN-RDR-77') },
])
const filteredTypes = computed(() => {
  const list = types.value.filter(t =>
    (!kw.value || t.code.includes(kw.value) || t.name.includes(kw.value)) &&
    (!activeCategorySet.value || activeCategorySet.value.has(t.category)),
  )
  if (!sortMode.value) return list
  const dir = sortMode.value === 1 ? 1 : -1
  return [...list].sort((a, b) => dir * a.code.localeCompare(b.code))
})

function defaultJson(id) {
  return JSON.stringify({
    typeId: id, timestamp: 'ISO8601',
    payload: { load_weight_t: 'float32', wind_speed_ms: 'float32', hoist_height_m: 'float32', status: { is_overload: 'boolean', error_code: 'int16' } },
  }, null, 2)
}

const form = ref(null)
const isNew = ref(false)
function edit(row) {
  isNew.value = !row
  form.value = row
    ? { ...row }
    : { code: '', name: '', category: activeCategory.value && leafCategories.value.includes(activeCategory.value) ? activeCategory.value : leafCategories.value[0], protocol: 'MQTT-SN', heartbeat: 5000, template: defaultJson('NEW-TYPE') }
}
async function save() {
  if (!form.value.code.trim()) { ElMessage.warning('请填写类型编码'); return }
  if (!form.value.name.trim()) { ElMessage.warning('请填写名称'); return }
  form.value.code = form.value.code.trim().toUpperCase()
  if (isNew.value && types.value.some(t => t.code === form.value.code)) {
    ElMessage.warning(`类型编码 ${form.value.code} 已存在`); return
  }
  try {
    if (isNew.value) {
      const created = await deviceTypeApi.create(form.value)
      if (created?.id != null) form.value._id = created.id
    } else if (form.value._id != null) {
      // 后端更新接口以数值 id 寻址,演示数据无 id 时仅本地生效
      await deviceTypeApi.update(form.value._id, form.value)
    }
  } catch { /* 无后端本地生效 */ }
  if (isNew.value) {
    types.value.unshift({ ...form.value })
    ElMessage.success(`已创建类型 ${form.value.code}`)
    edit(types.value[0])
  } else {
    const i = types.value.findIndex(t => t.code === form.value.code)
    if (i > -1) types.value[i] = { ...form.value }
    ElMessage.success('已保存修改')
  }
}

onMounted(async () => {
  rebuildTree()
  if (types.value.length) edit(types.value[0])
  try {
    const res = await deviceTypeApi.list({ page: 1, page_size: 100 })
    // 后端无 protocol/heartbeat/template 字段,按索引补演示值;category 缺省时按索引补齐
    if (res?.list?.length) {
      const protocols = ['MQTT-SN', 'MODBUS-TCP', 'HTTP-REST']
      const cats = leafCategories.value
      types.value = res.list.map((t, i) => ({
        _id: t.id,
        code: t.code || t.id, name: t.name || `设备类型 ${i + 1}`,
        category: t.category || cats[i % cats.length],
        protocol: t.protocol || protocols[i % 3],
        heartbeat: t.heartbeat ?? (i % 3 === 2 ? 3000 : 5000),
        template: t.template || defaultJson(t.code || t.id),
      }))
      rebuildTree()
      if (types.value.length) edit(types.value[0])
    }
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.grid3 { display: grid; grid-template-columns: 280px minmax(0, 1fr) 380px; gap: 14px; align-items: stretch; }
.grid3 > .panel { display: flex; flex-direction: column; }
.grid3 > .panel :deep(.body) { flex: 1; }
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
.json :deep(.el-textarea__inner) { font-family: var(--qa-mono); font-size: 12px; background: var(--qa-panel-2); }
.fbtns { display: flex; justify-content: flex-end; gap: 10px; margin-top: 14px; }

@media (max-width: 1300px) { .grid3 { grid-template-columns: 1fr; } }
</style>
