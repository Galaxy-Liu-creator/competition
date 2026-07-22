<template>
  <div class="page">
    <div class="vc-main">
      <!-- 左:大类树 -->
      <IndustrialPanel title="大类树结构" class="tree-panel">
        <template #extra><el-icon class="add" @click="ElMessage.info('新增大类开发中')"><Plus /></el-icon></template>
        <el-input v-model="treeKw" placeholder="搜索分类..." size="small" prefix-icon="Search" class="tree-search" />
        <div v-for="c in categories" :key="c.id" class="tree-item" :class="{ active: c.id === current.id }" @click="selectCat(c)">
          <el-icon><Folder /></el-icon><span>{{ c.name }} ({{ c.en }})</span>
        </div>
      </IndustrialPanel>

      <!-- 中:统计 + 子项列表 -->
      <div class="mid">
        <div class="stat-row mini">
          <StatCard label="总分类数" :value="stat.total" accent="#22d3ee" />
          <StatCard label="高风险类型" :value="stat.high" accent="#ef4444" />
          <StatCard label="中风险类型" :value="stat.mid" accent="#eab308" />
          <StatCard label="低风险类型" :value="stat.low" accent="#22c55e" />
        </div>
        <IndustrialPanel :title="current.name + '项目列表'">
          <template #extra><el-button type="primary" size="small" @click="ElMessage.info('新增子类开发中')">⊕ 新增子类</el-button></template>
          <el-table :data="current.items" @row-click="selectItem" highlight-current-row>
            <el-table-column label="编码 (CODE)" width="130"><template #default="{ row }"><span class="mono c-cyan">{{ row.code }}</span></template></el-table-column>
            <el-table-column prop="name" label="名称 (NAME)" min-width="180" />
            <el-table-column label="风险等级 (RISK)" width="130">
              <template #default="{ row }"><span class="qa-tag" :class="riskTag(row.level)">{{ riskText(row.level) }}</span></template>
            </el-table-column>
            <el-table-column label="状态 (STATUS)" width="100" align="center">
              <template #default="{ row }"><el-switch v-model="row.enabled" @change="onToggle(row)" @click.stop /></template>
            </el-table-column>
          </el-table>
        </IndustrialPanel>
      </div>

      <!-- 右:编辑详情 -->
      <IndustrialPanel title="编辑类目详情" class="edit-panel">
        <div v-if="editItem" class="edit">
          <h4>基础配置</h4>
          <div class="f"><label>分类名称</label><el-input v-model="editItem.name" /></div>
          <div class="f"><label>编码标识</label><el-input v-model="editItem.code" class="mono" /></div>
          <h4>关联统计</h4>
          <div class="rel-card"><span>关联违章项目数</span><b class="mono">{{ editItem.relCount || 142 }}</b></div>
          <h4>变更审计</h4>
          <ul class="audit">
            <li><b>状态变更:<span class="c-danger">已禁用</span></b><div class="au-meta"><span>管理员 A01</span><time class="mono">2023-10-27 18:32</time></div></li>
            <li><b>创建类目:{{ current.name }}</b><div class="au-meta"><span>系统初始化</span><time class="mono">2023-08-01 09:00</time></div></li>
          </ul>
          <div class="edit-actions"><el-button @click="editItem = null">取消</el-button><el-button type="primary" @click="save">保存变更</el-button></div>
        </div>
        <el-empty v-else description="点击左侧项目进行编辑" />
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Folder } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { violationCategoryApi } from '@/api'

const treeKw = ref('')
const stat = reactive({ total: 24, high: 8, mid: 12, low: 4 })
const categories = ref([
  { id: 1, name: '人员违章', en: 'Personnel', items: [
    { code: 'PV-001', name: '未按规定佩戴安全帽', level: 'high', enabled: true, relCount: 142 },
    { code: 'PV-002', name: '违规跨越作业区隔离带', level: 'mid', enabled: true, relCount: 88 },
  ] },
  { id: 2, name: '设备异常', en: 'Equipment', items: [
    { code: 'EQ-001', name: '吊钩超载运行', level: 'high', enabled: true, relCount: 56 },
    { code: 'EQ-002', name: '限位器失效', level: 'high', enabled: false, relCount: 12 },
  ] },
  { id: 3, name: '环境风险', en: 'Environment', items: [
    { code: 'EV-001', name: '大风超阈值作业', level: 'mid', enabled: true, relCount: 33 },
  ] },
])
const current = ref(categories.value[0])
const editItem = ref(null)

const riskTag = (l) => ({ high: 'danger', mid: 'warning', low: 'info' }[l] || 'info')
const riskText = (l) => ({ high: '高风险', mid: '中风险', low: '低风险' }[l] || '未知')

function selectCat(c) { current.value = c; editItem.value = null }
function selectItem(row) { editItem.value = row }
function onToggle(row) { ElMessage.success(`${row.name} 已${row.enabled ? '启用' : '禁用'}`) }
function save() { ElMessage.success('已保存变更'); editItem.value = null }

onMounted(async () => {
  try {
    const res = await violationCategoryApi.list({ page: 1, page_size: 50 })
    if (res.list?.length) { categories.value = res.list; current.value = res.list[0] }
  } catch { /* keep demo */ }
})
</script>

<style scoped>
.vc-main { display: grid; grid-template-columns: 260px minmax(0, 1fr) 300px; gap: 16px; }
.add { cursor: pointer; }
.tree-search { margin-bottom: 10px; }
.tree-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.tree-item:hover { background: var(--qa-panel-2); }
.tree-item.active { background: var(--qa-panel-3); color: var(--qa-cyan); }
.mid { display: flex; flex-direction: column; gap: 16px; }
.stat-row.mini { grid-template-columns: repeat(4, 1fr); }
.edit { display: flex; flex-direction: column; gap: 10px; }
.edit h4 { margin: 6px 0 0; font-size: 13px; color: var(--qa-text-2); }
.f { display: flex; flex-direction: column; gap: 5px; }
.f label { font-size: 12px; color: var(--qa-text-muted); }
.rel-card { display: flex; justify-content: space-between; align-items: center; padding: 12px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.rel-card b { font-size: 20px; color: var(--qa-cyan); }
.audit { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.audit li { padding: 10px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); font-size: 13px; }
.au-meta { display: flex; justify-content: space-between; margin-top: 6px; font-size: 11px; color: var(--qa-text-muted); }
.edit-actions { display: flex; gap: 10px; margin-top: 10px; }
.edit-actions .el-button { flex: 1; }
@media (max-width: 1200px) { .vc-main { grid-template-columns: 1fr; } .stat-row.mini { grid-template-columns: repeat(2, 1fr); } }
</style>
