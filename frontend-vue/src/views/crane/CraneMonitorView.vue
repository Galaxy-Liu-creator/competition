<template>
  <div class="page monitor">
    <!-- 筛选工具栏 -->
    <IndustrialPanel compact>
      <div class="filterbar">
        <el-select v-model="craneSel" class="f"><el-option label="全部吊车" value="all" /><el-option label="QT-018" value="QT-018" /></el-select>
        <el-select v-model="areaSel" class="f"><el-option label="2# 作业区" value="2" /><el-option label="1# 作业区" value="1" /></el-select>
        <el-select v-model="onlineSel" class="f"><el-option label="在线设备" value="online" /><el-option label="全部设备" value="all" /></el-select>
        <span class="mono time">{{ now }}</span>
        <div class="spacer" />
        <button v-for="g in grids" :key="g.v" type="button" :class="{ active: grid === g.v }" @click="grid = g.v">{{ g.t }}</button>
        <button type="button" class="ghost">全屏监控</button>
      </div>
    </IndustrialPanel>

    <section class="content">
      <IndustrialPanel class="videos">
        <div class="video-grid" :class="'g' + grid">
          <article v-for="(v, i) in visibleVideos" :key="v.name" class="feed">
            <img class="bg" :src="v.img" alt="" aria-hidden="true" />
            <img class="fg" :src="v.img" :alt="v.name" />
            <header>{{ v.name }}<time class="mono">{{ nowSec(i) }}</time></header>
            <div v-if="v.alert" class="detect" :class="{ gold: v.tone === 'gold' }">{{ v.alert }}</div>
            <footer>
              <span class="rec">REC · 1080P</span>
              <b class="mono">AI {{ v.alert ? '告警' : '正常' }} · 延迟 68ms</b>
            </footer>
          </article>
        </div>
      </IndustrialPanel>

      <aside class="right">
        <IndustrialPanel title="QT-018 实时遥测">
          <template #extra><span class="qa-tag warning">作业中</span></template>
          <div class="telemetry">
            <div v-for="t in telemetry" :key="t[0]"><span>{{ t[0] }}</span><strong class="mono">{{ t[1] }}</strong></div>
          </div>
        </IndustrialPanel>

        <IndustrialPanel title="雷达安全域">
          <template #extra><span class="c-success">雷达-03 在线</span></template>
          <RadarScope />
        </IndustrialPanel>

        <IndustrialPanel title="联动设备">
          <template #extra><span class="c-success">全部在线</span></template>
          <div v-for="d in linked" :key="d[0]" class="linked">
            <span>{{ d[0] }}</span><b class="mono c-success">{{ d[1] }}</b>
          </div>
        </IndustrialPanel>
      </aside>
    </section>
  </div>
</template>

<script setup>
// 实时监控:视频宫格 + 遥测 + 雷达域 + 联动设备(由旧 MonitorView 迁移,改用 --qa- 令牌)
import { ref, computed } from 'vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import RadarScope from '@/components/RadarScope.vue'
import { mediaPath } from '@/data/demoMedia'

const craneSel = ref('all')
const areaSel = ref('2')
const onlineSel = ref('online')
const grid = ref(4)
const grids = [{ v: 1, t: '1 宫格' }, { v: 4, t: '4 宫格' }, { v: 9, t: '9 宫格' }]
const now = '2026-07-21 14:36'
const nowSec = (i) => `2026-07-21 14:36:2${i + 1}`

