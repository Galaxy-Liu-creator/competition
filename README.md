# 擎安智吊 · 吊装场景智能巡检系统

深色工业监控风格的吊装安全运营平台(比赛演示版),1:1 复刻 `picture/Stitch生成稿-高清/` 共 21 张设计稿(含登录页与个人设置页)。

```text
Vue 3 + Vite + Element Plus + ECharts        frontend-vue/
        │  Vite 代理 /api → 127.0.0.1:8000
        ▼
FastAPI + SQLAlchemy 2.0 + SQLite            backend-python/ (app.db 自动建表播种)
```

## 启动

后端(首次启动自动创建 `app.db` 并写入种子数据):

```powershell
cd backend-python
pip install -r requirements.txt
python run.py            # http://127.0.0.1:8000 ,接口文档 /docs
```

前端:

```powershell
cd frontend-vue
npm install
npm run dev              # http://127.0.0.1:5173
```

所有页面在后端未启动时会自动回退到内置演示数据,便于纯前端演示。

## 登录与认证

- 演示账号:`admin / admin123`(仅供演示,种子数据写入 `users` 表,bcrypt 哈希存储)
- 后端 JWT 认证(`POST /api/auth/login`),除登录与健康检查外所有 `/api/*` 接口均需 `Authorization: Bearer <token>`
- JWT 密钥经 `backend-python/.env` 的 `JWT_SECRET` 配置(默认值仅供演示,生产必须覆盖)
- 前端路由守卫:未登录跳转 `/login`;个人设置页(`/settings`)支持编辑资料、明暗主题(夜间/日间/跟随系统)、通知偏好、默认落地页与修改密码
- 后端未启动时,登录页回退本地校验演示账号,保持纯前端可演示

## 功能模块(对应设计稿)

- 工作台(01):统计卡、作业区鸟瞰、实时告警队列、设备健康/风险趋势/高发违章
- 吊车管理(02/07-12/17):吊车、实时监控、周界摄像头、心跳检测、设备关联、设备类型、边缘盒子、雷达传感器、雷达信息
- 摄像头管理(03)、录像机管理(04)、音柱管理(05/18)
- 台账管理·风险事件处置(13,含处置流转与时间线)
- 违章类型·违章大类管理(14)
- 基础配置(06/15/16/19):系统、审批、阈值、推送策略
- 登录页(20)、个人设置页(21):JWT 登录、明暗主题切换、偏好设置
- 电子围栏、安全报表、审计日志(无设计稿,按同风格补全)

## 地图接入与离线回退

地图区域由 `src/components/map/SiteMap.vue` 渲染。高德 Web Key 演示值已随仓库放在
`frontend-vue/.env` 中,clone 后地图开箱即用;如需换用自己的 key,在
`frontend-vue/.env.local`(不入库,优先级更高)覆盖:

```env
VITE_AMAP_KEY=your-key
VITE_AMAP_SECURITY_CODE=your-security-code
```

后端已提供 `GET /api/sites/{siteId}/map-overview` 聚合接口(站点/设备点位/GIS 围栏/告警/天气,GCJ-02)。缺少 key、SDK 加载失败或业务接口暂不可用时,前端会自动切换到本地 SVG 离线示意图,并明确标注“GCJ-02 演示坐标”。

## 前端媒体与数据集归属

监控画面和风险证据帧使用 `frontend-vue/public/dataset/` 中的公开/授权图片,来源、作者、许可证、归属文本和 SHA-256 集中记录在 [`frontend-vue/public/dataset/manifest.json`](frontend-vue/public/dataset/manifest.json),人类可读说明见 [`frontend-vue/public/dataset/README.md`](frontend-vue/public/dataset/README.md)。主要来源包括:

- Wikimedia Commons 的逐图 CC0、公共领域、CC BY 2.0、CC BY-SA 2.0、CC BY-SA 3.0/3.0 AU 和 CC BY-SA 4.0 塔吊、施工现场、作业人员与安全防护图片。
- PPE/人员素材均按 Commons 单个文件页核验作者与许可证；曾评估但带商业图库水印的第三方样本没有进入最终产品媒体目录。

页面通过 `frontend-vue/src/data/demoMedia.js` 的稳定媒体 ID 引用图片,不引用没有许可证声明的 `aswin_hoist_*.jpg` 文件。图片是真实公开素材;设备状态、遥测、告警时间线、天气和报表数字仍是后端确定性演示种子数据。未附带官方检测框的图片上的框和标签是 `demo-overlay`,不代表真实模型推理。

## 测试

```powershell
cd backend-python && python -m pytest tests -q   # 当前测试集应全部通过
cd frontend-vue && npm run build                  # 构建验证
```
