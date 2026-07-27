# 任务清单完成实施计划（2026-07-26）

> **For agentic workers:** 本计划在当前会话内联执行（executing-plans 模式）。步骤用 `- [ ]` 追踪。
> 注意：工作树存在大量既有未提交改动，本计划不做中途 git commit，统一在收尾阶段由用户决定提交方式。

**Goal:** 完成 docs/任务清单.txt 的 9 项任务：摄像头配置面板/筛选/新增、录像机卡片高度与通道视图、音柱关联完善、报表与审计日志真实 Excel 导出、全站查询可用。

**Architecture:** 前端 Vue3+Element Plus 视图逐页修复，统一「后端优先、客户端最终过滤」策略保证双路径可用；新增共享 Excel 导出工具；后端 FastAPI 扩展审计日志过滤与通用 type 过滤（TDD）。

**Tech Stack:** Vue 3 / Element Plus / SheetJS xlsx / FastAPI / SQLAlchemy / pytest

## Global Constraints

- 不使用真实地名（编号式命名，如 A区/2# 作业区）
- 颜色一律用主题变量 `--qa-*`，明暗主题都可读
- 前端不展示演示账号凭据
- 所有页面在后端不可用时必须回退演示数据且功能不缩水
- 后端统一响应 `{code,message,data}`，列表 `{list,total,page,page_size}`

---

### Task 1: Excel 导出工具 + xlsx 依赖

**Files:**
- Modify: `frontend-vue/package.json`（npm i xlsx）
- Create: `frontend-vue/src/utils/exportExcel.js`

**Interfaces:**
- Produces: `exportExcel({ filename, sheets: [{ name, columns: [{label,key,width?}], rows: object[] }] })` → 触发浏览器下载 `<filename>_<YYYY-MM-DD>.xlsx`；空数据 sheet 仍生成表头。

- [ ] Step 1: `npm install xlsx`（frontend-vue 目录）
- [ ] Step 2: 实现 `exportExcel.js`：json→aoa（表头行 + 数据行按 columns.key 取值），`XLSX.utils.aoa_to_sheet`、`!cols` 宽度、`book_append_sheet`、`XLSX.writeFile`
- [ ] Step 3: `npm run build` 确认无编译错误

### Task 2: 后端过滤增强（TDD）

**Files:**
- Modify: `backend-python/app/api/resources.py`（audit-logs 端点）
- Modify: `backend-python/app/api/_crud.py`（列表端点通用 `type` 参数）
- Test: `backend-python/tests/test_resources.py`

**Interfaces:**
- Produces: `GET /api/audit-logs?operator=&module=&start=&end=`（operator 模糊、module 精确、start/end 为 YYYY-MM-DD 与 created_at 前 10 位比较）；`GET /api/cameras?type=perimeter`。

- [ ] Step 1: 写失败测试：审计日志按 operator/module/日期过滤；摄像头按 type 过滤
- [ ] Step 2: `python -m pytest tests/test_resources.py -k "audit or camera_type" -v` 确认 FAIL
- [ ] Step 3: 实现：audit-logs 端点加 4 参数手写查询；`build_crud_router.list_items` 加 `type_: str|None = Query(None, alias="type")`，模型含 `type` 列时过滤
- [ ] Step 4: 全量 `python -m pytest` PASS

### Task 3: CameraView（T1/T2/T9）

**Files:**
- Modify: `frontend-vue/src/views/device/CameraView.vue`

要点：
- 类型筛选项改 perimeter/hook/cab（周界枪机/吊钩球机/驾驶室）；演示数据补 type
- `load()`：后端行映射（work_zone→location、状态文案→runtime、保留 code/resolution/rtsp_url/type）→ `applyFilters()` 客户端 keyword/status/type 过滤（对后端与回退数据一致生效）
- 统计卡改由列表计算：total=全量条数、onlineRate、alarm=演示告警数、storage 保持
- 「配置参数」：el-dialog 表单（name/type/ip/work_zone/resolution/rtsp_url/status），rules 校验（name 必填、ip 正则），保存尽力 `cameraApi.update` + 本地行更新
- 「新增摄像头」：el-dialog 表单（code/name/type/ip/work_zone/resolution/status），rtsp 按 ip 自动生成，`cameraApi.create` 成功用返回行，失败本地插入

- [ ] Step 1: 实现上述改动
- [ ] Step 2: build 通过；运行页面验证筛选（关键词/状态/类型）、新增、配置保存在两条路径下均生效

### Task 4: NvrView（T3/T4/T9）

**Files:**
- Modify: `frontend-vue/src/views/device/NvrView.vue`

