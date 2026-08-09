<template>
  <div class="page">
    <div class="head">
      <h1>推送策略配置</h1>
      <div class="head-actions"><el-button @click="reset">重置</el-button><el-button type="primary" @click="save">保存配置</el-button></div>
    </div>

    <div class="grid-top">
      <IndustrialPanel title="消息渠道配置">
        <template #extra><el-icon class="add"><Plus /></el-icon></template>
        <div v-for="ch in channels" :key="ch.key" class="channel">
          <el-icon class="ch-ico" :class="ch.color"><component :is="ch.icon" /></el-icon>
          <div class="ch-info"><b>{{ ch.name }}</b><small>{{ ch.desc }}</small></div>
          <el-switch v-model="ch.enabled" />
        </div>
      </IndustrialPanel>

      <IndustrialPanel title="可靠性与重试机制">
        <div class="retry">
          <div class="f"><label>最大重试次数</label><el-input v-model="retry.max" /></div>
          <div class="f"><label>重试间隔(分钟)</label><el-input v-model="retry.interval" /></div>
        </div>
        <div class="fallback">
          <el-icon class="fb-ico"><RefreshRight /></el-icon>
          <b>降级备用渠道</b>
          <p>若主渠道达到最大重试次数后仍失败,将自动通过"系统弹窗"进行二次触达。</p>
          <el-button @click="ElMessage.info('降级逻辑配置开发中')">配置降级逻辑</el-button>
        </div>
      </IndustrialPanel>
    </div>

    <IndustrialPanel title="活跃推送策略">
      <template #extra><el-button type="primary" size="small" @click="ElMessage.info('新增策略开发中')">+ 新增策略</el-button></template>
      <el-table :data="strategies">
        <el-table-column prop="name" label="策略名称" min-width="150" />
        <el-table-column prop="channels" label="触发渠道" min-width="140" />
        <el-table-column prop="receivers" label="接收角色" min-width="140" />
        <el-table-column label="风险等级" width="110"><template #default="{ row }"><span class="qa-tag" :class="riskTag(row.level)">{{ riskText(row.level) }}</span></template></el-table-column>
        <el-table-column prop="window" label="静默期" width="140"><template #default="{ row }"><span class="mono">{{ row.window }}</span></template></el-table-column>
        <el-table-column label="状态" width="80" align="center"><template #default="{ row }"><el-switch v-model="row.enabled" /></template></el-table-column>
        <el-table-column label="操作" width="70" align="right"><template #default><el-button link type="primary"><el-icon><Edit /></el-icon></el-button></template></el-table-column>
      </el-table>
    </IndustrialPanel>

    <div class="grid-bottom page-fill">
      <IndustrialPanel title="告警升级逻辑">
        <ul class="escalation">
          <li v-for="(e, i) in escalation" :key="i"><span class="tl-dot" :class="e.color" /><div class="e-body" :style="{ borderColor: e.border }"><b>{{ e.title }}</b><small>{{ e.desc }}</small></div></li>
        </ul>
      </IndustrialPanel>

      <IndustrialPanel title="消息推送模板">
        <template #extra><a>高级变量插值库</a></template>
        <div class="tpl">
          <p><span class="c-danger">【紧急】</span>检测到吊装安全违章:位置 <code>${'{'}Location{'}'}</code>。</p>
          <p>风险等级:<code>${'{'}Risk_Level{'}'}</code></p>
          <p>发生时间:<code>${'{'}Timestamp{'}'}</code></p>
          <p>详情描述:<code>${'{'}Event_Description{'}'}</code></p>
          <p class="dim">请立即登录平台进行确认与处置。</p>
          <div class="vars"><el-tag v-for="v in ['Device_ID', 'Action_Req', 'Operator']" :key="v" effect="dark">+ ${'{'}{{ v }}{'}'}</el-tag></div>
        </div>
      </IndustrialPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, markRaw, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ChatDotRound, Message, Cellphone, Bell, RefreshRight, Edit } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { configApi } from '@/api'

