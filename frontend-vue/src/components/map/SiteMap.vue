<template>
  <section class="site-map-wrap">
    <div v-show="renderer === 'amap'" ref="mapEl" class="site-map"></div>

    <div v-if="renderer === 'offline' && overview" class="offline-map">
      <svg class="offline-canvas" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="离线作业区示意图">
        <defs>
          <pattern id="map-grid" width="8" height="8" patternUnits="userSpaceOnUse">
            <path d="M 8 0 L 0 0 0 8" fill="none" style="stroke: var(--map-grid)" stroke-width=".35" />
          </pattern>
          <filter id="map-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="1.2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        <rect width="100" height="100" style="fill: var(--map-bg)" />
        <rect width="100" height="100" fill="url(#map-grid)" />
        <path d="M -5 82 C 20 68, 36 78, 55 62 S 86 48, 106 32" fill="none" style="stroke: var(--map-road)" stroke-width="6" />
        <path d="M -5 82 C 20 68, 36 78, 55 62 S 86 48, 106 32" fill="none" style="stroke: var(--map-road-dash)" stroke-width=".7" stroke-dasharray="2 1" />

        <polygon
          v-for="zone in workZones"
          v-show="zone.points"
          :key="zone.id"
          :points="polygonPoints(zone)"
          :fill="`${zone.color}14`"
          :stroke="zone.color"
          stroke-width=".45"
          stroke-dasharray="1.8 1.1"
          vector-effect="non-scaling-stroke"
        />

        <polygon
          v-for="fence in overview.fences || []"
          :key="fence.id"
          :points="polygonPoints(fence)"
          :fill="`${fence.color || '#00d7ff'}22`"
          :stroke="fence.color || '#00d7ff'"
          stroke-width=".65"
          vector-effect="non-scaling-stroke"
        />

        <g
          v-for="device in overview.devices || []"
          :key="device.id"
          :transform="pointTransform(device)"
          filter="url(#map-glow)"
        >
          <circle r="1.55" style="fill: var(--map-bg)" :stroke="markerColor(device.type, device.status)" stroke-width=".7" vector-effect="non-scaling-stroke" />
          <circle r=".55" :fill="markerColor(device.type, device.status)" />
        </g>

        <g
          v-for="alarm in overview.alarms || []"
          :key="alarm.id"
          :transform="pointTransform(alarm)"
          class="alarm-point"
        >
          <circle r="2.8" fill="none" stroke="#ff5b5b" stroke-width=".55" vector-effect="non-scaling-stroke" />
          <circle r="1" fill="#ff5b5b" filter="url(#map-glow)" />
        </g>
      </svg>

      <span
        v-for="zone in workZones"
        :key="`tag-${zone.id}`"
        class="zone-tag"
        :style="zoneTagStyle(zone)"
      >{{ zone.name }}</span>

      <div class="offline-head">
        <strong>{{ overview.site?.shortName || overview.site?.name || '吊装作业区' }}</strong>
        <span>离线示意图 · GCJ-02 演示坐标</span>
      </div>
      <div class="offline-stats">
        <span>设备 <b>{{ overview.devices?.length || 0 }}</b></span>
        <span>围栏 <b>{{ overview.fences?.length || 0 }}</b></span>
        <span>告警 <b class="danger">{{ overview.alarms?.length || 0 }}</b></span>
      </div>
      <div class="offline-legend">
        <span><i style="--dot:#00d7ff"></i>吊车</span>
        <span><i style="--dot:#72f1b8"></i>摄像头</span>
        <span><i style="--dot:#b58cff"></i>雷达</span>
        <span><i style="--dot:#ff5b5b"></i>告警</span>
      </div>
    </div>

    <div v-if="loading" class="map-state">地图数据加载中...</div>
    <div v-else-if="notice" class="map-notice">{{ notice }}</div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import request from '@/api/request'
import { activeTheme } from '@/theme'

const props = defineProps({
  siteId: { type: String, default: 'site-001' },
})

