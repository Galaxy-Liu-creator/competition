# 演示媒体与数据集归属

这里的图片用于前端监控画面、风险事件证据帧、周界摄像头和雷达联动窗口。图片是真实的公开/授权图像；页面上的时间戳、设备编号、状态、检测框、电子围栏、危险区和遥测数值是本系统的确定性演示叠加，不是这些照片的真实现场记录，也不代表已运行真实模型推理。

完整的机器可读来源、作者、许可证、归属文本、实际尺寸、SHA-256、`evidenceMode` 和 `evidenceFor` 位于同目录的 [`manifest.json`](./manifest.json)。产品代码只引用 manifest 管理的稳定路径，不引用许可不明的 `aswin_hoist_*.jpg` 或 `/static/events/` 图片。

## 证据模式

- `direct-visual`：关键事实可从原始画面直接观察，例如未佩戴安全帽、未使用防坠设备、危险停放或不安全吊点。
- `overlay-assisted`：原图提供人物、围栏、吊物或作业面，是否进入电子围栏/吊装危险区由演示叠加确定。
- `sensor-context`：原图只提供设备或作业上下文；载荷百分比、风速、心跳、限位状态和吊钩姿态来自确定性演示遥测。

## 原有施工与 PPE 素材

- [Tower crane aerial 01](https://commons.wikimedia.org/wiki/File:Tower_crane_aerial_01.jpg) — Wikideas1 — CC0 1.0。
- [Tower crane aerial 02](https://commons.wikimedia.org/wiki/File:Tower_crane_aerial_02.jpg) — Wikideas1 — CC0 1.0。
- [Mobile crane E16](https://commons.wikimedia.org/wiki/File:Mobile_crane_E16.jpg) — sludgegulper — CC BY-SA 2.0。
- [Mobile crane lifting precast concrete walls (1)](https://commons.wikimedia.org/wiki/File:Mobile_crane_lifting_precast_concrete_walls_for_the_constrution_of_a_three-storey_international_style_hotel_(1).jpg) — Bidgee — CC BY-SA 3.0 AU。
- [A Liebherr LTM 1500-8.1 crane truck lifting a Genie S-85 Lift Crane 02](https://commons.wikimedia.org/wiki/File:A_Liebherr_LTM_1500-8.1_crane_truck_lifting_a_Genie_S-85_Lift_Crane_02.jpg) — Tbatb — CC BY-SA 4.0。
- [Construction worker CT](https://commons.wikimedia.org/wiki/File:Construction_worker_CT.jpg) — HelenOnline — CC BY-SA 3.0。
- [Baliwagenyo welder with green hard hat 02](https://commons.wikimedia.org/wiki/File:Baliwagenyo_welder_with_green_hard_hat_working_atop_a_petrol_station_metal_structure_02.jpg) — FBenjr123 — CC BY-SA 4.0。
- [Woman with chop saw and hard hat](https://commons.wikimedia.org/wiki/File:Woman_with_chop_saw_and_hard_hat_(3401747795).jpg) — Sean McGrath — CC BY 2.0。
- [Construction worker - 8217](https://commons.wikimedia.org/wiki/File:Construction_worker_-_8217.jpg) — Jorge Royan — CC BY-SA 3.0。
- [Construction workers not wearing fall protection equipment](https://commons.wikimedia.org/wiki/File:Construction_workers_not_wearing_fall_protection_equipment.jpg) — NIOSH — 公共领域。
- [Construction Workers](https://commons.wikimedia.org/wiki/File:Construction_Workers.jpg) — Paul Keheler — CC BY 2.0。

## 本轮违章语义校准素材

### 直接违章与作业面

- [Worker without proper safety equipment](https://commons.wikimedia.org/wiki/File:Worker_without_proper_safety_equipment.jpg) — NIOSH — 公共领域；用于未佩戴安全帽的直接视觉证据。
- [Crane parked dangerously](https://commons.wikimedia.org/wiki/File:Crane_parked_dangerously.jpg) — NIOSH — 公共领域；用于危险停放/违章操作的直接视觉证据。
- [Drywall Crane Workers](https://commons.wikimedia.org/wiki/File:Drywall_Crane_Workers.jpg) — NIOSH — 公共领域；用于杂乱物料堆场和吊装作业面。

### 吊装与雷达联动

- [20,000-pound load during a crane lift](https://commons.wikimedia.org/wiki/File:US_Navy_100308-N-1120L-014_Seabees_assigned_to_(NMCB)_7_use_tag_lines_to_steady_a_20,000-pound_load_during_a_crane_lift_to_load_cargo_onto_a_tractor_trailer.jpg) — Michael B. Lavender / U.S. Navy — 公共领域；用于重载起吊场景，超载结论来自载荷遥测。
- [Trench safety - guiding the trench box](https://commons.wikimedia.org/wiki/File:Trench_safety_-_guiding_the_trench_box_(9250664732).jpg) — NIOSH — 公共领域；用于悬吊构件危险区叠加。原图是正确操作示范，不被描述成原始违章记录。
- [Trench safety - improper eyebolt](https://commons.wikimedia.org/wiki/File:Trench_safety_-_improper_eyebolt_(9247876609).jpg) — NIOSH — 公共领域；用于不安全吊点上下文，斜拉角度来自姿态遥测。
- [Construction Worker (8098562099)](https://commons.wikimedia.org/wiki/File:Construction_Worker_(8098562099).jpg) — Tony Alter — CC BY 2.0；用于吊钩指挥和雷达视频联动。
- [Tanjung-Badak Sabah Crane-lifting-ashlars-02](https://commons.wikimedia.org/wiki/File:Tanjung-Badak_Sabah_Crane-lifting-ashlars-02.jpg) — Uwe Aranas — CC BY-SA 3.0；用于吊臂作业面和回转区域叠加。

### 设备与出入口

- [Potain tower crane4 - Cabin](https://commons.wikimedia.org/wiki/File:Potain_tower_crane4_-_Cabin.jpg) — Cjp24 — CC BY-SA 4.0；画面包含塔吊驾驶室和杯式风速仪，用于风速/限位传感器上下文。
- [China Construction Site Safety](https://commons.wikimedia.org/wiki/File:China_Construction_Site_Safety.jpg) — Aussie72 — CC BY-SA 3.0；用于工地入口、摄像头和设备心跳上下文。
- [立入禁止 (33881687926)](https://commons.wikimedia.org/wiki/File:%E7%AB%8B%E5%85%A5%E7%A6%81%E6%AD%A2_(33881687926).jpg) — se7en — CC BY 2.0；用于周界禁入区域和电子围栏叠加。

## 使用边界

设备、心跳、遥测、风险事件时间线、天气和报表数字由后端 SQLite 确定性种子提供，均为演示数据。没有随图片一起发布的官方检测框会以 `displayOverlay: "demo-overlay"` 标记；UI 叠加框只用于展示交互，不应被解释为原始标注。

曾评估的第三方 PPE/施工安全聚合数据集样本中出现商业图库水印或单图再许可范围不清，因此没有纳入最终产品媒体目录。
