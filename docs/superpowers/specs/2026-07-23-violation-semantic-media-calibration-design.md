# 违章语义媒体校准设计

日期：2026-07-23

## 背景

现有演示媒体文件、尺寸和 SHA-256 均完整，但后端和前端按“人物、吊装、工地”大类或关键词池稳定取图。该策略只能保证画面大致属于施工主题，不能保证图片主体支持“未佩戴安全帽、违规闯入、超载起吊、设备离线、限位失效”等具体描述，因而产生大量语义错配。

本轮不删除用户已修改的图片，也不改变风险事件 API 的现有字段结构。校准目标是把每个事件类型映射为确定的授权媒体，并在 UI 中明确区分图片可以直接证明的事实与必须依靠电子围栏或传感器才能判定的事实。

## 证据模式

所有风险媒体必须声明下列模式之一：

- `direct-visual`：关键事实在原始画面中直接可见，例如未戴安全帽、未使用防坠设备、危险停放或不合格吊点。
- `overlay-assisted`：画面中存在人物、围栏、吊物或危险作业面，但“是否进入算法危险区”由演示电子围栏或危险区叠加表达。
- `sensor-context`：照片只提供对应设备或作业场景；载荷百分比、风速、心跳、限位状态、吊钩倾角等结论来自确定性演示遥测，不能宣称照片本身证明该数值。

## 数据源边界

最终新增素材仅采用 Wikimedia Commons 可逐图核验的文件：

- NIOSH / 美国联邦政府 / 美国海军公共领域作品；
- 明确标注 CC BY、CC BY-SA 或 CC0 的 Commons 文件；
- 对下载的 Commons 缩略图保留原始文件页、原始文件 URL 和实际缩略图 URL。

不采用带商业图库水印、聚合来源无法追溯底图许可、或仅有数据集级许可证但单图来源不清的图片。

## 风险事件映射

| 事件类型 | 媒体 ID | 证据模式 | UI 判定来源 | 说明 |
| --- | --- | --- | --- | --- |
| 违规闯入 | `restrictedConstructionFence` | `overlay-assisted` | 电子围栏联动 | 围栏、禁入标识和人员同框，越界关系由演示围栏叠加表达 |
| 超载起吊 | `heavyLoadLift` | `sensor-context` | 载荷传感器联动 | 画面明确为 20,000 磅重载起吊，但演示事件是否超额由载荷遥测判定 |
| 未佩戴安全帽 | `workerWithoutPpe` | `direct-visual` | 视觉识别证据 | 高处人员未佩戴安全帽且缺少 PPE |
| 违章操作 | `unsafeCraneParking` | `direct-visual` | 人工巡检证据 | NIOSH 说明为危险停放的重型设备 |
| 斜拉斜吊 | `improperEyebolt` | `sensor-context` | 吊钩姿态传感器联动 | 图片直接展示不安全吊点；斜拉角度仍由吊钩姿态/摆角遥测判定 |
| 设备离线 | `constructionSiteEntrance` | `sensor-context` | 设备心跳联动 | 入口摄像头和工地场景可见，离线结论来自心跳状态 |
| 大风超阈值起吊 | `towerCraneAnemometer` | `sensor-context` | 风速传感器联动 | 塔吊驾驶室和杯式风速仪可见，阈值结论来自风速遥测 |
| 吊物下方站人 | `trenchBoxGuidance` | `overlay-assisted` | 吊装危险区联动 | 人员与悬吊构件同框，演示危险区叠加表达进入关系；原图为安全教学示范 |
| 未系安全带 | `ppeSite0701` | `direct-visual` | 视觉识别证据 | NIOSH 高处人员未使用防坠设备 |
| 限位失效 | `towerCraneAnemometer` | `sensor-context` | 限位传感器联动 | 塔吊控制设备场景；限位状态不可由静态照片直接判断 |

## GIS 告警映射

| 告警类型 | 媒体 ID | 证据模式 |
| --- | --- | --- |
| `person_in_rotation_radius` | `craneLiftingAshlars` | `overlay-assisted` |
| `overload_risk` | `heavyLoadLift` | `sensor-context` |
| `device_offline` | `constructionSiteEntrance` | `sensor-context` |
| `cross_fence` | `restrictedConstructionFence` | `overlay-assisted` |
| `no_helmet` | `workerWithoutPpe` | `direct-visual` |

## 页面校准

### 实时监控

九路视频按实际画面重新匹配：吊臂作业面使用工人与吊钩同框图；南侧围栏使用禁入围栏图；吊装落区使用悬吊构件与人员同框图；车辆通道保留汽车吊；塔基保留塔吊航拍；物料堆场使用杂乱吊装工地图；高空作业面使用无防坠设备图；东门闸口使用中国工地入口图；主臂回转区使用重载吊装图并以区域叠加表达。

### 周界摄像头

东区周界使用禁入围栏图并显示“电子围栏越界联动”；南区大门使用工地入口图，作为车辆识别能力的普通画面；离线设备不显示伪造画面；物料区的安全帽检测画面明确显示为“PPE 检测正常”，不冒充告警。

### 风险事件详情

详情面板不再固定显示 `AI EVIDENCE`、`AI_VISION_NODE_03` 和“实时录制中”。它根据事件类型展示证据模式、判定来源、证据说明和对应的视觉/围栏/遥测时间线。

### 雷达信息

联动窗口使用真实吊钩指挥人员画面，并明确载重、风速和目标数据来自雷达与吊机遥测，不把叠加数值描述为图片中的视觉事实。

## 数据与兼容性

- 后端通过显式字典返回确定路径和证据元数据，保留 `image_for_risk_event` 与 `image_for_alarm` 兼容接口。
- 前端通过显式字典返回媒体路径、证据模式、标签、来源节点和说明。
- SQLite 的 `_sync_demo_media` 在应用启动时把已有风险事件与 GIS 告警更新为新路径。
- `manifest.json` 为每张素材保存来源、许可、实际尺寸、SHA-256、`evidenceMode` 与 `evidenceFor`。
- 新目录为 `/dataset/violations/`、`/dataset/lifting/`、`/dataset/equipment/` 和 `/dataset/access-control/`。

## 验收标准

- 十种后端风险事件和五种 GIS 告警均有显式、确定映射。
- `未佩戴安全帽` 不再映射到正确佩戴安全帽的合规照片。
- `未系安全带` 继续使用直接显示缺少防坠设备的照片。
- 超载、斜拉角度、设备离线、风速阈值和限位状态全部声明为 `sensor-context`。
- manifest 中全部受管素材文件存在，尺寸和 SHA-256 与文件一致。
- 风险详情中的证据标签和判定来源随事件类型切换。
- 前后端专项测试、全量测试、前端构建以及桌面/移动 Playwright 验收通过。
