# 风险事件/实时监控/周界摄像头 配图语义校准与截断修复 设计文档

日期：2026-07-26
状态：已按用户指令自主执行（延续 2026-07-23 violation-semantic-media-calibration 已批准模式）

## 问题

1. **语义不贴合**：多处演示图片与事件/摄像头描述不符——"违规闯入"用的是日本自行车停车场照片、"斜拉斜吊"是手持吊环螺栓特写、"吊物下方站人"是挖掘机吊运草坪教学照、CAM-P-004"物料区"是室内切割台照片。
2. **图片截断**：三个页面均为固定高度容器 + `object-fit: cover`，竖幅原图（722×1024、1500×2100、2000×3000、1920×2868）被裁剪掉大部分画面。

## 方案

### A. 素材来源边界（沿用已批准 spec）

仅采用 Wikimedia Commons 可逐图核验许可的图片（现有测试也强制 `commons.wikimedia.org` 来源页 + `upload.wikimedia.org` 文件 URL）。已调研 GitHub 上的工程 CV 数据集（SODA/MOCS/Roboflow 爬取集等），均为数据集级许可、单图出处不可溯源，不满足 manifest 逐图核验边界，故不采用。

### B. 新增 7 张素材与映射（均为横幅、监控视角可信）

| 媒体 ID | 文件 | 用途 | 许可 |
|---|---|---|---|
| site-gate-pedestrians | access-control/site-gate-pedestrians.jpg | 违规闯入 / cross_fence / CAM-P-001 东区周界 | CC BY-SA 3.0 |
| site-fence-warning-sign | access-control/site-fence-warning-sign.jpg | CAM-09 南侧围栏 | CC BY-SA 4.0 |
| site-yard-tower-cranes | construction/site-yard-tower-cranes.jpg | CAM-13 物料堆场 | CC BY-SA 4.0 |
| girder-heavy-lift | lifting/girder-heavy-lift.jpg | 超载起吊 / overload_risk / CAM-16 主臂回转区 | CC BY 2.0 |
| angled-girder-rigging | lifting/angled-girder-rigging.jpg | 斜拉斜吊 | CC BY 2.0 |
| girder-landing-zone | lifting/girder-landing-zone.jpg | 吊物下方站人 / CAM-10 吊装落区 | CC BY 2.0 |
| rebar-deck-crew | ppe/rebar-deck-crew.jpg | CAM-P-004 物料区（PPE 检测正常）| CC BY-SA 3.0 |

证据模式（evidence_mode）保持不变（测试钉死）；仅换图并更新 note 文案。
未佩戴安全帽 / 未系安全带 / 违章操作 / 设备离线 / 大风 / 限位失效 及 CAM-08/11/12/14/15、CAM-P-002 沿用现图（语义已贴合）。
旧素材文件保留（其他页面仍在引用），仅从被替换槽位的 evidenceFor 中移除对应事件键。

### C. 截断修复（三个视图统一"双层图"模式）

容器保持固定高度；内部改为两层同源图片：
- 背景层：`object-fit: cover` + `blur + 降亮`，铺满容器消除黑边；
- 前景层：`object-fit: contain`，完整展示原图（NVR letterbox 效果）。

涉及 `RiskEventView .ev-box`（高度 200→230px）、`CraneMonitorView .feed`、`PerimeterCameraView .screen`。

### D. 同步面

manifest.json（7 条新资产：sha256/尺寸/作者/许可/attribution/evidenceFor）、
demo_media.py（DATASET_PATHS + 4 类型重映射）、demoMedia.js（镜像）、seed `_sync_demo_media` 启动自愈已有库。

## 验证

pytest tests/test_demo_media.py 全绿 + 全量后端测试；Playwright 截图三页面确认语义与无截断。
