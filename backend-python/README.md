# 擎安智吊后端

本目录是 `new_project` 的独立 FastAPI 后端。参考项目
`D:\University-Competition\Innovation_Entrepreneurship\project` 仅用于读取技术栈和接口风格，未被修改。

当前版本提供态势总览、站点、设备点位、GIS 电子围栏、地图告警和地图聚合数据。地图数据均显式标记为 `gcj02`；围栏点是经纬度，不复用视频画面中的像素坐标。

## 技术栈

- FastAPI 0.115.6
- Uvicorn 0.34.0
- Pydantic 2.12.4
- pydantic-settings 2.7.0
- pytest + FastAPI TestClient

## 安装与启动

```powershell
cd D:\University-Competition\Innovation_Entrepreneurship\new_project\backend-python
pip install -r requirements.txt
python run.py
```

也可以直接运行：

```powershell
uvicorn app.main:app --reload --port 8000
```

服务地址：`http://127.0.0.1:8000`

- Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## 统一响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

资源不存在时使用 HTTP 404 和业务码 `1004`：

```json
{
  "code": 1004,
  "message": "站点不存在",
  "data": null
}
```

## 接口

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |
| GET | `/api/dashboard/overview` | 态势总览首屏聚合数据 |
| GET | `/api/dashboard/stats` | 核心统计卡片 |
| GET | `/api/dashboard/trend` | 七日安全趋势 |
| GET | `/api/dashboard/category-distribution` | 事件类别分布 |
| GET | `/api/dashboard/status-distribution` | 处置状态分布 |
| GET | `/api/dashboard/recent-alarms` | 最新安全事件 |
| GET | `/api/sites` | 站点列表 |
| GET | `/api/sites/{site_id}` | 站点详情 |
| GET | `/api/sites/{site_id}/devices` | 站点设备点位 |
| GET | `/api/sites/{site_id}/fences` | GIS 电子围栏 |
| GET | `/api/sites/{site_id}/alarms` | 地图告警 |
| GET | `/api/sites/{site_id}/map-overview` | 地图首屏聚合数据 |

首版前端没有强制登录，因此这些演示接口当前保持公开。正式部署时应接入用户鉴权和站点数据权限。

## 地图数据约定

高德地图占位接入使用：

```json
{
  "lng": 121.4739,
  "lat": 31.2306,
  "coordinateSystem": "gcj02"
}
```

`GET /api/sites/site-001/map-overview` 一次返回：

- `site`：站点信息；
- `center`、`zoom`：地图默认视野；
- `devices`：吊车、摄像头、雷达、音柱、NVR、边缘盒；
- `fences`：经纬度 Polygon 点；
- `alarms`：地图告警点；
- `weather`：吊装天气摘要。

## 测试

```powershell
python -m pytest -q
python -m compileall app
```

