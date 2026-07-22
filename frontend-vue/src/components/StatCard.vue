<template>
  <article class="stat-card" :style="{ '--accent': accent }">
    <div class="info">
      <span class="label">{{ label }}</span>
      <div class="value mono">
        <strong>{{ value }}</strong>
        <small v-if="suffix">{{ suffix }}</small>
      </div>
      <span v-if="hint" class="hint">{{ hint }}</span>
    </div>
    <el-icon v-if="icon" class="icon"><component :is="icon" /></el-icon>
  </article>
</template>

<script setup>
// 设计稿统计卡:左侧色条 + 大数字 + 右上图标
defineProps({
  label: String,
  value: [String, Number],
  suffix: { type: String, default: '' },
  hint: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  accent: { type: String, default: '#3b82f6' },
})
</script>

<style scoped>
.stat-card {
  position: relative;
  display: flex; justify-content: space-between; align-items: flex-start;
  min-height: 104px; padding: 16px 18px;
  background: linear-gradient(135deg, var(--qa-panel-2), var(--qa-panel));
  border: 1px solid var(--qa-border);
  border-radius: var(--qa-radius-lg);
  overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; background: var(--accent);
}
.info { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.label { font-size: 13px; color: var(--qa-text-2); white-space: nowrap; }
.value strong { font-size: 30px; font-weight: 700; line-height: 1; color: var(--accent); }
.value small { margin-left: 4px; font-size: 13px; color: var(--qa-text-2); }
.hint { font-size: 12px; color: var(--qa-text-muted); }
.icon {
  font-size: 20px; color: var(--accent); flex-shrink: 0;
  padding: 7px; border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 14%, transparent);
  box-sizing: content-box;
}
</style>
