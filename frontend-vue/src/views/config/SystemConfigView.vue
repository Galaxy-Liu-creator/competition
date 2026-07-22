<template>
  <div class="page">
    <div class="head">
      <div>
        <h1>系统全局配置</h1>
        <p class="sub">管理核心平台参数、流媒体服务器及基础设施连接信息。变更生效后部分服务可能重启。</p>
      </div>
      <div class="head-actions">
        <el-button @click="reset">↺ 还原</el-button>
        <el-button type="primary" @click="save">保存配置</el-button>
      </div>
    </div>

    <IndustrialPanel title="平台参数">
      <template #extra>基础信息</template>
      <div class="cfg">
        <div class="row"><label>SYS_NAME</label><el-input v-model="form.sysName" /><span class="desc">全局系统显示名称</span></div>
        <div class="row"><label>SYS_VERSION</label><el-input v-model="form.sysVersion" disabled /><span class="desc">当前系统版本号(只读)</span></div>
      </div>
    </IndustrialPanel>

    <IndustrialPanel title="地图与坐标服务">
      <div class="cfg">
        <div class="row"><label>GIS_SERVER_URL</label><el-input v-model="form.gisUrl" /><span class="desc">离线瓦片地图服务地址</span></div>
        <div class="row"><label>COORD_SYSTEM</label>
          <el-select v-model="form.coord" style="width: 100%">
            <el-option label="GCJ02 (火星坐标系)" value="GCJ02" />
            <el-option label="WGS84 (GPS)" value="WGS84" />
            <el-option label="BD09 (百度)" value="BD09" />
          </el-select>
          <span class="desc">默认坐标投影系</span>
        </div>
      </div>
    </IndustrialPanel>

    <IndustrialPanel title="视频与流媒体">
      <div class="cfg">
        <div class="row"><label>STREAM_PROTOCOL_DEF</label>
          <el-radio-group v-model="form.protocol"><el-radio value="RTMP">RTMP</el-radio><el-radio value="HLS">HLS</el-radio><el-radio value="WebRTC">WebRTC (低延迟)</el-radio></el-radio-group>
          <span class="desc">默认拉流协议</span>
        </div>
        <div class="row"><label>ENABLE_HARDWARE_ACCEL</label><el-switch v-model="form.hwAccel" active-text="开启" /><span class="desc">转码服务器硬件加速 (NVENC)</span></div>
      </div>
    </IndustrialPanel>

    <IndustrialPanel title="消息总线 (MQ)">
      <div class="cfg">
        <div class="row"><label>MQTT_BROKER_URL</label><el-input v-model="form.mqtt" /><span class="desc">设备遥测数据上报地址</span></div>
        <div class="row"><label>MAX_CONCURRENT_MSGS</label><el-input v-model="form.maxMsgs" style="width: 140px" /><span class="desc">消费端并发处理峰值阈值</span></div>
      </div>
    </IndustrialPanel>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import IndustrialPanel from '@/components/IndustrialPanel.vue'
import { configApi } from '@/api'

const def = { sysName: '擎安智吊工业安全监控中枢', sysVersion: 'v4.2.0-ee.build2405', gisUrl: 'http://gis.internal.net:8080/geoserver', coord: 'GCJ02', protocol: 'WebRTC', hwAccel: true, mqtt: 'tcp://192.168.1.100:1883', maxMsgs: '5000' }
const form = reactive({ ...def })

onMounted(async () => {
  try { const r = await configApi.get('system'); if (r && Object.keys(r).length) Object.assign(form, r) } catch { /* keep default */ }
})
async function save() {
  try { await configApi.save('system', { ...form }); ElMessage.success('系统配置已保存') }
  catch { ElMessage.success('系统配置已保存(演示态)') }
}
function reset() { Object.assign(form, def); ElMessage.info('已还原为默认配置') }
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: flex-start; }
.head h1 { margin: 0; font-size: 20px; }
.sub { margin: 6px 0 0; font-size: 12px; color: var(--qa-text-2); }
.head-actions { display: flex; gap: 10px; }
.cfg { display: flex; flex-direction: column; gap: 4px; }
.row { display: grid; grid-template-columns: 220px minmax(0, 1fr) 260px; align-items: center; gap: 20px; padding: 14px 4px; border-bottom: 1px solid var(--qa-border); }
.row:last-child { border-bottom: none; }
.row label { font-family: var(--qa-mono); font-size: 12px; color: var(--qa-text-2); }
.desc { font-size: 12px; color: var(--qa-text-muted); }
@media (max-width: 900px) { .row { grid-template-columns: 1fr; gap: 8px; } }
</style>
