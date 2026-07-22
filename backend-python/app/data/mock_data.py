"""可复现的演示数据。

地图围栏与设备点位均为独立的 GCJ-02 经纬度数据。参考项目中基于
1280x720 视频帧的像素围栏不在此复用，也不能直接交给地图 SDK。
"""

from collections import Counter
from typing import Any

from app.schemas.models import (
    Alarm,
    DashboardOverview,
    DashboardStats,
    Device,
    DistributionItem,
    Fence,
    GeoPoint,
    MapOverview,
    Site,
    SiteSummary,
    Trend,
    Weather,
)


SITES: list[dict[str, Any]] = [
    {
        "id": "site-001",
        "name": "滨海能源基地 · 2#吊装作业区",
        "shortName": "滨海 2#作业区",
        "address": "上海市浦东新区滨海作业区",
        "center": {"lng": 121.4739, "lat": 31.2306, "coordinateSystem": "gcj02"},
        "coordinateSystem": "gcj02",
        "defaultZoom": 17,
        "enabled": True,
        "status": "warning",
        "statusLabel": "重点关注",
        "manager": "张工",
        "deviceCount": 8,
        "onlineDeviceCount": 7,
        "activeAlarmCount": 3,
    },
    {
        "id": "site-002",
        "name": "江南装备基地 · A区",
        "shortName": "江南 A区",
        "address": "杭州市滨江装备作业区",
        "center": {"lng": 120.1551, "lat": 30.2741, "coordinateSystem": "gcj02"},
        "coordinateSystem": "gcj02",
        "defaultZoom": 16,
        "enabled": True,
        "status": "normal",
        "statusLabel": "运行正常",
        "manager": "李工",
        "deviceCount": 4,
        "onlineDeviceCount": 4,
        "activeAlarmCount": 1,
    },
    {
        "id": "site-003",
        "name": "长江工程中心 · 西区",
        "shortName": "长江西区",
        "address": "南京市江北工程作业区",
        "center": {"lng": 118.7969, "lat": 32.0603, "coordinateSystem": "gcj02"},
        "coordinateSystem": "gcj02",
        "defaultZoom": 16,
        "enabled": True,
        "status": "normal",
        "statusLabel": "运行正常",
        "manager": "王工",
        "deviceCount": 3,
        "onlineDeviceCount": 2,
        "activeAlarmCount": 0,
    },
]


