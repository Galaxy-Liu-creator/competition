# 违章语义媒体校准实施计划

日期：2026-07-23

## 1. 固化失败测试

- 扩展 `backend-python/tests/test_demo_media.py`。
- 断言十种 `RE_TYPES` 和五种 GIS 告警均有显式映射。
- 断言 PPE 直接证据与传感器上下文模式正确。
- 断言 manifest 包含来源、许可、尺寸、哈希、`evidenceMode` 和 `evidenceFor`。
- 在生产代码修改前运行专项测试，确认因新映射/字段尚不存在而失败。

## 2. 接入授权素材

- 新建 `violations`、`lifting`、`equipment`、`access-control` 目录。
- 从已核验的临时候选目录复制最终 11 张图片，并使用语义化稳定文件名。
- 计算实际尺寸和 SHA-256。
- 扩展 `manifest.json` 和数据集 README，不删除用户已有图片。

## 3. 后端显式映射

- 重写 `app/data/demo_media.py`，用不可变显式字典取代关键词池。
- 增加 `EvidenceMedia`、`evidence_for_risk_event`、`evidence_for_alarm`。
- 保留路径兼容函数，供 mock 数据和 SQLite 同步使用。

## 4. 前端媒体与证据元数据

- 扩展 `src/data/demoMedia.js` 中的素材定义。
- 增加风险事件与 GIS 告警的显式映射和 `riskEvidenceFor` 查询函数。
- 保留 `riskMediaPath` 作为兼容包装。

## 5. 页面语义校准

- 调整 `CraneMonitorView.vue` 九路画面、告警文本和视频状态。
- 调整 `PerimeterCameraView.vue` 的周界、入口、离线和 PPE 正常画面。
- 调整 `RiskEventView.vue` 的证据模式、判定节点、说明和时间线。
- 调整 `RadarInfoView.vue` 的吊钩联动画面及遥测说明。

## 6. 数据同步与验证

- 运行专项后端测试并修复至通过。
- 运行全部后端测试。
- 运行前端生产构建。
- 校验 manifest 的文件存在性、尺寸、SHA-256，以及前后端路径集合一致性。
- 搜索并确认产品代码不再引用 `/static/events/` 或 `aswin_hoist_*`。

## 7. 浏览器验收

- 启动后端与 Vite 前端。
- 使用 Playwright 检查 `/crane/monitor`、`/crane/perimeter-camera`、`/crane/radar-info`、`/ledger/risk-events` 和 `/fence`。
- 在 1280×720 桌面视口和移动视口检查图片加载、布局、控制台、网络错误和文案语义。
- 在风险事件页面切换多个事件，验证图片、证据模式和判定来源同步变化。
- 截图仅保存到系统临时目录。

## 8. 工作区交付检查

- 运行 `git diff --check`、`git diff --stat`、`git status --short`。
- 仅报告本轮相关修改，不提交、不重置、不清理用户其他改动。
