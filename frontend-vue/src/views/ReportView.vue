<template>
  <div class="page">
    <div class="head">
      <h1>安全报表</h1>
      <div class="head-actions">
        <el-radio-group v-model="range" size="small" @change="buildCharts">
          <el-radio-button value="7">近 7 日</el-radio-button>
          <el-radio-button value="30">近 30 日</el-radio-button>
        </el-radio-group>
        <el-date-picker v-model="dateRange" type="daterange" size="small" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width: 240px" />
        <el-button type="primary" size="small" @click="onExport"><el-icon><Download /></el-icon>&nbsp;导出报表</el-button>
      </div>
    </div>

    <div class="stat-row">
      <StatCard label="事件总数" :value="kpi.total" suffix="起" accent="#22d3ee" />
      <StatCard label="已处置" :value="kpi.resolved" suffix="起" accent="#22c55e" />
      <StatCard label="高风险占比" :value="kpi.highRate" suffix="%" accent="#ef4444" />
      <StatCard label="平均处置时效" :value="kpi.avgTime" suffix="min" accent="#3b82f6" />
    </div>

    <div class="chart-grid">
      <IndustrialPanel :title="`${range} 日事件趋势`"><BaseChart :option="trendOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="违章类型分布"><BaseChart :option="pieOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="各作业区事件对比"><BaseChart :option="barOption" height="280px" /></IndustrialPanel>
      <IndustrialPanel title="处置时效统计"><BaseChart :option="timeOption" height="280px" /></IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import BaseChart from '@/components/BaseChart.vue'

const range = ref('7')
const dateRange = ref()
const kpi = reactive({ total: 328, resolved: 305, highRate: 18.6, avgTime: 42 })

const axis = { axisLine: { lineStyle: { color: '#1e3a5c' } }, axisLabel: { color: '#8ba3c2' }, splitLine: { lineStyle: { color: 'rgba(30,58,92,.5)' } } }
const grid = { left: 40, right: 20, top: 40, bottom: 30 }

const trendOption = ref({})
const pieOption = ref({})
const barOption = ref({})
const timeOption = ref({})

function buildCharts() {
  const days = Number(range.value)
  const labels = Array.from({ length: days }, (_, i) => `${i + 1}日`)
  const alarm = labels.map(() => Math.round(20 + Math.random() * 40))
  const violation = labels.map(() => Math.round(10 + Math.random() * 25))
  trendOption.value = {
    tooltip: { trigger: 'axis' }, legend: { data: ['告警事件', '违章事件'], textStyle: { color: '#8ba3c2' }, top: 6 }, grid,
    xAxis: { type: 'category', data: labels, ...axis }, yAxis: { type: 'value', ...axis },
    series: [
      { name: '告警事件', type: 'line', smooth: true, data: alarm, itemStyle: { color: '#22d3ee' }, areaStyle: { color: 'rgba(34,211,238,.12)' } },
      { name: '违章事件', type: 'line', smooth: true, data: violation, itemStyle: { color: '#f59e0b' } },
    ],
  }
  pieOption.value = {
    tooltip: { trigger: 'item' }, legend: { bottom: 0, textStyle: { color: '#8ba3c2' } },
    series: [{ type: 'pie', radius: ['45%', '68%'], center: ['50%', '44%'], label: { color: '#e8f1fd' }, data: [
      { value: 145, name: '人员违章', itemStyle: { color: '#ef4444' } },
      { value: 98, name: '设备异常', itemStyle: { color: '#f59e0b' } },
      { value: 62, name: '环境风险', itemStyle: { color: '#22d3ee' } },
      { value: 23, name: '其他', itemStyle: { color: '#3b82f6' } },
    ] }],
  }
  barOption.value = {
    tooltip: { trigger: 'axis' }, grid,
    xAxis: { type: 'category', data: ['A区', 'B区', 'C区', 'D区', '料场'], ...axis }, yAxis: { type: 'value', ...axis },
    series: [{ type: 'bar', barWidth: '46%', data: [86, 54, 72, 38, 28], itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] } }],
  }
  timeOption.value = {
    tooltip: { trigger: 'axis' }, grid,
    xAxis: { type: 'category', data: ['<15min', '15-30', '30-60', '1-2h', '>2h'], ...axis }, yAxis: { type: 'value', ...axis },
    series: [{ type: 'bar', barWidth: '46%', data: [120, 88, 60, 42, 18], itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] } }],
  }
}
function onExport() { ElMessage.success('报表已导出(CSV 演示)') }
onMounted(buildCharts)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.head h1 { margin: 0; font-size: 20px; }
.head-actions { display: flex; gap: 10px; align-items: center; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 1000px) { .chart-grid { grid-template-columns: 1fr; } }
</style>
