"""兼容旧 dashboard/sites 接口的 DB 聚合服务。

地图数据以 camelCase JSON payload 原样存储在 legacy_* 表中，此处读取后
经 Pydantic 模型校验并 dump，输出与原 mock_data 完全一致的契约。
"""

from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models as m
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


def _dump(model) -> dict[str, Any]:
    return model.model_dump(mode="json")


def _site_payloads(db: Session) -> list[dict]:
    rows = db.scalars(select(m.LegacySite)).all()
    return [r.payload for r in rows]


def _device_payloads(db: Session, site_id: str | None = None) -> list[dict]:
    stmt = select(m.LegacyDevice)
    if site_id is not None:
        stmt = stmt.where(m.LegacyDevice.site_id == site_id)
    return [r.payload for r in db.scalars(stmt).all()]


def _fence_payloads(db: Session, site_id: str | None = None) -> list[dict]:
    stmt = select(m.LegacyFence)
    if site_id is not None:
        stmt = stmt.where(m.LegacyFence.site_id == site_id)
    return [r.payload for r in db.scalars(stmt).all()]


def _alarm_payloads(db: Session, site_id: str | None = None) -> list[dict]:
    stmt = select(m.LegacyAlarm).order_by(m.LegacyAlarm.occurred_at.desc())
    if site_id is not None:
        stmt = stmt.where(m.LegacyAlarm.site_id == site_id)
    return [r.payload for r in db.scalars(stmt).all()]


def list_sites(db: Session) -> list[dict]:
    return [_dump(Site.model_validate(p)) for p in _site_payloads(db)]


def find_site(db: Session, site_id: str) -> dict | None:
    row = db.get(m.LegacySite, site_id)
    return _dump(Site.model_validate(row.payload)) if row else None


def list_devices(db: Session, site_id: str) -> list[dict]:
    return [_dump(Device.model_validate(p)) for p in _device_payloads(db, site_id)]


def list_fences(db: Session, site_id: str) -> list[dict]:
    return [_dump(Fence.model_validate(p)) for p in _fence_payloads(db, site_id)]


def list_alarms(db: Session, site_id: str | None = None) -> list[dict]:
    return [_dump(Alarm.model_validate(p)) for p in _alarm_payloads(db, site_id)]


def map_overview(db: Session, site_id: str) -> dict | None:
    site = find_site(db, site_id)
    if not site:
        return None
    weather_row = db.get(m.LegacyWeather, site_id)
    payload = MapOverview(
        siteId=site_id,
        coordinateSystem="gcj02",
        center=GeoPoint.model_validate(site["center"]),
        zoom=site["defaultZoom"],
        site=Site.model_validate(site),
        devices=[Device.model_validate(item) for item in list_devices(db, site_id)],
        fences=[Fence.model_validate(item) for item in list_fences(db, site_id)],
        alarms=[Alarm.model_validate(item) for item in list_alarms(db, site_id)],
        weather=Weather.model_validate(weather_row.payload),
    )
    return _dump(payload)


# --------------------------- Dashboard 聚合 --------------------------- #
def dashboard_stats(db: Session) -> dict:
    sites = _site_payloads(db)
    devices = _device_payloads(db)
    alarms = _alarm_payloads(db)
    active = [a for a in alarms if a["status"] != "closed"]
    return _dump(DashboardStats(
        activeSites=sum(1 for s in sites if s["enabled"]),
        totalDevices=len(devices),
        onlineDevices=sum(1 for d in devices if d["status"] != "offline"),
        activeAlarms=len(active),
        criticalAlarms=sum(1 for a in active if a["level"] == "critical"),
        todayAlerts=len(alarms),
        closedLoopRate=0.94,
        safeDays=128,
    ))


def dashboard_trend(_db: Session | None = None) -> dict:
    return _dump(Trend(
        dates=["07-13", "07-14", "07-15", "07-16", "07-17", "07-18", "07-19"],
        series=[
            {"name": "安全事件", "data": [18, 14, 21, 17, 12, 16, 11]},
            {"name": "已闭环", "data": [16, 13, 18, 16, 11, 15, 9]},
        ],
    ))


def risk_distribution(db: Session) -> list[dict]:
    colors = {"critical": "#ff4d5f", "high": "#ff8a3d", "medium": "#ffd166", "low": "#45d6a8"}
    labels = {"critical": "紧急", "high": "高风险", "medium": "中风险", "low": "低风险"}
    counts = Counter(a["level"] for a in _alarm_payloads(db))
    return [
        _dump(DistributionItem(name=labels[lv], value=counts[lv], color=colors[lv]))
        for lv in ("critical", "high", "medium", "low")
    ]


def device_status_distribution(db: Session) -> list[dict]:
    devices = _device_payloads(db)
    groups = {
        "在线/作业": sum(1 for d in devices if d["status"] in {"online", "working"}),
        "待机": sum(1 for d in devices if d["status"] == "standby"),
        "告警": sum(1 for d in devices if d["status"] == "alarm"),
        "离线": sum(1 for d in devices if d["status"] == "offline"),
    }
    colors = {"在线/作业": "#00d7ff", "待机": "#ffd166", "告警": "#ff5b5b", "离线": "#718096"}
    return [_dump(DistributionItem(name=n, value=v, color=colors[n])) for n, v in groups.items()]


def category_distribution(db: Session) -> list[dict]:
    counts = Counter(a["typeLabel"] for a in _alarm_payloads(db))
    return [_dump(DistributionItem(name=n, value=v)) for n, v in counts.most_common()]


def alarm_status_distribution(db: Session) -> list[dict]:
    labels = {"pending": "待处置", "processing": "处置中", "closed": "已闭环"}
    counts = Counter(a["status"] for a in _alarm_payloads(db))
    return [_dump(DistributionItem(name=labels[st], value=counts[st])) for st in ("pending", "processing", "closed")]


def site_summary(db: Session) -> dict:
    sites = _site_payloads(db)
    devices = _device_payloads(db)
    return _dump(SiteSummary(
        totalSites=len(sites),
        normalSites=sum(1 for s in sites if s["status"] == "normal"),
        warningSites=sum(1 for s in sites if s["status"] == "warning"),
        totalDevices=len(devices),
        onlineDevices=sum(1 for d in devices if d["status"] != "offline"),
    ))


def dashboard_overview(db: Session) -> dict:
    return _dump(DashboardOverview(
        stats=dashboard_stats(db),
        trend=dashboard_trend(db),
        riskDistribution=risk_distribution(db),
        deviceStatus=device_status_distribution(db),
        recentAlarms=list_alarms(db)[:8],
        siteSummary=site_summary(db),
    ))
