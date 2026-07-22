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

## 地图接入(待配置)

地图区域当前使用 `src/components/map/MapPlaceholder.vue` 占位。拿到高德 Web Key 后,在
`frontend-vue/.env.local`(勿提交 Git)配置:

```env
VITE_MAP_PROVIDER=amap
VITE_AMAP_KEY=your-key
VITE_AMAP_SECURITY_CODE=your-security-code
```

后端已提供 `GET /api/sites/{siteId}/map-overview` 聚合接口(站点/设备点位/GIS 围栏/告警/天气,GCJ-02),接入时按 `docs/后端技术栈与地图接入方案.md` 的适配层方案实现即可。

## 测试

```powershell
cd backend-python && python -m pytest tests -q   # 22 passed
cd frontend-vue && npm run build                  # 构建验证
```
