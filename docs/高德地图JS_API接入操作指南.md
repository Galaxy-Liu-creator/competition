# 擎安智吊接入高德地图 JS API 操作指南

本文面向 `擎安智吊` 前端，按参考项目的 Vue 3 + Vite 结构说明高德地图 JS API 2.0 的申请、配置、开发和后端数据对接方法。

## 一、接入前需要准备什么

需要准备以下信息：

- 一个高德开放平台账号，并完成实名认证。
- 一个“Web 端（JS API）”类型的 Key。
- 与 Key 配套的安全密钥 `securityJsCode`。
- 开发环境访问地址，例如 `http://localhost:5173` 和 `http://127.0.0.1:5173`。
- 生产环境的实际域名，例如 `https://qinganzhidiao.example.com`。

高德 JS API 的 Key 必须出现在浏览器请求中，因此不能把它当成真正的服务器密码。安全性主要依靠 Referer 白名单、配额限制、HTTPS 和高德控制台的安全设置来保证。

## 二、在高德开放平台创建 Key

1. 打开高德开放平台：<https://console.amap.com/>，注册或登录并完成实名认证。
2. 进入“控制台” → “应用管理” → “我的应用”。
3. 点击“创建新应用”，应用名称可以填写“擎安智吊”。
4. 在该应用下点击“添加 Key”。
5. 服务平台选择“Web 端（JS API）”。不要把 Web 服务 API 的 Key 直接当成 JS API Key 使用。
6. 创建后记录两项内容：

   - `Key`：浏览器加载地图时使用。
   - `安全密钥（securityJsCode）`：JS API 2.0 加载时使用。

7. 在应用的安全设置中配置 Web 端 Referer 白名单。开发阶段至少加入：

   - `localhost`
   - `127.0.0.1`

   生产阶段加入实际域名，并尽量不要使用过宽的 `*`。如果控制台按完整地址填写，可分别填写 `http://localhost:5173`、`http://127.0.0.1:5173` 和生产站点地址；以控制台当前提示格式为准。

8. 设置合理的日调用量和异常告警，避免 Key 被滥用。

## 三、在 Vue + Vite 项目中配置环境变量

在前端项目根目录创建 `.env.local`（例如 `frontend-vue/.env.local`）：

```env
VITE_AMAP_KEY=替换为你的高德Web端JS_API_Key
VITE_AMAP_SECURITY_CODE=替换为你的securityJsCode
VITE_API_BASE_URL=http://127.0.0.1:8000
```

只有以 `VITE_` 开头的变量会被 Vite 暴露给浏览器代码。不要把 Key 直接硬编码到组件中，也不要提交 `.env.local`。

在 `.gitignore` 中加入：

```gitignore
.env.local
.env.*.local
```

修改环境变量后需要重启 Vite 开发服务器。

## 四、安装 SDK

在 `frontend-vue` 目录执行：

```bash
npm install @amap/amap-jsapi-loader
```

参考项目已经使用 Vue 3、Vite、Element Plus 和 Axios，因此不需要更换现有技术栈。高德 SDK 只负责地图渲染，业务数据仍然由 FastAPI 接口提供。

## 五、可直接使用的 SiteMap.vue 示例

建议新建：`frontend-vue/src/components/map/SiteMap.vue`。

下面的组件包含地图初始化、设备 Marker、点击信息窗体、电子围栏 Polygon、告警点和组件销毁逻辑。示例假定后端接口为 `/api/sites/{siteId}/map-overview`。