const mapEl = ref(null)
const loading = ref(true)
const notice = ref('')
const renderer = ref('offline')
const overview = ref(null)

let AMap = null
let map = null
let overlays = []

const DEFAULT_OVERVIEW = {
  siteId: 'site-001',
  coordinateSystem: 'gcj02',
  center: { lng: 121.9660, lat: 30.9080, coordinateSystem: 'gcj02' },
  zoom: 17,
  site: { name: '一号能源基地 · 2#吊装作业区', shortName: '一号基地 2#作业区' },
  devices: [
    { id: 'CRANE-DEMO', name: '1号履带吊', type: 'crane', status: 'working', lng: 121.9658, lat: 30.9081 },
    { id: 'CAM-DEMO', name: '东侧摄像头', type: 'camera', status: 'online', lng: 121.9674, lat: 30.9082 },
    { id: 'RADAR-DEMO', name: '人员入侵雷达', type: 'radar', status: 'online', lng: 121.9666, lat: 30.90885 },
  ],
  fences: [
    {
      id: 'FENCE-DEMO', color: '#00d7ff', points: [
        { lng: 121.96445, lat: 30.90700 }, { lng: 121.96755, lat: 30.90700 },
        { lng: 121.96755, lat: 30.90900 }, { lng: 121.96445, lat: 30.90900 },
      ],
    },
  ],
  alarms: [{ id: 'ALARM-DEMO', lng: 121.96590, lat: 30.90805 }],
}

// 吊装工地功能分区:以站点中心为基准的相对布局(经纬度偏移),
// 让鸟瞰图呈现出完整的吊装作业现场,而非一片空地
const ZONE_LAYOUT = [
  { id: 'zone-main', name: '主吊装作业区', color: '#22d3ee', box: [-0.0008, -0.0006, 0.0012, 0.0008], labelShift: [0, -0.00050] },
  { id: 'zone-assembly', name: '构件拼装区', color: '#3b82f6', box: [0.0014, -0.0005, 0.0026, 0.0007] },
  { id: 'zone-material', name: '材料堆场', color: '#eab308', box: [-0.0024, -0.0006, -0.0011, 0.0007] },
  { id: 'zone-parking', name: '设备停放区', color: '#22c55e', box: [-0.0012, -0.0020, 0.0010, -0.0008] },
  { id: 'zone-office', name: '办公生活区', color: '#b58cff', box: [-0.0018, 0.0012, -0.0002, 0.0021] },
  { id: 'zone-gate', name: '安全出入口', color: '#f59e0b', point: [0.0013, -0.0016] },
]

const siteCenter = computed(() => (overview.value || DEFAULT_OVERVIEW).center || DEFAULT_OVERVIEW.center)

const workZones = computed(() => {
  const center = siteCenter.value
  return ZONE_LAYOUT.map((zone) => {
    if (zone.point) {
      return { ...zone, points: null, anchor: { lng: center.lng + zone.point[0], lat: center.lat + zone.point[1] } }
    }
    const [dLng1, dLat1, dLng2, dLat2] = zone.box
    const points = [
      { lng: center.lng + dLng1, lat: center.lat + dLat1 },
      { lng: center.lng + dLng2, lat: center.lat + dLat1 },
      { lng: center.lng + dLng2, lat: center.lat + dLat2 },
      { lng: center.lng + dLng1, lat: center.lat + dLat2 },
    ]
    const [shiftLng, shiftLat] = zone.labelShift || [0, 0]
    return {
      ...zone,
      points,
      anchor: {
        lng: center.lng + (dLng1 + dLng2) / 2 + shiftLng,
        lat: center.lat + (dLat1 + dLat2) / 2 + shiftLat,
      },
    }
  })
})

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;')

const markerColor = (type, status) => {
  if (status === 'alarm') return '#ff5b5b'
  if (type === 'crane') return '#00d7ff'
  if (type === 'camera') return '#72f1b8'
  if (type === 'radar') return '#b58cff'
  if (type === 'speaker') return '#24c88b'
  return '#ffd166'
}