DEVICES: list[dict[str, Any]] = [
    {
        "id": "CRANE-001",
        "siteId": "site-001",
        "name": "1号履带吊",
        "type": "crane",
        "typeLabel": "履带式起重机",
        "status": "working",
        "statusLabel": "作业中",
        "riskLevel": "medium",
        "lng": 121.47420,
        "lat": 31.23082,
        "coordinateSystem": "gcj02",
        "heading": 126.4,
        "lastHeartbeat": "2026-07-19T15:42:21+08:00",
        "metadata": {"model": "XGC85", "ratedLoad": "85t", "operator": "赵师傅"},
    },
    {
        "id": "CRANE-002",
        "siteId": "site-001",
        "name": "2号汽车吊",
        "type": "crane",
        "typeLabel": "汽车起重机",
        "status": "alarm",
        "statusLabel": "告警",
        "riskLevel": "high",
        "lng": 121.47355,
        "lat": 31.23042,
        "coordinateSystem": "gcj02",
        "heading": 82.0,
        "lastHeartbeat": "2026-07-19T15:42:04+08:00",
        "metadata": {"model": "QY50K", "ratedLoad": "50t", "operator": "陈师傅"},
    },
    {
        "id": "CAM-008",
        "siteId": "site-001",
        "name": "东侧高清摄像头",
        "type": "camera",
        "typeLabel": "视频摄像头",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 121.47338,
        "lat": 31.23018,
        "coordinateSystem": "gcj02",
        "heading": 35.0,
        "lastHeartbeat": "2026-07-19T15:42:28+08:00",
        "metadata": {"channel": "CH08", "resolution": "4K"},
    },
    {
        "id": "CAM-012",
        "siteId": "site-001",
        "name": "西侧全景摄像头",
        "type": "camera",
        "typeLabel": "全景摄像头",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 121.47448,
        "lat": 31.23016,
        "coordinateSystem": "gcj02",
        "heading": 220.0,
        "lastHeartbeat": "2026-07-19T15:42:25+08:00",
        "metadata": {"channel": "CH12", "resolution": "4K"},
    },
    {
        "id": "RADAR-003",
        "siteId": "site-001",
        "name": "人员入侵雷达",
        "type": "radar",
        "typeLabel": "毫米波雷达",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 121.47443,
        "lat": 31.23094,
        "coordinateSystem": "gcj02",
        "heading": 180.0,
        "lastHeartbeat": "2026-07-19T15:42:27+08:00",
        "metadata": {"range": "80m"},
    },
    {
        "id": "SPK-005",
        "siteId": "site-001",
        "name": "现场广播音柱",
        "type": "speaker",
        "typeLabel": "智能音柱",
        "status": "standby",
        "statusLabel": "待机",
        "riskLevel": "low",
        "lng": 121.47324,
        "lat": 31.23088,
        "coordinateSystem": "gcj02",
        "heading": None,
        "lastHeartbeat": "2026-07-19T15:42:10+08:00",
        "metadata": {"volume": "72%"},
    },
    {
        "id": "NVR-001",
        "siteId": "site-001",
        "name": "现场录像主机",
        "type": "nvr",
        "typeLabel": "NVR录像机",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 121.47382,
        "lat": 31.23105,
        "coordinateSystem": "gcj02",
        "heading": None,
        "lastHeartbeat": "2026-07-19T15:42:30+08:00",
        "metadata": {"channels": 16, "storageUsage": "61%"},
    },
    {
        "id": "EDGE-018",
        "siteId": "site-001",
        "name": "AI边缘计算盒",
        "type": "edge_box",
        "typeLabel": "边缘计算盒",
        "status": "offline",
        "statusLabel": "离线",
        "riskLevel": "high",
        "lng": 121.47378,
        "lat": 31.22998,
        "coordinateSystem": "gcj02",
        "heading": None,
        "lastHeartbeat": "2026-07-19T15:31:02+08:00",
        "metadata": {"modelVersion": "V20260718", "temperature": "--"},
    },
    {
        "id": "CRANE-101",
        "siteId": "site-002",
        "name": "A区1号汽车吊",
        "type": "crane",
        "typeLabel": "汽车起重机",
        "status": "working",
        "statusLabel": "作业中",
        "riskLevel": "low",
        "lng": 120.15535,
        "lat": 30.27422,
        "coordinateSystem": "gcj02",
        "heading": 160.0,
        "lastHeartbeat": "2026-07-19T15:42:18+08:00",
        "metadata": {"model": "QY25K", "ratedLoad": "25t"},
    },
    {
        "id": "CAM-101",
        "siteId": "site-002",
        "name": "A区北侧摄像头",
        "type": "camera",
        "typeLabel": "视频摄像头",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 120.15486,
        "lat": 30.27435,
        "coordinateSystem": "gcj02",
        "heading": 145.0,
        "lastHeartbeat": "2026-07-19T15:42:26+08:00",
        "metadata": {"channel": "CH01"},
    },
    {
        "id": "RADAR-101",
        "siteId": "site-002",
        "name": "A区安全雷达",
        "type": "radar",
        "typeLabel": "毫米波雷达",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 120.15502,
        "lat": 30.27388,
        "coordinateSystem": "gcj02",
        "heading": 20.0,
        "lastHeartbeat": "2026-07-19T15:42:20+08:00",
        "metadata": {"range": "60m"},
    },
    {
        "id": "EDGE-101",
        "siteId": "site-002",
        "name": "A区边缘计算盒",
        "type": "edge_box",
        "typeLabel": "边缘计算盒",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 120.15518,
        "lat": 30.27452,
        "coordinateSystem": "gcj02",
        "heading": None,
        "lastHeartbeat": "2026-07-19T15:42:29+08:00",
        "metadata": {"modelVersion": "V20260718"},
    },
    {
        "id": "CRANE-201",
        "siteId": "site-003",
        "name": "西区1号履带吊",
        "type": "crane",
        "typeLabel": "履带式起重机",
        "status": "standby",
        "statusLabel": "待机",
        "riskLevel": "low",
        "lng": 118.79710,
        "lat": 32.06052,
        "coordinateSystem": "gcj02",
        "heading": 270.0,
        "lastHeartbeat": "2026-07-19T15:42:12+08:00",
        "metadata": {"model": "XGC55", "ratedLoad": "55t"},
    },
    {
        "id": "CAM-201",
        "siteId": "site-003",
        "name": "西区固定摄像头",
        "type": "camera",
        "typeLabel": "视频摄像头",
        "status": "online",
        "statusLabel": "在线",
        "riskLevel": "low",
        "lng": 118.79663,
        "lat": 32.06010,
        "coordinateSystem": "gcj02",
        "heading": 45.0,
        "lastHeartbeat": "2026-07-19T15:42:22+08:00",
        "metadata": {"channel": "CH01"},
    },
    {
        "id": "SPK-201",
        "siteId": "site-003",
        "name": "西区广播音柱",
        "type": "speaker",
        "typeLabel": "智能音柱",
        "status": "offline",
        "statusLabel": "离线",
        "riskLevel": "medium",
        "lng": 118.79672,
        "lat": 32.06062,
        "coordinateSystem": "gcj02",
        "heading": None,
        "lastHeartbeat": "2026-07-19T14:58:40+08:00",
        "metadata": {"volume": "--"},
    },
]


