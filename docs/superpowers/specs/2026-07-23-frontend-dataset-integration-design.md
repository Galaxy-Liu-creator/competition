# 前端数据集与证据媒体整合设计

## 背景

本系统是一个 Vue 3 + Vite 的吊装施工安全监管演示系统，后端使用 FastAPI、SQLAlchemy 和 SQLite 提供设备、心跳、风险事件、GIS 站点等结构化接口。前端已有若干页面级演示图片，但图片来源没有集中记录，部分引用来自没有公开许可证声明的数据集，风险事件接口还返回不存在的 `/static/events/*.jpg` 路径。

本次工作将“可追溯的真实公开图像”和“用于演示业务流程的模拟结构化数据”明确分开：公开图像只承担视觉证据和监控画面展示；设备状态、遥测、告警时间线和报表数值继续由确定性的后端种子数据提供，并在文档中标注为模拟数据。

## 目标与非目标

### 目标

1. 为前端视觉区域提供一组稳定、可追溯、具有明确授权信息的施工现场与 PPE 图片。
2. 让每个前端图片引用都通过统一媒体目录解析，避免页面自行拼接随机路径。
3. 让风险事件和 GIS 告警接口返回可加载的前端静态媒体路径。
4. 保留现有 API 数据结构和数据库表结构，不引入不必要的迁移。
5. 提供机器可读的媒体清单、许可证归属和校验哈希，并在根 README 中解释数据真实性边界。
6. 在后端测试、前端构建和浏览器关键页面检查中验证资源路径和回退行为。

### 非目标

- 不把公开图像伪装成现场实时流或真实传感器数据。
- 不新增在线标注服务、模型推理服务或数据库媒体表。
- 不删除用户已有的未跟踪截图、组件或图片二进制；未授权图片只停止被代码引用，并在清单中注明不纳入产品媒体目录。
- 不改变现有登录、路由、CRUD 和风险事件处置 API 契约。

## 数据集与授权决策

### 采用的数据源

| 用途 | 数据源 | 授权 | 内容 | 处理方式 |
| --- | --- | --- | --- | --- |
| 作业人员/PPE 证据帧 | Wikimedia Commons 中逐图核验的文件 | 公共领域、CC BY 2.0、CC BY-SA 3.0/4.0 | hard-hat、fall-protection、eye-protection、work-at-height、person | 每张图片单独记录 Commons 文件页、原作者、许可证、实际尺寸和 SHA-256；UI 检测框统一标注为演示叠加 |
| 施工现场/塔吊照片 | Wikimedia Commons 中逐图有许可证的文件（CC0、公共领域、CC BY/CC BY-SA） | 以每张图片的 Commons 文件页为准 | 塔吊、施工现场、起重作业 | 每张图片单独记录文件页、原作者、许可证和归属文本；没有真实检测框的图片只显示“演示叠加框” |

### 明确排除的数据源

`aswin00000/ConstructionSiteCleanedDataSet` 没有在 Hugging Face 元数据或 README 中提供许可证声明。因此现有 `aswin_hoist_*.jpg` 文件不进入新媒体目录，也不得继续被前端或后端代码引用。为避免破坏用户工作区，除非后续明确要求，不删除这些二进制文件。

`LibreYOLO/construction-safety-gsnvb` 曾作为候选来源评估，但抽样图片中出现 Shutterstock、Alamy 等商业图库水印，聚合数据卡不足以证明底图可以按所声明许可证再分发，因此不进入最终产品媒体目录。

## 媒体目录与接口

新增目录结构：

```text
frontend-vue/public/dataset/
├── construction/       # Commons 施工现场/塔吊图片
├── ppe/                # Commons 逐图核验的人员/PPE 安全图片
├── labels/             # 可选的本地演示标注说明，不冒充原始标注
├── manifest.json       # 机器可读来源、许可证、哈希和标签
└── README.md           # 人类可读归属和使用边界
```

新增 `frontend-vue/src/data/demoMedia.js`，导出：

- `DEMO_MEDIA`: 以稳定 ID 为键的媒体记录；每条记录包含 `id`、`path`、`kind`、`tags`、`source`、`license`、`attribution`、`overlay`。
- `MEDIA_PATHS`: 供后端种子或页面选择的稳定路径常量。
- `mediaById(id)` 和 `mediaPath(id, fallbackId)`：在 ID 不存在时给出明确、可加载的默认媒体。

页面只依赖媒体 ID 或目录函数，不再维护重复的 `imgPool`。所有 Commons 图片均未携带本项目可验证的原始检测框，因此统一标注 `overlay: "demo-overlay"`。

## 页面映射

- Workbench：统计、趋势、告警和地图继续使用后端 API；不把外部数据集数值当作现场遥测。
- Crane Monitor：视频网格使用 `construction` 与 `ppe` 媒体；告警框是演示叠加，并在媒体清单中说明。
- Perimeter Camera：周界画面使用施工现场/PPE 媒体；离线摄像头继续显示无信号状态。
- Radar Info：联动视频使用许可明确的施工现场媒体；雷达目标仍来自 `/api/radars/{id}/readings`，失败时使用页面内确定性回退。
- Risk Events：优先使用后端 `image_url`；若接口没有图片才按事件类型从媒体目录选择稳定回退，不再按列表索引轮换图片。
- 其他设备、心跳、配置和报表页面：继续使用后端确定性种子；必要时只在视觉区域调用媒体目录。
- Fence/SiteMap：保留 GCJ-02 演示坐标；没有 AMap key 时显示可操作的离线地图回退，不把地图瓦片截图当作数据集证据。

## 后端种子策略

新增小型 `app/data/demo_media.py`（或等价的集中常量模块），只保存稳定的 `/dataset/...` 路径和按风险类型选择媒体的函数。`seed.py` 为 36 条风险事件按事件类型确定性分配路径，并为 legacy 地图告警的 `evidence.imageUrl` 使用同一组路径。路径不能指向 `/static/events` 或 `aswin_hoist_*`。

SQLite 当前使用 `create_all`，因此本次不修改 `RiskEvent` 表结构，不做迁移。已有数据库在重新运行种子时不会覆盖已存在记录；测试需使用空/隔离数据库验证新种子规则，并用 API 断言现有数据库中的返回值也不含禁用路径。

## 真实性与标注边界

所有结构化设备、遥测、告警和天气值均为确定性的演示种子数据；它们不是外部现场的实时数据。Commons 图片没有原始目标框，UI 上的框、标签和“AI EVIDENCE”仅是演示叠加，不代表图片作者、Commons 或模型推理结果。

## 验收标准

1. `manifest.json` 中每个被前端引用的媒体都有来源 URL、作者、许可证、归属文本、标签和 SHA-256。
2. `rg "aswin_hoist_|/static/events" frontend-vue/src backend-python/app` 无结果（排除明确的历史说明文档/不纳入产品的清单记录）。
3. 风险事件 API 返回的 `image_url` 为 `/dataset/...` 且对应文件存在；GIS 告警证据路径同样满足此条件。
4. 后端新增测试覆盖：路径前缀、禁用路径、确定性映射和文件存在性。
5. `pytest` 全部通过，`npm run build` 成功。
6. 浏览器检查登录、Workbench、Crane Monitor、Perimeter Camera、Radar Info、Risk Events 和 Fence/map fallback：图片加载成功、关键 API 无失败请求、控制台无新增错误。