要点：
- 高度一致：`.main{align-items:stretch}`；`.list-panel{display:flex;flex-direction:column}`、`.list-panel :deep(.body){flex:1;display:flex;flex-direction:column;min-height:0}`、表格容器 flex:1，el-table `height="100%"`（外层 min-height 480px 兜底）
- 列表按 code 升序；默认选中 usedCh 最大的一台
- 通道视图重做：格子内显示通道号，active(绿)/danger(红)/idle(暗+边框) 用主题变量，加图例行「在用/异常/空闲」，格子 title 提示
- keyword 回退过滤：load 后统一客户端按 code/name/ip 过滤
- 统计卡由列表计算：total、onlineRate、storageUsed(总used/总total)、abnormal(非 online 台数 + 满载通道)

- [ ] Step 1: 实现
- [ ] Step 2: 验证左右卡片总高一致、通道格子在明暗主题下清晰可见、搜索双路径可用

### Task 5: SpeakerLinkView（T5/T8/T9）

**Files:**
- Modify: `frontend-vue/src/views/speaker/SpeakerLinkView.vue`

要点：
- `.p-actions .el-button+.el-button{margin-left:0}`，按钮 width:100%
- poolKw → `filteredCranes`/`filteredSpeakers` computed（id/name 包含匹配）
- 播放试听：speechSynthesis zh-CN 播报（按 triggers 组合警示语 + 优先级），播放中禁用按钮，不支持时 ElMessage.warning
- 应用关联配置：per-crane {prio,triggers} 存 localStorage `qa-speaker-link-config` + 尽力 `configApi.save('speaker_link', all)`；selectCrane 时恢复；应用后写历史
- 拓扑已连接节点加 ✕ 解除关联（更新 links + 历史）
- 历史：初始化合并 localStorage `qa-speaker-link-history`，变更即持久化；删除 onMounted 用后端数据覆盖历史的逻辑
- 导出记录 → exportExcel（时间/操作人/动作/详情/状态）

- [ ] Step 1: 实现
- [ ] Step 2: 验证两按钮对齐、搜索、试听、配置持久化（刷新后保留）、解除关联、导出打开为有效 xlsx

### Task 6: ReportView 导出（T6）

**Files:**
- Modify: `frontend-vue/src/views/ReportView.vue`

- [ ] Step 1: `onExport()` 用 exportExcel 生成 5 个 Sheet：概览(指标/数值/统计区间)、事件明细(编号/类型/等级/状态/区域/设备/时间/处理人)、类型分布、区域分布、处置状态；数据取 `selectedEvents()` 当前筛选
- [ ] Step 2: 验证下载的 xlsx 内容与页面 KPI 一致

### Task 7: AuditLogView（T7/T8/T9）

**Files:**
- Modify: `frontend-vue/src/views/AuditLogView.vue`

- [ ] Step 1: `load()` 请求带 operator/module/start/end（日期→YYYY-MM-DD）；响应行映射 created_at→time；回退分支补日期区间过滤
- [ ] Step 2: `onExport()` 导出当前条件全量（后端 page_size=200 / 回退本地全集过滤）Excel
- [ ] Step 3: 验证：查询（操作人/模块/日期）双路径生效、翻页正常、导出为真实 xlsx

### Task 8: HeartbeatView 导出超时日志（T8）

**Files:**
- Modify: `frontend-vue/src/views/crane/HeartbeatView.vue`

- [ ] Step 1: 导出按钮绑定 handler：取 `rows` 中 status!=='online' 行导出（设备ID/状态/最后上报/延迟/丢包率/连续离线/异常描述）；空则 ElMessage.info
- [ ] Step 2: 验证 xlsx 内容

### Task 9: 零散查询修复（T9）

**Files:**
- Modify: `frontend-vue/src/views/config/ApprovalConfigView.vue`（kw→filteredFlows computed）
- Modify: `frontend-vue/src/views/violation/ViolationCategoryView.vue`（treeKw→filteredCategories computed）
- Modify: `frontend-vue/src/views/crane/RadarView.vue`（筛选按钮→状态 el-select：全部/在线/信号弱/离线，接入 filteredRows）
- Modify: `frontend-vue/src/views/ledger/RiskEventView.vue`（回退分支客户端 keyword/status 过滤）

- [ ] Step 1: 逐个实现
- [ ] Step 2: 验证各页搜索/筛选生效

### Task 10: 全量验证

- [ ] backend: `python -m pytest`（全绿）
- [ ] frontend: `npm run build`（无错误）
- [ ] 启动前后端，浏览器逐条走查 9 项任务（含明暗主题、后端关闭的回退路径抽查），截图记录