# 独立 GIS 围栏：points 是经纬度，不是视频像素点。
FENCES: list[dict[str, Any]] = [
    {
        "id": "FENCE-001",
        "siteId": "site-001",
        "name": "2#吊装核心作业区",
        "type": "polygon",
        "typeLabel": "区域围栏",
        "riskLevel": "high",
        "color": "#00d7ff",
        "enabled": True,
        "coordinateSystem": "gcj02",
        "points": [
            {"lng": 121.47328, "lat": 31.23005, "coordinateSystem": "gcj02"},
            {"lng": 121.47455, "lat": 31.23006, "coordinateSystem": "gcj02"},
            {"lng": 121.47458, "lat": 31.23096, "coordinateSystem": "gcj02"},
            {"lng": 121.47330, "lat": 31.23098, "coordinateSystem": "gcj02"},
        ],
        "ruleIds": ["RULE-PERSON-UNDER-LOAD", "RULE-CROSS-FENCE"],
        "deviceIds": ["CAM-008", "CAM-012", "RADAR-003", "SPK-005"],
    },
    {
        "id": "FENCE-002",
        "siteId": "site-001",
        "name": "吊臂回转高风险区",
        "type": "polygon",
        "typeLabel": "区域围栏",
        "riskLevel": "critical",
        "color": "#ff5b5b",
        "enabled": True,
        "coordinateSystem": "gcj02",
        "points": [
            {"lng": 121.47388, "lat": 31.23042, "coordinateSystem": "gcj02"},
            {"lng": 121.47434, "lat": 31.23048, "coordinateSystem": "gcj02"},
            {"lng": 121.47425, "lat": 31.23086, "coordinateSystem": "gcj02"},
            {"lng": 121.47382, "lat": 31.23079, "coordinateSystem": "gcj02"},
        ],
        "ruleIds": ["RULE-ROTATION-RADIUS"],
        "deviceIds": ["CRANE-001", "CAM-012", "RADAR-003"],
    },
    {
        "id": "FENCE-101",
        "siteId": "site-002",
        "name": "A区临时管控区",
        "type": "polygon",
        "typeLabel": "区域围栏",
        "riskLevel": "medium",
        "color": "#b58cff",
        "enabled": True,
        "coordinateSystem": "gcj02",
        "points": [
            {"lng": 120.15475, "lat": 30.27382, "coordinateSystem": "gcj02"},
            {"lng": 120.15548, "lat": 30.27385, "coordinateSystem": "gcj02"},
            {"lng": 120.15552, "lat": 30.27455, "coordinateSystem": "gcj02"},
            {"lng": 120.15480, "lat": 30.27458, "coordinateSystem": "gcj02"},
        ],
        "ruleIds": ["RULE-CROSS-FENCE"],
        "deviceIds": ["CAM-101", "RADAR-101"],
    },
    {
        "id": "FENCE-201",
        "siteId": "site-003",
        "name": "西区吊装作业边界",
        "type": "polygon",
        "typeLabel": "区域围栏",
        "riskLevel": "medium",
        "color": "#ffd166",
        "enabled": True,
        "coordinateSystem": "gcj02",
        "points": [
            {"lng": 118.79640, "lat": 32.05992, "coordinateSystem": "gcj02"},
            {"lng": 118.79728, "lat": 32.05995, "coordinateSystem": "gcj02"},
            {"lng": 118.79731, "lat": 32.06072, "coordinateSystem": "gcj02"},
            {"lng": 118.79643, "lat": 32.06075, "coordinateSystem": "gcj02"},
        ],
        "ruleIds": ["RULE-CROSS-FENCE"],
        "deviceIds": ["CAM-201", "SPK-201"],
    },
]


