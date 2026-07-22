<template>
  <div class="page">
    <div class="stat-row">
      <StatCard label="围栏总数" :value="stats.total" suffix="个" accent="#22d3ee" />
      <StatCard label="已启用" :value="stats.enabled" suffix="个" accent="#22c55e" />
      <StatCard label="高风险围栏" :value="stats.high" suffix="个" accent="#ef4444" />
      <StatCard label="关联设备" :value="stats.devices" suffix="台" accent="#3b82f6" />
    </div>

    <div class="fence-main">
      <IndustrialPanel title="围栏空间分布" class="map-panel">
        <template #extra>地图 API 待配置</template>
        <MapPlaceholder />
      </IndustrialPanel>

      <IndustrialPanel title="围栏列表" class="list-panel">
        <template #extra><el-button type="primary" size="small" @click="ElMessage.info('新增围栏开发中')">+ 新增围栏</el-button></template>
        <div class="fence-list">
          <article v-for="f in fences" :key="f.id" class="fence-card">
            <div class="fc-head">
              <b>{{ f.name }}</b>
              <span class="qa-tag" :class="riskTag(f.level)">{{ riskText(f.level) }}</span>
            </div>
            <div class="fc-meta">
              <span>关联设备 <b class="mono">{{ f.devices }}</b> 台</span>
              <span class="text-muted">{{ f.zone }}</span>
            </div>
            <div class="fc-foot">
              <el-switch v-model="f.enabled" @change="onToggle(f)" />
              <span class="text-muted">{{ f.enabled ? '监控中' : '已停用' }}</span>
              <el-button link type="primary" @click="ElMessage.info('查看围栏详情')">详情</el-button>
            </div>
          </article>
        </div>
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import MapPlaceholder from '@/components/map/MapPlaceholder.vue'

const stats = reactive({ total: 12, enabled: 9, high: 3, devices: 46 })
const fences = ref([
  { id: 1, name: '2# 吊装作业核心区', level: 'high', devices: 8, zone: 'A区 · 塔吊半径', enabled: true },
  { id: 2, name: '南侧周界安全带', level: 'mid', devices: 6, zone: '南侧围栏', enabled: true },
  { id: 3, name: '高空作业临时围栏', level: 'high', devices: 4, zone: 'C区 · 高空平台', enabled: true },
  { id: 4, name: '车辆通道隔离区', level: 'low', devices: 5, zone: '出入口', enabled: false },
  { id: 5, name: '材料堆放禁入区', level: 'mid', devices: 3, zone: 'B区 · 料场', enabled: true },
])
const riskTag = (l) => ({ high: 'danger', mid: 'warning', low: 'info' }[l] || 'info')
const riskText = (l) => ({ high: '高风险', mid: '中风险', low: '低风险' }[l] || '—')
function onToggle(f) { ElMessage.success(`「${f.name}」已${f.enabled ? '启用' : '停用'}`) }
</script>

<style scoped>
.fence-main { display: grid; grid-template-columns: minmax(0, 1.6fr) 360px; gap: 16px; align-items: start; }
.map-panel :deep(.body) { padding: 0; }
.map-panel :deep(.map) { min-height: 560px; }
.fence-list { display: flex; flex-direction: column; gap: 12px; max-height: 560px; overflow: auto; }
.fence-card { padding: 14px; border: 1px solid var(--qa-border); border-radius: 8px; background: var(--qa-panel-2); }
.fc-head { display: flex; justify-content: space-between; align-items: center; }
.fc-head b { font-size: 14px; }
.fc-meta { display: flex; justify-content: space-between; margin: 10px 0; font-size: 12px; color: var(--qa-text-2); }
.fc-foot { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.fc-foot .el-button { margin-left: auto; }
@media (max-width: 1100px) { .fence-main { grid-template-columns: 1fr; } }
</style>
