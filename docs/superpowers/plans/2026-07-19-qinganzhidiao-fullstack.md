# 油擎智安前后端首版实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在当前工作区的 `frontend-vue/` 和 `backend-python/` 中迁移并实现与 `picture/UI设计稿` 一致的油擎智安吊装安全运营平台首版；`D:/University-Competition/Innovation_Entrepreneurship/project` 仅作只读参考，地图先使用可替换占位层，不配置高德 Key。

**Architecture:** 前端继续使用 Vue 3 + Vite + Element Plus + ECharts，新增深色工业监控壳层、页面路由、指标卡片、告警面板和地图占位组件；后端继续使用 FastAPI，以现有 mock 数据为兼容基础，补充可复用的站点地图汇总、设备、围栏、告警和健康检查接口。地图组件通过 `mapAdapter` 风格接口预留未来高德实现。

**Tech Stack:** Vue 3 Composition API、Vue Router、Element Plus、ECharts、Axios、FastAPI、Pydantic、Python mock 数据。

---

### Task 1: 建立前端设计令牌与油擎智安运营壳层

**Files:**
- Create/Modify: `frontend-vue/src/App.vue`
- Create/Modify: `frontend-vue/src/styles/*`
- Create: `frontend-vue/src/styles/qinganzhidiao.css`
- Create/Modify: `frontend-vue/src/layouts/*`

- [ ] 读取现有布局、路由和主题样式，保留登录与既有页面入口。
- [ ] 建立深海军蓝背景、蓝青主色、橙红告警色、细边框、密集信息面板等设计令牌。
- [ ] 实现带 logo、“油擎智安”标题、系统状态、当前时间和用户入口的顶部栏。
- [ ] 实现左侧导航栏，支持态势总览、实时监测、事件闭环、电子围栏、设备中心、安全分析、规则策略、运维审计。
- [ ] 确保 1920×1080 稿图比例下信息密度和对齐方式一致，并对 1280px 以下窗口提供收缩布局。

### Task 2: 实现前端态势总览与地图占位

**Files:**
- Create: `frontend-vue/src/components/map/SiteMapPlaceholder.vue`
- Create: `frontend-vue/src/views/QingAnDashboardView.vue`
- Create/Modify: `frontend-vue/src/router/index.js`

- [ ] 根据 `picture/UI设计稿/01-态势总览.png` 实现指标卡片、工地状态、告警列表、设备在线率和趋势区域。
- [ ] 地图区域使用不依赖网络和 Key 的 SVG/CSS 占位，显示工地轮廓、吊车/摄像头/雷达图例和示例设备点。
- [ ] 在占位组件中保留 `initMap()`、`addMarker()`、`addPolygon()` 等未来高德适配入口，但不读取真实 Key。
- [ ] 接入后端 `/api/dashboard/overview`，接口不可用时回退到本地 mock，页面仍可渲染。
- [ ] 其他稿图页面先提供共享壳层和可用的占位数据页，保证路由可访问。

### Task 3: 实现前端业务页面和共享组件

**Files:**
- Create: `frontend-vue/src/components/qinganzhidiao/*`
- Create/Modify: `frontend-vue/src/views/*`

- [ ] 抽取指标卡、状态标签、告警行、时间线、图表面板、空状态和分页等共享组件。
- [ ] 实现实时监测、事件闭环、电子围栏、设备中心、安全分析、规则策略、运维审计首版页面。
- [ ] 使用 ECharts 绘制安全趋势、设备健康度和告警等级分布。
- [ ] 所有交互控件使用语义化 button/link，并提供 hover、focus 和 loading 状态；不使用 emoji 作为图标。

### Task 4: 补充 FastAPI 地图和运营接口

**Files:**
- Create/Modify: `backend-python/app/main.py`
- Create/Modify: `backend-python/app/api/*`
- Create/Modify: `backend-python/app/data/mock_data.py`
- Create/Modify: `backend-python/app/schemas/*`

- [ ] 保留现有接口行为，新增 `/api/dashboard/overview`、`/api/sites`、`/api/sites/{site_id}/map-overview`、设备、围栏和告警接口。
- [ ] 统一地图数据字段为 `lng`、`lat`、`coordinateSystem`，明确返回 `gcj02`。
- [ ] 为设备、围栏、告警响应建立 Pydantic 模型，避免前端依赖不稳定的裸字典。
- [ ] API 继续兼容 mock 数据；数据库仍可作为后续持久化替换点，不在本次任务中破坏已有运行方式。
- [ ] 增加 CORS 配置和统一异常响应，便于 Vite 开发代理调用。

### Task 5: 集成、验证与文档

**Files:**
- Create/Modify: `frontend-vue/package.json`
- Create/Modify: `frontend-vue/vite.config.js`
- Create: `docs/油擎智安前后端首版实现说明.md`

- [ ] 安装并记录新增依赖。
- [ ] 启动 FastAPI 和 Vite，验证首页、路由、接口和地图占位渲染。
- [ ] 执行前端构建和后端语法检查。
- [ ] 记录高德地图后续替换占位组件的接入点、环境变量和接口契约。