// 高德覆盖物(信息窗/分区标签)的面板配色,随日间/夜间主题切换
const amapPanel = () => (activeTheme.value === 'light'
  ? { bg: 'rgba(255,255,255,.95)', text: '#16283f' }
  : { bg: '#071524', text: '#dceeff' })

const amapStyle = () => (activeTheme.value === 'light' ? 'amap://styles/normal' : 'amap://styles/dark')

const allGeoPoints = computed(() => {
  const data = overview.value || DEFAULT_OVERVIEW
  const points = [data.center]
  points.push(...(data.devices || []), ...(data.alarms || []))
  ;(data.fences || []).forEach((fence) => points.push(...(fence.points || [])))
  workZones.value.forEach((zone) => points.push(zone.anchor, ...(zone.points || [])))
  return points.filter((point) => Number.isFinite(Number(point?.lng)) && Number.isFinite(Number(point?.lat)))
})

const bounds = computed(() => {
  const lngs = allGeoPoints.value.map((point) => Number(point.lng))
  const lats = allGeoPoints.value.map((point) => Number(point.lat))
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  return {
    minLng, minLat,
    lngSpan: Math.max(maxLng - minLng, 0.0001),
    latSpan: Math.max(maxLat - minLat, 0.0001),
  }
})

const projectPoint = (point) => ({
  x: 7 + ((Number(point.lng) - bounds.value.minLng) / bounds.value.lngSpan) * 86,
  y: 93 - ((Number(point.lat) - bounds.value.minLat) / bounds.value.latSpan) * 86,
})

const pointTransform = (point) => {
  const projected = projectPoint(point)
  return `translate(${projected.x.toFixed(2)} ${projected.y.toFixed(2)})`
}

const polygonPoints = (zoneOrFence) => (zoneOrFence.points || [])
  .map((point) => {
    const projected = projectPoint(point)
    return `${projected.x.toFixed(2)},${projected.y.toFixed(2)}`
  })
  .join(' ')

const zoneTagStyle = (zone) => {
  const projected = projectPoint(zone.anchor)
  return { left: `${projected.x}%`, top: `${projected.y}%`, '--zone-color': zone.color }
}

function addDeviceMarker(device) {
  if (device.lng == null || device.lat == null) return
  const color = markerColor(device.type, device.status)
  const content = `<div style="width:18px;height:18px;border:2px solid ${color};border-radius:50%;background:${color}33;box-shadow:0 0 14px ${color};cursor:pointer;"></div>`
  const marker = new AMap.Marker({
    position: [device.lng, device.lat],
    title: device.name,
    content,
    anchor: 'center',
    zIndex: device.status === 'alarm' ? 120 : 100,
    extData: device,
  })
  const infoWindow = new AMap.InfoWindow({
    isCustom: true,
    offset: new AMap.Pixel(0, -16),
    content: `<div style="min-width:220px;padding:12px 14px;background:${amapPanel().bg};border:1px solid ${color};border-radius:6px;color:${amapPanel().text};box-shadow:0 8px 24px #0005;font:13px/1.7 Arial,sans-serif;"><div style="font-size:15px;font-weight:600;color:${color};margin-bottom:5px;">${escapeHtml(device.name)}</div><div>类型：${escapeHtml(device.typeLabel || device.type || '设备')}</div><div>状态：${escapeHtml(device.statusLabel || device.status || '未知')}</div><div>坐标：${Number(device.lng).toFixed(6)}, ${Number(device.lat).toFixed(6)}</div></div>`,
  })
  marker.on('click', () => infoWindow.open(map, marker.getPosition()))
  map.add(marker)
  overlays.push(marker)
}

