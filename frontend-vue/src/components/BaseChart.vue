<template><div ref="el" :style="{height,width:'100%'}"></div></template>
<script setup>
import * as echarts from 'echarts'
import { onMounted, onBeforeUnmount, watch, ref, nextTick } from 'vue'
import { activeTheme } from '@/theme'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '260px' },
})
const el = ref()
const chart = ref()

// 各视图的图表配置沿用深色主题的字面量色值;渲染前统一映射为当前主题令牌,
// 使日间/夜间切换时坐标轴、图例、分隔线即时跟随
const TOKEN_COLORS = {
  '#8ba3c2': '--qa-text-2',
  '#55708f': '--qa-text-muted',
  '#1e3a5c': '--qa-border',
  '#d5e3f5': '--qa-text',
  '#e8f1fd': '--qa-text',
  'rgba(30,58,92,.5)': '--qa-border',
  'rgba(30,58,92,.4)': '--qa-border',
}

function themed(value, styles) {
  if (typeof value === 'string' && TOKEN_COLORS[value]) {
    return styles.getPropertyValue(TOKEN_COLORS[value]).trim() || value
  }
  if (Array.isArray(value)) return value.map((item) => themed(item, styles))
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, themed(item, styles)]))
  }
  return value
}

const render = () => {
  if (!chart.value) return
  chart.value.setOption(themed(props.option, getComputedStyle(document.documentElement)), true)
}
const resize = () => chart.value?.resize()

onMounted(() => {
  chart.value = echarts.init(el.value)
  render()
  window.addEventListener('resize', resize)
})
watch(() => props.option, async () => { await nextTick(); render() }, { deep: true })
watch(activeTheme, () => render())
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart.value?.dispose()
})
</script>
