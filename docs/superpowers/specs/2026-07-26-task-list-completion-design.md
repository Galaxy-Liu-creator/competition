# 任务清单完成方案设计（2026-07-26）

对应 `docs/任务清单.txt` 的 9 项任务。总原则：

1. **双路径可用**：每个功能在「后端在线」与「纯前端回退（演示数据）」两种模式下都必须真实可用。做法是统一在前端做最终过滤/映射，后端能力作为增强。
2. **真实导出**：所有导出按钮生成真实 `.xlsx` 文件（SheetJS `xlsx` 库），不再弹「演示」提示。
3. **遵循演示约束**（见项目记忆）：不用真实地名；主题变量（`--qa-*`）适配明暗主题；不展示演示账号。

## 各任务设计

### T1 摄像头「配置参数」面板（CameraView.vue）

- 用 `el-dialog` 实现配置面板：设备名称、类型（perimeter/hook/cab）、IP 地址、所在区域、分辨率/型号、RTSP 地址、运行状态。
- 表单校验：名称必填、IP 格式校验。
- 保存：`cameraApi.update(id, payload)` 尽力而为；无论后端是否成功，同步更新本地行 + 成功提示（与项目既有「演示忽略」模式一致）。

### T2 摄像头筛选 + 新增（CameraView.vue + 后端）

- **类型值对齐后端**：筛选项改为 周界枪机(perimeter)/吊钩球机(hook)/驾驶室(cab)，演示数据补上 `type` 字段。
- **后端行映射**：`work_zone→location`、状态→runtime 文案，补 `code/resolution` 展示。
- **统一客户端过滤**：load() 拿到数据（后端或回退）后，前端按 keyword/status/type 过滤，保证任何模式筛选都生效；关键词即时回车触发。
- **后端增强**：`build_crud_router` 列表端点新增可选 `type` 查询参数（模型有 `type` 列时生效），带 pytest。
- **新增摄像头**：`el-dialog` 表单（编号/名称/类型/IP/区域/分辨率/状态，RTSP 由 IP 自动生成），`cameraApi.create` 成功用后端返回行，失败本地插入；统计卡随列表数据实时计算（总数/在线率）。

### T3 录像机卡片高度一致（NvrView.vue）

- 用 ViolationCategoryView 已有的 flex 填充模式：`.main` grid 拉伸，左侧 `.list-panel` 变 flex 列、`:deep(.body)` flex:1，`el-table` `height="100%"`（含 min-height 兜底），左卡高度自动与右列三卡总高一致。
- 统计卡从真实列表数据计算（总数/在线率/存储使用率/异常通道）。

### T4 录像机通道视图（NvrView.vue）

- 根因：默认选中逻辑 `find(code==='NVR-B02')` 永不匹配后端数据，回退到 id 倒序第一台 NVR-08（0 通道在用）+ 空闲格子颜色与面板底色几乎一致 → 看起来"无内容"。
- 修复:列表按 code 升序展示；默认选中在用通道最多的一台；通道格子重做：显示通道号、active/danger/idle 三态高分辨色 + 边框、加图例（在用/异常/空闲）、title 提示。

### T5 音柱关联完善（SpeakerLinkView.vue）

- **按钮对齐**：`.p-actions` 为 column flex，覆盖 Element Plus 的 `.el-button+.el-button{margin-left:12px}` 为 0，两钮等宽。
- **设备池搜索**：poolKw 接入 computed 过滤吊车与音柱两组列表。
- **播放试听**：Web Speech API (zh-CN) 真实播报警示语（按当前触发项组合文案），不支持时降级提示；播放中按钮置忙。
- **应用关联配置**：按吊车持久化 {优先级, 触发项} 到 localStorage（键 `qa-speaker-link-config`）并尽力写后端 `configApi.save('speaker_link', …)`；切换吊车时载入对应配置；应用后写入关联历史。
- **解除关联**：拓扑图已连接节点加 ✕，点击解除（更新 links + 历史）。
- **关联历史**：不再被后端形状不符的数据覆盖（删除 onMounted 覆盖逻辑），历史本地持久化（localStorage）；「导出记录」改为真实 Excel 导出。

### T6 安全报表导出 Excel（ReportView.vue + 新 util）

- 新增 `src/utils/exportExcel.js`：`exportExcel({ filename, sheets:[{name, columns:[{label,key,width}], rows}] })`，基于 `xlsx` 生成多 Sheet 工作簿并下载（自动拼日期后缀）。
- 报表导出 Sheet：概览(KPI+统计区间)、事件明细、类型分布、区域分布、处置状态，数据取当前筛选范围（range/日期）。

### T7 审计日志查询 + 导出（AuditLogView.vue + 后端）

- **后端**：`/api/audit-logs` 新增 `operator`（模糊）、`module`（精确）、`start`/`end`（created_at 日期前缀范围）参数，带 pytest。
- **前端**：请求带上述参数（日期格式化 YYYY-MM-DD）；响应行映射 `created_at→time`（"YYYY-MM-DD HH:mm:ss"）；回退分支补日期过滤。
- **导出**：导出当前筛选条件下的全量数据（后端拉 page_size=200；回退取本地过滤全集）为 Excel。

### T8 所有导出真实 Excel

- ReportView（T6）、AuditLogView（T7）、SpeakerLinkView 导出记录（T5）、HeartbeatView「导出超时日志」（导出 status≠online 的行，含设备/状态/最后上报/延迟/丢包/连续离线/异常描述；无数据时提示）。

### T9 所有查询可用

已可用（前端 computed）：CraneList、DeviceLink、DeviceType、EdgeBox、Heartbeat、PerimeterCamera、Radar 搜索框。
需修复：

| 页面 | 问题 | 方案 |
| --- | --- | --- |
| CameraView | 回退不过滤 + type 值错位 | T2 |
| NvrView | 回退不过滤 | load 后统一客户端 keyword 过滤 |
| RiskEventView | 回退不过滤 | 回退分支按 keyword/status 客户端过滤 |
| AuditLogView | 后端不支持参数 + 回退缺日期过滤 | T7 |
| SpeakerLinkView | poolKw 未接线 | T5 |
| ApprovalConfigView | kw 未接线 | computed 过滤流程列表 |
| ViolationCategoryView | treeKw 未接线 | computed 过滤大类树 |
| RadarView | 「筛选」按钮无功能 | 改为状态下拉筛选（全部/在线/信号弱/离线）接入 filteredRows |

## 测试与验证

- 后端：pytest 新增审计日志过滤、摄像头 type 过滤用例；全量测试通过。
- 前端：`npm run build` 通过；启动前后端后用浏览器逐任务验证（截图核对）,覆盖明暗主题。