function addFence(fence) {
  const points = (fence.points || []).filter((point) => point.lng != null && point.lat != null)
  if (points.length < 3) return
  const polygon = new AMap.Polygon({
    path: points.map((point) => [point.lng, point.lat]),
    strokeColor: fence.color || '#00d7ff',
    strokeWeight: 2,
    strokeOpacity: 0.95,
    fillColor: fence.color || '#00d7ff',
    fillOpacity: 0.12,
    bubble: true,
    extData: fence,
  })
  map.add(polygon)
  overlays.push(polygon)
}

function addZone(zone) {
  if (zone.points) {
    const polygon = new AMap.Polygon({
      path: zone.points.map((point) => [point.lng, point.lat]),
      strokeColor: zone.color,
      strokeWeight: 2,
      strokeOpacity: 0.85,
      strokeStyle: 'dashed',
      fillColor: zone.color,
      fillOpacity: 0.07,
      bubble: true,
      zIndex: 30,
      extData: zone,
    })
    map.add(polygon)
    overlays.push(polygon)
  }
  const label = new AMap.Marker({
    position: [zone.anchor.lng, zone.anchor.lat],
    anchor: 'center',
    zIndex: 60,
    bubble: true,
    content: `<div style="padding:3px 10px;font-size:12px;white-space:nowrap;color:${zone.color};background:${amapPanel().bg};border:1px solid ${zone.color};border-radius:4px;">${escapeHtml(zone.name)}</div>`,
  })
  map.add(label)
  overlays.push(label)
}

function addAlarm(alarm) {
  addDeviceMarker({ ...alarm, type: 'alarm', typeLabel: '告警点', status: 'alarm', statusLabel: alarm.levelLabel || '告警' })
}

const loadOverview = () => request.get(`/api/sites/${props.siteId}/map-overview`)

function renderOverlays(data, fit = true) {
  if (!map) return
  if (overlays.length) map.remove(overlays)
  overlays = []
  workZones.value.forEach(addZone)
  ;(data.devices || []).forEach(addDeviceMarker)
  ;(data.fences || []).forEach(addFence)
  ;(data.alarms || []).forEach(addAlarm)
  if (fit && overlays.length) map.setFitView(overlays, false, [60, 60, 60, 60])
}

async function initAmap(data) {
  const key = import.meta.env.VITE_AMAP_KEY
  const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_CODE
  if (!key || !securityJsCode) {
    notice.value = '未配置高德地图密钥，已自动切换为离线作业区示意图'
    renderer.value = 'offline'
    return
  }

  window._AMapSecurityConfig = { securityJsCode }
  renderer.value = 'amap'
  AMap = await AMapLoader.load({ key, version: '2.0', plugins: ['AMap.Scale', 'AMap.ToolBar'] })
  map = new AMap.Map(mapEl.value, {
    viewMode: '2D',
    zoom: data.zoom || 15,
    center: [data.center.lng, data.center.lat],
    mapStyle: amapStyle(),
    resizeEnable: true,
  })
  map.addControl(new AMap.Scale())
  map.addControl(new AMap.ToolBar({ position: 'RB' }))
  renderOverlays(data)
  renderer.value = 'amap'
}

// 日间/夜间切换时高德底图换肤,并重建覆盖物(信息窗/标签的面板色依赖主题)
watch(activeTheme, () => {
  if (!map) return
  map.setMapStyle(amapStyle())
  renderOverlays(overview.value || DEFAULT_OVERVIEW, false)
})

onMounted(async () => {
  try {
    overview.value = await loadOverview()
  } catch (error) {
    overview.value = DEFAULT_OVERVIEW
    notice.value = '地图业务数据暂不可用，当前显示本地演示坐标'
  }

  try {
    await initAmap(overview.value)
  } catch (error) {
    renderer.value = 'offline'
    notice.value = '高德地图加载失败，已自动切换为离线作业区示意图'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
    map = null
  }
  overlays = []
})
</script>