ALARMS: list[dict[str, Any]] = [
    {
        "id": "EV202607190036",
        "siteId": "site-001",
        "deviceId": "CAM-012",
        "fenceId": "FENCE-002",
        "type": "person_in_rotation_radius",
        "typeLabel": "人员进入回转半径",
        "title": "人员进入吊臂回转高风险区",
        "description": "西侧全景摄像头识别到人员进入起重机回转范围。",
        "level": "critical",
        "levelLabel": "紧急",
        "status": "pending",
        "statusLabel": "待处置",
        "lng": 121.47408,
        "lat": 31.23066,
        "coordinateSystem": "gcj02",
        "occurredAt": "2026-07-19T15:32:18+08:00",
        "evidence": {"imageUrl": None, "videoUrl": None},
    },
    {
        "id": "EV202607190035",
        "siteId": "site-001",
        "deviceId": "CRANE-002",
        "fenceId": "FENCE-001",
        "type": "overload_risk",
        "typeLabel": "载荷风险",
        "title": "2号汽车吊载荷接近阈值",
        "description": "当前载荷达到额定载荷的 92%，建议降低作业幅度。",
        "level": "high",
        "levelLabel": "高风险",
        "status": "processing",
        "statusLabel": "处置中",
        "lng": 121.47355,
        "lat": 31.23042,
        "coordinateSystem": "gcj02",
        "occurredAt": "2026-07-19T15:26:45+08:00",
        "evidence": {"imageUrl": None, "videoUrl": None},
    },
    {
        "id": "EV202607190034",
        "siteId": "site-001",
        "deviceId": "EDGE-018",
        "fenceId": None,
        "type": "device_offline",
        "typeLabel": "设备离线",
        "title": "AI边缘计算盒离线",
        "description": "EDGE-018 已超过 10 分钟未上报心跳。",
        "level": "high",
        "levelLabel": "高风险",
        "status": "pending",
        "statusLabel": "待处置",
        "lng": 121.47378,
        "lat": 31.22998,
        "coordinateSystem": "gcj02",
        "occurredAt": "2026-07-19T15:21:02+08:00",
        "evidence": {"imageUrl": None, "videoUrl": None},
    },
    {
        "id": "EV202607190031",
        "siteId": "site-002",
        "deviceId": "CAM-101",
        "fenceId": "FENCE-101",
        "type": "cross_fence",
        "typeLabel": "人员越界",
        "title": "人员进入临时管控区",
        "description": "北侧摄像头检测到未授权人员短时进入围栏。",
        "level": "medium",
        "levelLabel": "中风险",
        "status": "processing",
        "statusLabel": "处置中",
        "lng": 120.15508,
        "lat": 30.27412,
        "coordinateSystem": "gcj02",
        "occurredAt": "2026-07-19T14:58:36+08:00",
        "evidence": {"imageUrl": None, "videoUrl": None},
    },
    {
        "id": "EV202607190020",
        "siteId": "site-003",
        "deviceId": "CAM-201",
        "fenceId": "FENCE-201",
        "type": "no_helmet",
        "typeLabel": "未佩戴安全帽",
        "title": "作业人员防护装备不规范",
        "description": "告警已由现场安全员复核并闭环。",
        "level": "medium",
        "levelLabel": "中风险",
        "status": "closed",
        "statusLabel": "已闭环",
        "lng": 118.79692,
        "lat": 32.06034,
        "coordinateSystem": "gcj02",
        "occurredAt": "2026-07-19T13:42:10+08:00",
        "evidence": {"imageUrl": None, "videoUrl": None},
    },
]


WEATHER: dict[str, dict[str, Any]] = {
    "site-001": {
        "temperature": 31.2,
        "humidity": 68,
        "windSpeed": 5.2,
        "windDirection": "东南风",
        "condition": "多云",
        "safeForLifting": True,
        "updatedAt": "2026-07-19T15:40:00+08:00",
    },
    "site-002": {
        "temperature": 30.5,
        "humidity": 72,
        "windSpeed": 4.6,
        "windDirection": "东风",
        "condition": "多云",
        "safeForLifting": True,
        "updatedAt": "2026-07-19T15:40:00+08:00",
    },
    "site-003": {
        "temperature": 32.0,
        "humidity": 64,
        "windSpeed": 6.8,
        "windDirection": "西南风",
        "condition": "晴",
        "safeForLifting": True,
        "updatedAt": "2026-07-19T15:40:00+08:00",
    },
}


def _dump(model):
    return model.model_dump(mode="json")


def list_sites() -> list[dict[str, Any]]:
    return [_dump(Site.model_validate(item)) for item in SITES]


def find_site(site_id: str) -> dict[str, Any] | None:
    item = next((site for site in SITES if site["id"] == site_id), None)
    return _dump(Site.model_validate(item)) if item else None


def list_devices(site_id: str) -> list[dict[str, Any]]:
    return [
        _dump(Device.model_validate(item))
        for item in DEVICES
        if item["siteId"] == site_id
    ]