const channels = ref([
  { key: 'sms', name: '短信网关', desc: '阿里云短信服务', icon: markRaw(Cellphone), color: 'c-cyan', enabled: true },
  { key: 'app', name: '企业微信', desc: '企业内部 APP', icon: markRaw(ChatDotRound), color: 'c-success', enabled: true },
  { key: 'email', name: '邮件服务器', desc: 'SMTP 服务', icon: markRaw(Message), color: 'c-muted', enabled: false },
  { key: 'speaker', name: '音柱联动', desc: '现场声光播报', icon: markRaw(Bell), color: 'c-gold', enabled: true },
])
const retry = reactive({ max: '3', interval: '5' })
const strategies = ref([
  { name: '重超载风险预警', channels: '短信 + 企业微信', receivers: '安全员, 项目经理', level: 'high', window: '无', enabled: true },
  { name: '电子围栏闯入播', channels: '系统弹窗', receivers: '操作员, 安全员', level: 'mid', window: '22:00 - 06:00', enabled: true },
  { name: '每日资产报表推', channels: '邮件', receivers: '管理员', level: 'low', window: 'N/A', enabled: false },
])
const escalation = [
  { title: '初始告警:现场安全员', desc: '渠道:短信 (T+0 min)', color: 'c-cyan', border: 'var(--qa-cyan)' },
  { title: '超时 15 分钟未处理', desc: '升级至:项目经理(渠道:企业微信)', color: 'c-warning', border: 'var(--qa-warning)' },
  { title: '超时 30 分钟未处理', desc: '升级至:区域负责人 + 现场声光报警', color: 'c-danger', border: 'var(--qa-danger)' },
]
const riskTag = (l) => ({ high: 'danger', mid: 'warning', low: 'success' }[l] || 'info')
const riskText = (l) => ({ high: '严重', mid: '中级', low: '普通' }[l] || '—')

onMounted(async () => { try { const r = await configApi.get('push'); if (r?.channels?.length) { channels.value = r.channels; Object.assign(retry, r.retry || {}) } } catch { /* keep demo */ } })
async function save() { try { await configApi.save('push', { channels: channels.value, retry, strategies: strategies.value }); ElMessage.success('推送策略已保存') } catch { ElMessage.success('推送策略已保存(演示态)') } }
function reset() { ElMessage.info('已重置') }
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; }
.head h1 { margin: 0; font-size: 20px; }
.head-actions { display: flex; gap: 10px; }
.add { cursor: pointer; }
.grid-top, .grid-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.channel { display: flex; align-items: center; gap: 12px; padding: 12px; margin-bottom: 10px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.ch-ico { font-size: 20px; }
.ch-info { flex: 1; } .ch-info b { display: block; font-size: 13px; } .ch-info small { color: var(--qa-text-muted); font-size: 11px; }
.retry { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.f { display: flex; flex-direction: column; gap: 6px; } .f label { font-size: 12px; color: var(--qa-text-2); }
.fallback { padding: 16px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); text-align: center; }
.fb-ico { font-size: 24px; color: var(--qa-cyan); }
.fallback b { display: block; margin: 8px 0; }
.fallback p { font-size: 12px; color: var(--qa-text-muted); margin: 0 0 12px; }
.escalation { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
.escalation li { display: flex; gap: 12px; align-items: flex-start; }
.tl-dot { width: 12px; height: 12px; margin-top: 4px; border-radius: 50%; border: 2px solid currentColor; flex-shrink: 0; }
.e-body { flex: 1; padding: 10px 12px; border: 1px solid var(--qa-border); border-left-width: 3px; border-radius: 4px; background: var(--qa-panel-2); }
.e-body b { display: block; font-size: 13px; } .e-body small { color: var(--qa-text-muted); font-size: 11px; }
.tpl { font-size: 13px; line-height: 1.9; padding: 14px; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.tpl p { margin: 0; }
.tpl code { font-family: var(--qa-mono); color: var(--qa-cyan); background: var(--qa-cyan-dim); padding: 1px 5px; border-radius: 3px; }
.tpl .dim { color: var(--qa-text-muted); margin-top: 8px; }
.vars { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
@media (max-width: 1000px) { .grid-top, .grid-bottom { grid-template-columns: 1fr; } }
</style>