```vue
<template>
  <section class="site-map-wrap">
    <div ref="mapEl" class="site-map"></div>
    <div v-if="loading" class="map-state">地图加载中...</div>
    <div v-if="error" class="map-error">{{ error }}</div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'

const props = defineProps({
  siteId: { type: String, default: 'site-001' },
})

const mapEl = ref(null)
const loading = ref(true)
const error = ref('')

let AMap = null
let map = null
let overlays = []

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
  return '#ffd166'
}

function addDeviceMarker(device) {
  const color = markerColor(device.type, device.status)
  const content = `
    <div style="width:18px;height:18px;border:2px solid ${color};border-radius:50%;
      background:${color}33;box-shadow:0 0 14px ${color};cursor:pointer;"></div>
  `

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
    content: `
      <div style="min-width:220px;padding:12px 14px;background:#071524;
        border:1px solid ${color};border-radius:6px;color:#dceeff;
        box-shadow:0 8px 24px #0008;font:13px/1.7 Arial,sans-serif;">
        <div style="font-size:15px;font-weight:600;color:${color};margin-bottom:5px;">
          ${escapeHtml(device.name)}
        </div>
        <div>类型：${escapeHtml(device.typeLabel || device.type || '设备')}</div>
        <div>状态：${escapeHtml(device.statusLabel || device.status || '未知')}</div>
        <div>坐标：${Number(device.lng).toFixed(6)}, ${Number(device.lat).toFixed(6)}</div>
      </div>
    `,
  })

  marker.on('click', () => infoWindow.open(map, marker.getPosition()))
  map.add(marker)
  overlays.push(marker)
}

function addFence(fence) {
  const polygon = new AMap.Polygon({
    path: fence.points.map((point) => [point.lng, point.lat]),
    strokeColor: fence.color || '#00d7ff',
    strokeWeight: 2,
    strokeOpacity: 0.95,
    fillColor: fence.color || '#00d7ff',
    fillOpacity: 0.12,
    bubble: true,
    extData: fence,
  })
  polygon.on('click', () => {
    // 可在这里打开电子围栏详情抽屉或跳转到围栏管理页
    console.log('点击围栏：', fence.id)
  })
  map.add(polygon)
  overlays.push(polygon)
}

function addAlarm(alarm) {
  addDeviceMarker({
    ...alarm,
    type: 'alarm',
    typeLabel: '告警点',
    status: 'alarm',
    statusLabel: alarm.levelLabel || '告警',
  })
}

async function loadOverview() {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const response = await fetch(`${baseUrl}/api/sites/${props.siteId}/map-overview`)
  if (!response.ok) throw new Error(`地图数据请求失败：HTTP ${response.status}`)
  return response.json()
}

async function initMap() {
  const key = import.meta.env.VITE_AMAP_KEY
  const securityJsCode = import.meta.env.VITE_AMAP_SECURITY_CODE
  if (!key || !securityJsCode) {
    throw new Error('缺少 VITE_AMAP_KEY 或 VITE_AMAP_SECURITY_CODE，请检查 .env.local')
  }

  // 必须在 SDK load 之前设置安全密钥
  window._AMapSecurityConfig = { securityJsCode }

  AMap = await AMapLoader.load({
    key,
    version: '2.0',
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.ControlBar'],
  })

  map = new AMap.Map(mapEl.value, {
    viewMode: '2D',
    zoom: 12,
    center: [121.4739, 31.2306], // 示例：上海，替换为项目默认工地坐标
    mapStyle: 'amap://styles/dark',
    resizeEnable: true,
  })
  map.addControl(new AMap.Scale())
  map.addControl(new AMap.ToolBar({ position: 'RB' }))

  const overview = await loadOverview()
  if (overview.center) map.setCenter([overview.center.lng, overview.center.lat])
  if (overview.zoom) map.setZoom(overview.zoom)

  ;(overview.devices || []).forEach(addDeviceMarker)
  ;(overview.fences || []).forEach(addFence)
  ;(overview.alarms || []).forEach(addAlarm)

  if (overlays.length) map.setFitView(overlays, false, [60, 60, 60, 60])
}

onMounted(async () => {
  try {
    await initMap()
  } catch (err) {
    error.value = err?.message || '地图初始化失败'
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

<style>
.site-map-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 480px;
  overflow: hidden;
  background: #06111e;
}

.site-map {
  width: 100%;
  height: 100%;
  min-height: 480px;
}

.map-state,
.map-error {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  padding: 9px 14px;
  border: 1px solid #1d4560;
  border-radius: 4px;
  background: #071524dd;
  color: #b8d9ed;
}

.map-error {
  border-color: #a53c4c;
  color: #ff9ba5;
}
</style>
```

注意：组件父元素必须有确定高度，否则地图会显示成一条空白区域。例如：

```css
.overview-map-panel {
  height: 620px;
}
```

## 六、后端接口返回格式

推荐新增或实现：`GET /api/sites/{siteId}/map-overview`。

接口返回的数据应全部使用经纬度，而不是视频帧像素坐标：

```json
{
  "siteId": "site-001",
  "coordinateSystem": "gcj02",
  "center": { "lng": 121.4739, "lat": 31.2306 },
  "zoom": 16,
  "devices": [
    {
      "id": "crane-001",
      "name": "1号塔吊",
      "type": "crane",
      "typeLabel": "塔式起重机",
      "status": "online",
      "statusLabel": "在线",
      "lng": 121.4742,
      "lat": 31.2308
    },
    {
      "id": "camera-012",
      "name": "东侧摄像头",
      "type": "camera",
      "typeLabel": "视频摄像头",
      "status": "online",
      "statusLabel": "在线",
      "lng": 121.4735,
      "lat": 31.2302
    }
  ],
  "fences": [
    {
      "id": "fence-001",
      "name": "吊装作业区",
      "color": "#00d7ff",
      "points": [
        { "lng": 121.4734, "lat": 31.2301 },
        { "lng": 121.4745, "lat": 31.2301 },
        { "lng": 121.4745, "lat": 31.2310 },
        { "lng": 121.4734, "lat": 31.2310 }
      ]
    }
  ],
  "alarms": []
}
```