def list_fences(site_id: str) -> list[dict[str, Any]]:
    return [
        _dump(Fence.model_validate(item))
        for item in FENCES
        if item["siteId"] == site_id
    ]


def list_alarms(site_id: str | None = None) -> list[dict[str, Any]]:
    items = ALARMS if site_id is None else [a for a in ALARMS if a["siteId"] == site_id]
    return [_dump(Alarm.model_validate(item)) for item in items]


def map_overview(site_id: str) -> dict[str, Any] | None:
    site = find_site(site_id)
    if not site:
        return None
    payload = MapOverview(
        siteId=site_id,
        coordinateSystem="gcj02",
        center=GeoPoint.model_validate(site["center"]),
        zoom=site["defaultZoom"],
        site=Site.model_validate(site),
        devices=[Device.model_validate(item) for item in list_devices(site_id)],
        fences=[Fence.model_validate(item) for item in list_fences(site_id)],
        alarms=[Alarm.model_validate(item) for item in list_alarms(site_id)],
        weather=Weather.model_validate(WEATHER[site_id]),
    )
    return _dump(payload)


def dashboard_stats() -> dict[str, Any]:
    active_alarms = [item for item in ALARMS if item["status"] != "closed"]
    stats = DashboardStats(
        activeSites=sum(1 for item in SITES if item["enabled"]),
        totalDevices=len(DEVICES),
        onlineDevices=sum(1 for item in DEVICES if item["status"] != "offline"),
        activeAlarms=len(active_alarms),
        criticalAlarms=sum(1 for item in active_alarms if item["level"] == "critical"),
        todayAlerts=len(ALARMS),
        closedLoopRate=0.94,
        safeDays=128,
    )
    return _dump(stats)


def dashboard_trend() -> dict[str, Any]:
    return _dump(
        Trend(
            dates=["07-13", "07-14", "07-15", "07-16", "07-17", "07-18", "07-19"],
            series=[
                {"name": "安全事件", "data": [18, 14, 21, 17, 12, 16, 11]},
                {"name": "已闭环", "data": [16, 13, 18, 16, 11, 15, 9]},
            ],
        )
    )


def risk_distribution() -> list[dict[str, Any]]:
    colors = {
        "critical": "#ff4d5f",
        "high": "#ff8a3d",
        "medium": "#ffd166",
        "low": "#45d6a8",
    }
    labels = {"critical": "紧急", "high": "高风险", "medium": "中风险", "low": "低风险"}
    counts = Counter(item["level"] for item in ALARMS)
    return [
        _dump(DistributionItem(name=labels[level], value=counts[level], color=colors[level]))
        for level in ("critical", "high", "medium", "low")
    ]


def device_status_distribution() -> list[dict[str, Any]]:
    groups = {
        "在线/作业": sum(1 for item in DEVICES if item["status"] in {"online", "working"}),
        "待机": sum(1 for item in DEVICES if item["status"] == "standby"),
        "告警": sum(1 for item in DEVICES if item["status"] == "alarm"),
        "离线": sum(1 for item in DEVICES if item["status"] == "offline"),
    }
    colors = {"在线/作业": "#00d7ff", "待机": "#ffd166", "告警": "#ff5b5b", "离线": "#718096"}
    return [
        _dump(DistributionItem(name=name, value=value, color=colors[name]))
        for name, value in groups.items()
    ]


def category_distribution() -> list[dict[str, Any]]:
    counts = Counter(item["typeLabel"] for item in ALARMS)
    return [
        _dump(DistributionItem(name=name, value=value))
        for name, value in counts.most_common()
    ]


def alarm_status_distribution() -> list[dict[str, Any]]:
    labels = {"pending": "待处置", "processing": "处置中", "closed": "已闭环"}
    counts = Counter(item["status"] for item in ALARMS)
    return [
        _dump(DistributionItem(name=labels[status], value=counts[status]))
        for status in ("pending", "processing", "closed")
    ]


def site_summary() -> dict[str, Any]:
    summary = SiteSummary(
        totalSites=len(SITES),
        normalSites=sum(1 for item in SITES if item["status"] == "normal"),
        warningSites=sum(1 for item in SITES if item["status"] == "warning"),
        totalDevices=len(DEVICES),
        onlineDevices=sum(1 for item in DEVICES if item["status"] != "offline"),
    )
    return _dump(summary)


def dashboard_overview() -> dict[str, Any]:
    payload = DashboardOverview(
        stats=dashboard_stats(),
        trend=dashboard_trend(),
        riskDistribution=risk_distribution(),
        deviceStatus=device_status_distribution(),
        recentAlarms=list_alarms()[:8],
        siteSummary=site_summary(),
    )
    return _dump(payload)

