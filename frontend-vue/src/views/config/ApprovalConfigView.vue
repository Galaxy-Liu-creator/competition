<template>
  <div class="page">
    <div class="head">
      <h1>审批配置</h1>
      <div class="head-actions">
        <el-button @click="reset">重置</el-button>
        <el-button type="primary" @click="save">保存配置</el-button>
      </div>
    </div>

    <div class="ac-main">
      <!-- 左:业务流程列表 -->
      <IndustrialPanel title="业务流程" class="flow-list">
        <template #extra><el-icon class="add" @click="ElMessage.info('新增流程开发中')"><Plus /></el-icon></template>
        <el-input v-model="kw" placeholder="搜索流程..." size="small" class="mb" clearable />
        <div v-for="f in filteredFlows" :key="f.id" class="flow-item" :class="{ active: f.id === current.id }" @click="current = f">
          <div class="fi-head"><b>{{ f.name }}</b><span class="qa-tag" :class="f.published ? 'success' : 'info'">{{ f.published ? '已发布' : '草稿' }}</span></div>
          <div class="fi-meta">版本:{{ f.version }} · 更新:{{ f.updated }}</div>
        </div>
        <p v-if="!filteredFlows.length" class="flow-empty">无匹配流程</p>
      </IndustrialPanel>

      <!-- 右:审批流层级可视化 -->
      <IndustrialPanel :title="current.name + ' · ' + current.version" class="flow-canvas">
        <div class="canvas">
          <div class="grid-bg" />
          <div class="flow-track">
            <div class="node start">开始</div>
            <div class="arrow" />
            <div v-for="(step, i) in current.steps" :key="i" class="stage">
              <div class="node step" :class="{ risk: step.risk }">
                <div class="s-head"><el-icon><component :is="step.icon" /></el-icon>{{ step.name }}</div>
                <div class="s-row"><span>审批角色</span><b>{{ step.role }}</b></div>
                <div class="s-row"><span>审批方式</span><b>{{ step.mode }}</b></div>
              </div>
              <template v-if="i < current.steps.length - 1"><div class="arrow" :class="{ active: i === 0 }" /><div v-if="step.branch" class="branch"><i /><label>{{ step.branch }}</label></div></template>
            </div>
            <div class="arrow" />
            <div class="node end">归档</div>
          </div>
        </div>
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, User, Medal, WarningFilled } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { configApi } from '@/api'

const kw = ref('')
const flows = ref([
  { id: 1, name: '吊装作业许可', version: 'V2.4', updated: '2小时前', published: true, steps: [
    { name: '部门审核', role: '部门经理', mode: '或签(一人通过)', icon: markRaw(User), branch: '高风险' },
    { name: '安全总监审批', role: '安全总监', mode: '会签(全员通过)', icon: markRaw(Medal), risk: true },
    { name: '塔机主管确认', role: '塔机主管', mode: '或签', icon: markRaw(WarningFilled) },
  ] },
  { id: 2, name: '违章申诉处理', version: 'V1.1', updated: '2天前', published: true, steps: [
    { name: '班组初审', role: '班组长', mode: '或签', icon: markRaw(User) },
    { name: '安全员复核', role: '安全员', mode: '会签', icon: markRaw(Medal), risk: true },
  ] },
  { id: 3, name: '设备维保申请', version: 'V3.0', updated: '1周前', published: false, steps: [
    { name: '设备主管审批', role: '设备主管', mode: '或签', icon: markRaw(User) },
  ] },
])
const current = ref(flows.value[0])
// 关键词过滤业务流程列表(名称/版本)
const filteredFlows = computed(() => {
  const keyword = kw.value.trim().toLowerCase()
  return flows.value.filter((f) => !keyword || `${f.name} ${f.version}`.toLowerCase().includes(keyword))
})

onMounted(async () => { try { const r = await configApi.get('approval'); if (r?.flows?.length) flows.value = r.flows } catch { /* keep demo */ } })
async function save() { try { await configApi.save('approval', { flows: flows.value }); ElMessage.success('审批配置已保存') } catch { ElMessage.success('审批配置已保存(演示态)') } }
function reset() { ElMessage.info('已重置') }
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.head h1 { margin: 0; font-size: 20px; }
.head-actions { display: flex; gap: 10px; }
.ac-main { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 16px; }
.add { cursor: pointer; }
.mb { margin-bottom: 10px; }
.flow-item { padding: 12px; margin-bottom: 10px; border: 1px solid var(--qa-border); border-radius: 6px; cursor: pointer; }
.flow-item.active { border-color: var(--qa-border-active); background: var(--qa-panel-3); }
.fi-head { display: flex; justify-content: space-between; align-items: center; }
.fi-head b { color: var(--qa-cyan); }
.fi-meta { margin-top: 6px; font-size: 11px; color: var(--qa-text-muted); }
.flow-empty { margin: 4px 0; font-size: 12px; color: var(--qa-text-muted); text-align: center; }
.canvas { position: relative; min-height: 520px; padding: 20px; overflow-x: auto; }
.grid-bg { position: absolute; inset: 0; background-image: radial-gradient(rgba(56,119,157,.15) 1px, transparent 1px); background-size: 22px 22px; }
.flow-track { position: relative; z-index: 2; display: flex; align-items: center; gap: 4px; min-width: max-content; padding: 40px 0; }
.node { padding: 12px 16px; border: 1px solid var(--qa-border-strong); border-radius: 8px; background: var(--qa-panel-2); font-size: 12px; }
.node.start, .node.end { border-radius: 20px; color: var(--qa-text-2); }
.node.step { min-width: 180px; border-color: var(--qa-cyan); box-shadow: 0 0 14px rgba(34,211,238,.15); }
.node.step.risk { border-color: var(--qa-warning); }
.s-head { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: var(--qa-cyan); margin-bottom: 8px; }
.node.step.risk .s-head { color: var(--qa-warning); }
.s-row { display: flex; justify-content: space-between; gap: 16px; padding: 3px 0; }
.s-row span { color: var(--qa-text-muted); }
.arrow { width: 40px; height: 2px; background: var(--qa-border-strong); position: relative; flex-shrink: 0; }
.arrow::after { content: ''; position: absolute; right: 0; top: -3px; border: 4px solid transparent; border-left-color: var(--qa-border-strong); }
.arrow.active { background: var(--qa-cyan); } .arrow.active::after { border-left-color: var(--qa-cyan); }
.stage { display: flex; align-items: center; gap: 4px; }
.branch { display: flex; flex-direction: column; align-items: center; font-size: 11px; color: var(--qa-warning); }
.branch i { width: 12px; height: 12px; transform: rotate(45deg); border: 1px solid var(--qa-warning); margin-bottom: 4px; }
@media (max-width: 1000px) { .ac-main { grid-template-columns: 1fr; } }
</style>