const videos = [
  { name: 'CAM-08 · 吊臂作业面', alert: 'PERSON · 回转区 0.94', tone: 'danger', img: mediaPath('craneLiftingAshlars') },
  { name: 'CAM-09 · 南侧围栏', img: mediaPath('siteFenceWarningSign') },
  { name: 'CAM-10 · 吊装落区', alert: 'LIFTING ZONE', tone: 'gold', img: mediaPath('girderLandingZone') },
  { name: 'CAM-11 · 车辆通道', img: mediaPath('mobileCraneE16') },
  { name: 'CAM-12 · 北侧塔基', img: mediaPath('towerCraneAerial02') },
  { name: 'CAM-13 · 物料堆场', img: mediaPath('siteYardTowerCranes') },
  { name: 'CAM-14 · 高空作业面', alert: 'NO HARNESS 0.88', tone: 'danger', img: mediaPath('ppeSite0701') },
  { name: 'CAM-15 · 东门闸口', img: mediaPath('constructionSiteEntrance') },
  { name: 'CAM-16 · 主臂回转区', alert: 'ROTATION ZONE', tone: 'gold', img: mediaPath('girderHeavyLift') },
]
const visibleVideos = computed(() => videos.slice(0, grid.value))
const telemetry = [
  ['吊臂角度', '42.6°'], ['载荷重量', '8.42 t'], ['回转角度', '126.4°'],
  ['吊钩高度', '18.7 m'], ['实时风速', '5.2 m/s'], ['安全余量', '28.4%'],
]
const linked = [
  ['边缘盒 BOX-018', '12 ms'], ['摄像头 CAM-08', '68 ms'],
  ['雷达 RADAR-03', '32 ms'], ['音柱 SPK-05', '待命'],
]
</script>

<style scoped>
.content { display: grid; grid-template-columns: minmax(0, 1fr) 440px; gap: 14px; }
.filterbar { display: flex; align-items: center; gap: 10px; }
.filterbar .f { width: 150px; }
.filterbar .time { color: var(--qa-text-2); }
.filterbar .spacer { flex: 1; }
.filterbar button {
  height: 32px; padding: 0 14px; color: var(--qa-text-2); cursor: pointer;
  background: var(--qa-panel-2); border: 1px solid var(--qa-border); border-radius: 6px; font-size: 12px;
}
.filterbar button.active { color: #fff; background: var(--qa-blue); border-color: var(--qa-blue); }
.filterbar button.ghost { color: var(--qa-cyan); border-color: var(--qa-border-strong); }

.videos :deep(.body) { padding: 10px; }
.video-grid { display: grid; gap: 10px; }
.video-grid.g1 { grid-template-columns: 1fr; }
.video-grid.g4 { grid-template-columns: repeat(2, 1fr); }
.video-grid.g9 { grid-template-columns: repeat(3, 1fr); }
.feed { position: relative; min-height: 320px; overflow: hidden; border: 1px solid var(--qa-border-strong); background: #050b12; border-radius: 4px; }
.feed img.bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: blur(16px) brightness(.35) saturate(.7); transform: scale(1.12); }
.feed img.fg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; filter: brightness(.78) saturate(.9); }
.feed header, .feed footer { position: absolute; z-index: 2; left: 10px; right: 10px; display: flex; justify-content: space-between; font-size: 11px; }
.feed header { top: 10px; padding: 7px 9px; background: rgba(4, 13, 24, .82); border-left: 2px solid var(--qa-cyan); }
.feed footer { bottom: 9px; }
.feed .rec { color: var(--qa-success); }
.feed footer b { font-weight: 400; color: var(--qa-text-2); }
.detect { position: absolute; z-index: 2; left: 46%; top: 30%; width: 19%; height: 34%; padding: 5px; color: #fff; border: 1px solid var(--qa-danger); background: rgba(239, 68, 68, .1); font: 9px var(--qa-mono); }
.detect.gold { left: 20%; top: 55%; width: 28%; height: 20%; border-color: var(--qa-gold); background: rgba(234, 179, 8, .1); }

.right { display: grid; gap: 14px; align-content: start; }
.telemetry { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.telemetry > div { display: grid; gap: 8px; padding: 12px; border: 1px solid var(--qa-border); background: var(--qa-panel-2); border-radius: 6px; }
.telemetry span { font-size: 11px; color: var(--qa-text-2); }
.telemetry strong { font-size: 20px; font-weight: 700; }
.linked { display: flex; justify-content: space-between; padding: 11px 0; border-bottom: 1px solid var(--qa-border); font-size: 12px; }
.linked:last-child { border-bottom: none; }

@media (max-width: 1250px) {
  .content { grid-template-columns: 1fr; }
  .right { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 800px) {
  .video-grid.g4, .video-grid.g9, .right { grid-template-columns: 1fr; }
  .filterbar { flex-wrap: wrap; }
}
</style>
