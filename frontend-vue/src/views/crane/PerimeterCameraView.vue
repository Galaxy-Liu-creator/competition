<template>
  <div class="page perimeter">
    <section class="layout page-fill">
      <!-- 左:实时监控宫格 -->
      <IndustrialPanel class="grid-panel">
        <template #header>
          <div class="phead">
            <h2><i></i>实时监控 ({{ feeds.length }})<span class="qa-tag success on">在线</span></h2>
            <div class="ph-actions">
              <el-button>所有区域</el-button>
              <el-button type="primary" :icon="Plus" @click="openAdd">添加设备</el-button>
            </div>
          </div>
        </template>

        <div class="cam-grid">
          <article v-for="c in feeds" :key="c.id" class="cam" :class="{ off: c.status === 'offline' }">
            <div class="screen">
              <template v-if="c.status !== 'offline'">
                <img class="bg" :src="c.img" alt="" aria-hidden="true" />
                <img class="fg" :src="c.img" :alt="c.name" />
                <span class="ts mono">录制中 {{ c.ts }}</span>
                <span v-if="c.alert" class="ai-alert">{{ c.alert }}</span>
                <span v-else-if="c.notice" class="ai-alert normal">{{ c.notice }}</span>
                <span v-if="c.circle" class="target"></span>
                <el-icon class="wifi c-success"><Connection /></el-icon>
                <span class="res mono">{{ c.res }}</span>
              </template>
              <div v-else class="nosignal">
                <el-icon><VideoCameraFilled /></el-icon>
                <span>信号丢失</span>
              </div>
            </div>
            <footer>
              <div class="cinfo">
                <strong>{{ c.name }}</strong>
                <small>关联吊车:{{ c.crane || '无' }}</small>
              </div>
              <span class="qa-tag" :class="c.status === 'offline' ? 'info' : 'success'">{{ c.status === 'offline' ? '离线' : '在线' }}</span>
            </footer>
            <div class="cap-row">
              <span v-for="cap in c.caps" :key="cap" class="cap">{{ cap }}</span>
            </div>
          </article>
        </div>
      </IndustrialPanel>

      <!-- 右:系统状态 + 设备列表 -->
      <aside class="right">
        <IndustrialPanel title="系统状态速览">
          <template #extra><el-icon><Setting /></el-icon></template>
          <div class="overview">
            <div class="ov"><span>总设备数</span><b class="mono c-blue">{{ sys.total }}</b></div>
            <div class="ov"><span>异警设备</span><b class="mono c-danger">{{ sys.alarm }}</b></div>
            <div class="ov"><span>平均延迟</span><b class="mono c-cyan">{{ sys.latency }}<small>ms</small></b></div>
          </div>
          <div class="latest">
            <el-icon><WarningFilled /></el-icon>
            最新告警:CAM-P-001 检测到人员进入危险区域(2分钟前)
          </div>
        </IndustrialPanel>

        <IndustrialPanel title="设备列表" class="dev-panel">
          <template #extra>
            <el-input v-model="kw" placeholder="搜索 ID 或方向…" :prefix-icon="Search" size="small" style="width: 160px" />
          </template>
          <el-table :data="filteredList" height="440" highlight-current-row>
            <el-table-column label="设备 ID" min-width="110">
              <template #default="{ row }"><b class="mono" :class="row.status === 'offline' ? 'c-muted' : 'c-blue'">{{ row.id }}</b></template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <span :class="statusTone(row.status)"><i class="status-dot" :class="statusTone(row.status)"></i> {{ statusLabel(row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="dir" label="方向" width="70" />
            <el-table-column prop="ability" label="AI 能力" min-width="110" />
            <el-table-column label="心跳" width="80">
              <template #default="{ row }"><span class="mono" :class="row.status === 'offline' ? 'c-danger' : 'c-success'">{{ row.status === 'offline' ? '离线' : row.hb + 'ms' }}</span></template>
            </el-table-column>
          </el-table>
        </IndustrialPanel>
      </aside>
    </section>
  </div>
</template>

<script setup>
// 周界摄像头:实时监控宫格 + 系统速览 + 设备列表;cameraApi(type=perimeter) 失败回退演示数据
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Connection, VideoCameraFilled, Setting, WarningFilled, Search } from '@element-plus/icons-vue'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { cameraApi } from '@/api'
import { mediaPath } from '@/data/demoMedia'

const feeds = ref([
  { id: 'CAM-P-001', name: 'CAM-P-001(东区周界)', crane: 'CR-8012', status: 'online', ts: '00:14:23', res: '1080P / 30FPS', alert: '电子围栏越界联动', circle: true, caps: ['人员检测', '电子围栏联动'], img: mediaPath('siteGatePedestrians') },
  { id: 'CAM-P-002', name: 'CAM-P-002(南区大门)', crane: '无', status: 'online', ts: '12:06:11', res: '4K / 60FPS', caps: ['车辆识别', '入口管控'], img: mediaPath('constructionSiteEntrance') },
  { id: 'CAM-P-003', name: 'CAM-P-003(北区吊臂)', crane: 'CR-8022', status: 'online', ts: '08:41:37', res: '1080P / 30FPS', notice: '吊钩指挥监护中', caps: ['吊钩跟踪', '指挥手势识别'], img: mediaPath('craneHookGuidance') },
  { id: 'CAM-P-004', name: 'CAM-P-004(物料区)', crane: 'CR-8015', status: 'online', ts: '04:22:01', res: '1080P / 30FPS', notice: 'PPE 检测正常', caps: ['安全帽检测', '护目镜检测'], img: mediaPath('rebarDeckCrew') },
])