<style scoped>
/* 组件级地图配色令牌:夜间为深海底图,日间切换为浅色底图 */
.site-map-wrap {
  --map-bg: #06111e;
  --map-grid: rgba(52, 105, 142, .18);
  --map-road: rgba(92, 126, 153, .2);
  --map-road-dash: rgba(156, 190, 214, .22);
  --map-panel: rgba(5, 18, 31, .86);
  --map-panel-2: rgba(5, 18, 31, .78);
  --map-border: #1e4565;
  --map-text: #e7f6ff;
  --map-text-2: #8db1c8;
  --map-muted: #6f98b5;
  --map-glow: rgba(0, 215, 255, .08);
}
[data-theme="light"] .site-map-wrap {
  --map-bg: #e6edf5;
  --map-grid: rgba(52, 105, 142, .22);
  --map-road: rgba(122, 148, 172, .5);
  --map-road-dash: rgba(74, 104, 133, .55);
  --map-panel: rgba(255, 255, 255, .92);
  --map-panel-2: rgba(255, 255, 255, .9);
  --map-border: #c3d2e4;
  --map-text: #16283f;
  --map-text-2: #4d647f;
  --map-muted: #62809e;
  --map-glow: rgba(0, 150, 210, .07);
}

.site-map-wrap { position: relative; width: 100%; height: 100%; min-height: 430px; overflow: hidden; background: var(--map-bg); border: 1px solid var(--map-border); }
.site-map, .offline-map { width: 100%; height: 100%; min-height: 430px; }
.offline-map { position: relative; background: radial-gradient(circle at 65% 30%, var(--map-glow), transparent 42%), var(--map-bg); }
.offline-canvas { position: absolute; inset: 0; width: 100%; height: 100%; }
.zone-tag {
  position: absolute; transform: translate(-50%, -50%); z-index: 3;
  padding: 2px 8px; font-size: 10px; white-space: nowrap; pointer-events: none;
  color: var(--zone-color); background: var(--map-panel-2);
  border: 1px solid var(--zone-color); border-radius: 3px; letter-spacing: 1px;
}
.offline-head { position: absolute; left: 16px; top: 14px; display: grid; gap: 4px; padding: 9px 12px; background: var(--map-panel); border: 1px solid var(--map-border); border-left: 3px solid var(--qa-cyan); border-radius: 4px; }
.offline-head strong { color: var(--map-text); font-size: 13px; }
.offline-head span { color: var(--map-muted); font: 10px var(--qa-mono); }
.offline-stats { position: absolute; right: 14px; top: 14px; display: flex; gap: 12px; padding: 8px 11px; color: var(--map-text-2); background: var(--map-panel); border: 1px solid var(--map-border); border-radius: 4px; font-size: 11px; }
.offline-stats b { color: var(--qa-cyan); font-family: var(--qa-mono); }
.offline-stats b.danger { color: var(--qa-danger); }
.offline-legend { position: absolute; left: 14px; bottom: 14px; display: flex; flex-wrap: wrap; gap: 12px; padding: 7px 10px; color: var(--map-text-2); background: var(--map-panel); border: 1px solid var(--map-border); border-radius: 4px; font-size: 10px; }
.offline-legend span { display: inline-flex; align-items: center; gap: 5px; }
.offline-legend i { width: 7px; height: 7px; border-radius: 50%; background: var(--dot); box-shadow: 0 0 8px var(--dot); }
.alarm-point { animation: alarm-pulse 1.8s ease-out infinite; transform-box: fill-box; transform-origin: center; }
.map-state { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 10; padding: 9px 14px; border: 1px solid var(--map-border); border-radius: 4px; background: var(--map-panel); color: var(--map-text-2); }
.map-notice { position: absolute; right: 14px; bottom: 14px; z-index: 10; max-width: 320px; padding: 7px 10px; border: 1px solid rgba(234, 179, 8, .45); border-radius: 4px; background: var(--qa-warning-dim); color: var(--qa-warning); font-size: 10px; }
@keyframes alarm-pulse { 0%, 100% { opacity: 1; } 50% { opacity: .45; } }
@media (max-width: 700px) { .offline-stats { top: 72px; left: 16px; right: auto; } .map-notice { left: 14px; right: 14px; } }
</style>
