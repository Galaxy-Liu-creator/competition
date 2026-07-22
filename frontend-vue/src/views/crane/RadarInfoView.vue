<template>
  <div class="page radarinfo">
    <!-- 顶部:雷达扫描图 + 视频联动 -->
    <section class="top">
      <IndustrialPanel title="实时雷达扫描图">
        <template #extra>
          <div class="legend"><span><i class="dot red"></i>危险区</span><span><i class="dot gold"></i>警示区</span></div>
        </template>
        <div class="scan">
          <div class="zone danger"></div>
          <div class="zone warn"></div>
          <div class="sweep"></div>
          <div class="blip cyan" style="left: 62%; top: 34%"><span class="tag mono">编号: T-4092<br>速度: 1.2m/s</span></div>
          <div class="blip gold" style="left: 40%; top: 66%"><span class="tag mono">编号: T-8821<br>速度: 2.6m/s</span></div>
        </div>
      </IndustrialPanel>

      <IndustrialPanel title="视频联动窗口">
        <template #extra><span class="qa-tag warning">定位追踪 T-8821</span></template>
        <div class="video">
          <img src="/login-bg.png" alt="联动视频" />
          <span class="rec"><i class="status-dot c-danger"></i>录制中</span>
          <div class="tbox">
            <div class="tinfo mono">吊钩 ID: CRANE-07<br>高度: 44.5m<br>载重: 12.4t<br>状态: 起吊中<br>风速: 14km/h</div>
          </div>
          <span class="cam-label mono">CAM-04 · 主吊臂视角</span>
        </div>
      </IndustrialPanel>
    </section>

    <!-- 底部三面板 -->
    <section class="bottom">
      <IndustrialPanel title="目标实时数据">
        <el-table :data="targets" size="small">
          <el-table-column label="目标 ID" min-width="90"><template #default="{ row }"><b class="mono" :class="{ 'c-gold': row.risk === 'warning' }">{{ row.id }}</b></template></el-table-column>
          <el-table-column prop="dist" label="距离(m)" align="right"><template #default="{ row }"><span class="mono">{{ row.dist }}</span></template></el-table-column>
          <el-table-column prop="speed" label="速度(m/s)" align="right"><template #default="{ row }"><span class="mono">{{ row.speed }}</span></template></el-table-column>
          <el-table-column prop="azimuth" label="方位角" align="right"><template #default="{ row }"><span class="mono">{{ row.azimuth }}</span></template></el-table-column>
          <el-table-column label="风险等级" width="80" align="center"><template #default="{ row }"><span class="qa-tag" :class="row.risk === 'warning' ? 'warning' : 'success'">{{ row.risk === 'warning' ? '警告' : '安全' }}</span></template></el-table-column>
        </el-table>
      </IndustrialPanel>

      <IndustrialPanel class="alarm-panel">
        <template #header><h2 class="ah"><el-icon class="c-warning"><WarningFilled /></el-icon>高危目标告警区</h2></template>
        <div class="alarm-body">
          <strong class="ain">正在进入警示区</strong>
          <p>目标 T-8821 正沿西南方向朝吊臂旋转半径内移动。</p>
          <div class="countdown">
            <span>碰撞预计剩余时间:</span>
            <b class="mono">12.4s</b>
          </div>
          <el-button type="danger" class="stop" @click="emergencyStop">紧急停止吊装</el-button>
          <el-button class="confirm">手动确认清除</el-button>
        </div>
      </IndustrialPanel>

      <IndustrialPanel title="参数设置与回放">
        <div class="cfg">
          <label>危险区域半径 <b class="c-danger">15m</b></label>
          <el-slider v-model="dangerR" :max="50" />
          <label>警示区域半径 <b class="c-gold">30m</b></label>
          <el-slider v-model="warnR" :max="50" />
          <label>历史数据回放</label>
          <el-slider v-model="playback" />
          <el-button type="primary" plain class="track-btn" :icon="Clock">追踪历史时间视图</el-button>
        </div>
      </IndustrialPanel>
    </section>
  </div>
</template>

<script setup>
// 雷达信息:实时扫描图 + 视频联动 + 目标数据/告警/参数回放;radarApi.readings 失败回退演示数据
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Clock } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { radarApi } from '@/api'

const targets = ref([
  { id: 'T-4092', dist: 28.4, speed: 1.2, azimuth: '045°', risk: 'safe' },
  { id: 'T-8821', dist: 14.5, speed: 2.6, azimuth: '112°', risk: 'warning' },
  { id: 'T-1934', dist: 45.0, speed: 0.5, azimuth: '330°', risk: 'safe' },
])