如果开发环境没有完成 FastAPI 接口，可以先把 `loadOverview()` 换成一组本地 mock 数据，地图组件本身不需要改变。

## 七、Vite 开发代理

如果不想在开发环境处理跨域，可以在 `vite.config.js` 中配置：

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

配置代理后，前端可以直接请求 `/api/sites/site-001/map-overview`，不必在浏览器中写完整后端地址。

## 八、坐标系必须提前统一

高德地图 JS API 使用 GCJ-02（国测局坐标系）。项目中的地图数据建议统一存为 GCJ-02，并在接口中显式返回 `coordinateSystem: "gcj02"`。

- 高德地图拾取的坐标通常已经是 GCJ-02。
- GPS、部分物联网设备和 CAD 测量数据通常是 WGS-84，不能直接传给高德显示。
- 参考项目原有的 `fences.points` 是基于 `1280×720` 视频帧的像素坐标，不能直接作为 Polygon 点；必须先根据工地地理标定点转换成经纬度。
- 不要只交换 `lng` 和 `lat` 的顺序来“转换坐标系”。WGS-84 → GCJ-02 应在后端统一处理，并保留原始坐标用于追溯。

## 九、建议的地图代码目录

```text
frontend-vue/src/components/map/
├─ SiteMap.vue          # 地图容器和生命周期
├─ DeviceMarkers.vue    # 设备 Marker
├─ FenceLayer.vue       # 电子围栏图层
├─ AlarmLayer.vue       # 告警图层
├─ MapLegend.vue        # 图例
└─ mapAdapter.js        # 高德/Leaflet 的统一适配接口
```

后续如果需要切换到 Leaflet 或 MapLibre，页面业务层只调用 `mapAdapter` 的 `setCenter`、`addMarker`、`addPolygon`、`clear` 等方法即可，不必重写态势总览页面。

## 十、运行和验证

在前端目录执行：

```bash
npm install
npm run dev
```

打开终端输出的地址（通常是 `http://localhost:5173`），检查：

1. 浏览器 Network 中是否成功加载 `webapi.amap.com`。
2. 地图是否显示深色底图。
3. 设备 Marker 是否出现在正确位置。
4. 点击 Marker 是否弹出信息窗体。
5. 电子围栏是否显示为半透明 Polygon。
6. 后端接口失败时，页面是否显示明确错误，而不是无提示空白。

## 十一、常见错误排查

### `INVALID_USER_KEY` 或 `USERKEY_PLAT_NOMATCH`

通常是 Key 类型选错、Key 被删除、平台类型不是“Web 端（JS API）”，或者 Referer 白名单不匹配。检查 Key 所属应用和当前访问域名。

### `INVALID_USER_SCODE`

安全密钥错误，或 `window._AMapSecurityConfig` 设置得太晚。必须在 `AMapLoader.load()` 之前设置：

```js
window._AMapSecurityConfig = {
  securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE,
}
```

### 地图区域空白

优先检查 `.site-map` 及所有父元素是否有高度；其次检查 Key、控制台错误、网络请求和 `mapStyle` 配置。

### API 请求跨域

使用 Vite proxy，或在 FastAPI 中配置允许的前端 Origin。高德地图脚本的加载和业务后端接口的跨域是两件事，需要分别排查。

### Marker 偏移或围栏位置不对

检查经纬度顺序是否为 `[lng, lat]`，并确认所有数据都是 GCJ-02。不要把原有视频像素点直接传入高德。

### 重复加载 SDK

不要在每一个 Marker 组件中调用 `AMapLoader.load()`。建议由 `SiteMap.vue` 或单例 `mapAdapter.js` 统一加载一次，再把地图实例传给业务图层。

## 十二、生产环境安全建议

- 生产站点使用 HTTPS，并把 Referer 白名单限制到实际域名。
- Key 只用于前端 JS API；后端地理编码、路径规划等 Web 服务 API 使用单独的服务器 Key，并放到 FastAPI 的服务端环境变量中。
- 不要把 `.env.local`、生产 Key、安全密钥提交到 Git。
- 对地图接口增加登录鉴权和项目权限校验，避免任意用户读取全部工地设备坐标。
- 记录高德配额和错误日志；达到限额时可以切换到离线底图或备用地图适配器。
