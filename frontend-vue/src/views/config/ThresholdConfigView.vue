<template>
  <div class="page">
    <div class="head">
      <div>
        <h1>全局阈值参数配置</h1>
        <p class="sub">管理并分发各基础节点的安全告警阈值参数</p>
      </div>
      <div class="head-actions">
        <el-button @click="reset">↺ 目标撤销</el-button>
        <el-button @click="save">保存配置</el-button>
        <el-button type="primary" @click="publish">发布生效</el-button>
      </div>
    </div>

    <IndustrialPanel v-for="group in groups" :key="group.name" :title="group.title">
      <template #extra>{{ group.en }}</template>
      <el-table :data="group.items">
        <el-table-column prop="name" label="参数名称" min-width="160" />
        <el-table-column prop="unit" label="单位" width="70" />
        <el-table-column label="推荐默认值" width="150"><template #default="{ row }"><el-input v-model="row.def" size="small" /></template></el-table-column>
        <el-table-column label="设备置值" width="170">
          <template #default="{ row }">
            <div class="val-cell">
              <el-input v-model="row.value" size="small" :class="{ over: isOver(row) }" placeholder="继承默认" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="range" label="建议范围" width="130"><template #default="{ row }"><span class="mono text-muted">{{ row.range }}</span></template></el-table-column>
        <el-table-column label="状态提示" min-width="140">
          <template #default="{ row }">
            <span v-if="isOver(row)" class="qa-tag danger">⊘ 超出安全限制</span>
            <span v-else-if="isWarn(row)" class="qa-tag warning">△ 易触发频繁影响</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="" width="70" align="right">
          <template #default="{ row }"><el-slider v-model="row.sliderVal" :min="0" :max="row.max || 100" size="small" @input="v => syncSlider(row, v)" style="display:none" /><el-button link type="primary" @click="row.value = row.def">继承</el-button></template>
        </el-table-column>
      </el-table>
    </IndustrialPanel>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { configApi } from '@/api'

const groups = ref([
  { name: 'ops', title: '运行安全参数', en: '(Operating Safety)', items: [
    { name: '风速告警阈值', unit: 'm/s', def: '13.8', value: '12.5', range: '10.0 - 15.0', hardMax: 15 },
    { name: '最大额定载重', unit: 't', def: '500.0', value: '', range: '≤ 600.0', hardMax: 600 },
    { name: '结构极限高度', unit: 'm', def: '85.5', value: '98.0', range: '≤ 85.0', hardMax: 85 },
  ] },
  { name: 'sense', title: '感知与监控', en: '(Sensing & Monitoring)', items: [
    { name: '雷达安全喊话半径', unit: 'm', def: '15.0', value: '', range: '10.0 - 20.0', hardMax: 20 },
    { name: 'AI 识别置信度阈值', unit: '%', def: '85', value: '95', range: '≥ 80', hardMax: 100, warnHigh: 90 },
    { name: '心跳超时阈值', unit: 's', def: '30', value: '', range: '15 - 60', hardMax: 60 },
  ] },
])

const num = (v) => parseFloat(v)
const isOver = (row) => row.value !== '' && !isNaN(num(row.value)) && num(row.value) > row.hardMax
const isWarn = (row) => row.value !== '' && !isOver(row) && row.warnHigh && num(row.value) >= row.warnHigh
function syncSlider() {}

onMounted(async () => { try { const r = await configApi.get('threshold'); if (r?.groups?.length) groups.value = r.groups } catch { /* keep demo */ } })
async function save() { try { await configApi.save('threshold', { groups: groups.value }); ElMessage.success('阈值配置已保存') } catch { ElMessage.success('阈值配置已保存(演示态)') } }
function publish() {
  const over = groups.value.flatMap(g => g.items).filter(isOver)
  if (over.length) return ElMessage.warning(`存在 ${over.length} 项超出安全限制,请修正后再发布`)
  ElMessage.success('阈值已发布生效并下发至各节点')
}
function reset() { ElMessage.info('已撤销未保存的变更') }
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: flex-start; }
.head h1 { margin: 0; font-size: 20px; }
.sub { margin: 6px 0 0; font-size: 12px; color: var(--qa-text-2); }
.head-actions { display: flex; gap: 10px; }
.val-cell :deep(.over .el-input__wrapper) { box-shadow: 0 0 0 1px var(--qa-danger) inset; }
.val-cell :deep(.over .el-input__inner) { color: var(--qa-danger); }
</style>