const sys = ref({ total: 42, alarm: 3, latency: 24 })

const list = ref([
  { id: 'CAM-P-001', status: 'online', dir: '北侧', ability: '人员检测, 围栏…', hb: 12 },
  { id: 'CAM-P-002', status: 'online', dir: '南门', ability: '车辆识别', hb: 18 },
  { id: 'CAM-P-003', status: 'online', dir: '东侧', ability: '吊钩跟踪, 手势识别', hb: 21 },
  { id: 'CAM-P-004', status: 'online', dir: '物料区', ability: '安全帽检测', hb: 16 },
  { id: 'CAM-P-005', status: 'online', dir: '西侧', ability: '人员检测', hb: 16 },
  { id: 'CAM-P-006', status: 'alarm', dir: '中控室', ability: '行为分析', hb: 69 },
  { id: 'CAM-P-007', status: 'online', dir: '西部A', ability: '车辆识别', hb: 33 },
  { id: 'CAM-P-008', status: 'online', dir: '西部B', ability: '车辆识别', hb: 33 },
])

const kw = ref('')
const filteredList = computed(() => list.value.filter(r => !kw.value || r.id.includes(kw.value) || r.dir.includes(kw.value)))

function statusTone(s) { return { online: 'c-success', offline: 'c-muted', alarm: 'c-danger' }[s] || 'c-muted' }
function statusLabel(s) { return { online: '在线', offline: '离线', alarm: '异常' }[s] || s }
function openAdd() { ElMessage.info('打开添加设备表单') }

onMounted(async () => {
  try {
    const res = await cameraApi.list({ type: 'perimeter', page: 1, page_size: 100 })
    if (res?.list?.length) {
      list.value = res.list.map(c => ({ id: c.id || c.code, status: c.status || 'online', dir: c.dir || '-', ability: c.ability || '-', hb: c.hb ?? 0 }))
      sys.value.total = res.total ?? sys.value.total
    }
  } catch { /* 回退演示数据 */ }
})
</script>

<style scoped>
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 400px; gap: 14px; }
.phead { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.phead h2 { display: flex; align-items: center; gap: 9px; margin: 0; font-size: 14px; }
.phead h2 i { width: 4px; height: 17px; background: linear-gradient(var(--qa-cyan), var(--qa-blue)); }
.phead .on { margin-left: 6px; }

.cam-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.cam { border: 1px solid var(--qa-border); border-radius: 6px; overflow: hidden; background: var(--qa-panel-2); }
.screen { position: relative; height: 200px; background: #04080f; overflow: hidden; }
.screen img.bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: blur(16px) brightness(.35) saturate(.7); transform: scale(1.12); }
.screen img.fg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; filter: brightness(.8) saturate(.9); }
.ts { position: absolute; left: 8px; top: 8px; font-size: 11px; color: var(--qa-cyan); background: rgba(4, 13, 24, .7); padding: 2px 6px; border-radius: 3px; }
.ai-alert { position: absolute; left: 8px; top: 32px; font-size: 11px; color: #fff; background: var(--qa-danger); padding: 3px 8px; border-radius: 3px; }
.ai-alert.normal { background: var(--qa-success); }
.target { position: absolute; left: 45%; top: 40%; width: 40px; height: 40px; border: 2px solid var(--qa-danger); border-radius: 50%; box-shadow: 0 0 12px var(--qa-danger); }
.wifi { position: absolute; right: 8px; top: 8px; font-size: 15px; }
.res { position: absolute; left: 8px; bottom: 8px; font-size: 11px; color: var(--qa-cyan); }
.nosignal { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 8px; color: var(--qa-text-muted); }
.nosignal .el-icon { font-size: 30px; }
.cam.off .screen { background: #0a1220; }
.cam footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; }
.cinfo strong { display: block; font-size: 13px; }
.cinfo small { color: var(--qa-text-muted); font-size: 11px; }
.cap-row { display: flex; gap: 8px; padding: 0 12px 12px; }
.cap { font-size: 11px; color: var(--qa-text-2); padding: 3px 8px; border: 1px solid var(--qa-border); border-radius: 4px; }

.right { display: grid; gap: 14px; align-content: start; }
.overview { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.ov { display: grid; gap: 6px; padding: 12px; text-align: center; border: 1px solid var(--qa-border); border-radius: 6px; background: var(--qa-panel-2); }
.ov span { font-size: 11px; color: var(--qa-text-2); }
.ov b { font-size: 24px; }
.latest { display: flex; align-items: center; gap: 8px; margin-top: 12px; padding: 10px 12px; font-size: 12px; color: var(--qa-danger); background: var(--qa-danger-dim); border: 1px solid rgba(239, 68, 68, .3); border-radius: 6px; }

@media (max-width: 1200px) { .layout { grid-template-columns: 1fr; } .cam-grid { grid-template-columns: 1fr; } }
</style>