const dangerR = ref(30)
const warnR = ref(60)
const playback = ref(50)

async function emergencyStop() {
  await ElMessageBox.confirm('确认下发紧急停止吊装指令?此操作将立即制动当前吊装作业。', '紧急停止', { type: 'warning', confirmButtonText: '确认停止' })
  ElMessage.success('已下发紧急停止指令')
}

onMounted(async () => {
  try {
    const res = await radarApi.readings('RDR-CR1-001')
    if (Array.isArray(res) && res.length) targets.value = res.map(t => ({
      id: t.id, dist: t.dist, speed: t.speed, azimuth: t.azimuth, risk: t.risk || 'safe',
    }))
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.top { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.legend { display: flex; gap: 12px; }
.legend span { display: inline-flex; align-items: center; gap: 5px; color: var(--qa-text-2); }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.red { background: var(--qa-danger); } .dot.gold { background: var(--qa-gold); }

.scan { position: relative; height: 380px; border-radius: 8px; overflow: hidden; background: #04101c;
  background-image: repeating-radial-gradient(circle at 40% 45%, transparent 0 46px, rgba(34,211,238,.1) 47px 48px); }
.scan .zone { position: absolute; left: 40%; top: 45%; transform: translate(-50%, -50%); border-radius: 50%; }
.scan .zone.danger { width: 45%; height: 45%; background: radial-gradient(rgba(239,68,68,.12), transparent 70%); border: 1px solid rgba(239,68,68,.4); }
.scan .zone.warn { width: 72%; height: 72%; border: 1px solid rgba(234,179,8,.35); }
.sweep { position: absolute; left: 40%; top: 45%; width: 60%; height: 60%; transform: translate(-50%, -50%);
  background: conic-gradient(from 0deg, rgba(34,211,238,.3), transparent 70deg); border-radius: 50%; }
.blip { position: absolute; width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 0 12px currentColor; }
.blip.cyan { background: var(--qa-cyan); color: var(--qa-cyan); }
.blip.gold { background: var(--qa-gold); color: var(--qa-gold); }
.blip .tag { position: absolute; left: 14px; top: -6px; padding: 4px 8px; font-size: 10px; color: var(--qa-text); background: rgba(6,17,31,.9); border: 1px solid var(--qa-border); border-radius: 4px; white-space: nowrap; line-height: 1.5; }

.video { position: relative; height: 380px; border-radius: 8px; overflow: hidden; background: #04080f; }
.video img { width: 100%; height: 100%; object-fit: cover; filter: brightness(.5); }
.rec { position: absolute; right: 12px; top: 12px; display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: var(--qa-danger); }
.tbox { position: absolute; left: 55%; top: 30%; width: 90px; height: 130px; border: 2px solid var(--qa-success); box-shadow: 0 0 14px rgba(34,197,94,.5); }
.tinfo { position: absolute; left: 100%; top: 0; margin-left: 8px; padding: 8px; font-size: 10px; line-height: 1.7; color: var(--qa-success); background: rgba(6,20,14,.85); border: 1px solid rgba(34,197,94,.4); border-radius: 4px; white-space: nowrap; }
.cam-label { position: absolute; left: 12px; bottom: 12px; font-size: 11px; color: var(--qa-cyan); }

.bottom { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.ah { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 14px; }
.alarm-panel { border-color: rgba(234, 179, 8, .35); }
.ain { display: block; font-size: 15px; color: var(--qa-warning); }
.alarm-body p { margin: 10px 0 14px; font-size: 12px; color: var(--qa-text-2); }
.countdown { display: flex; align-items: center; justify-content: space-between; padding: 14px; margin-bottom: 16px; background: var(--qa-panel-2); border: 1px solid var(--qa-border); border-radius: 6px; }
.countdown b { font-size: 24px; color: var(--qa-gold); }
.stop { width: 100%; margin-bottom: 10px; }
.confirm { width: 100%; margin-left: 0; }

.cfg label { display: block; margin: 14px 0 4px; font-size: 12px; color: var(--qa-text-2); }
.cfg label:first-child { margin-top: 0; }
.cfg label b { float: right; }
.track-btn { width: 100%; margin-top: 18px; }

@media (max-width: 1200px) { .top { grid-template-columns: 1fr; } .bottom { grid-template-columns: 1fr; } }
</style>
