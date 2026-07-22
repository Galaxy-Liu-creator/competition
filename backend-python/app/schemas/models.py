"""站点、地图资源和看板响应模型。"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CoordinateSystem = Literal["gcj02"]
DeviceType = Literal["crane", "camera", "radar", "speaker", "nvr", "edge_box"]
RiskLevel = Literal["critical", "high", "medium", "low"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GeoPoint(StrictModel):
    lng: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    coordinateSystem: CoordinateSystem = "gcj02"


class Site(StrictModel):
    id: str
    name: str
    shortName: str
    address: str
    center: GeoPoint
    coordinateSystem: CoordinateSystem = "gcj02"
    defaultZoom: int = Field(16, ge=3, le=20)
    enabled: bool = True
    status: Literal["normal", "warning", "offline"]
    statusLabel: str
    manager: str
    deviceCount: int = Field(..., ge=0)
    onlineDeviceCount: int = Field(..., ge=0)
    activeAlarmCount: int = Field(..., ge=0)


class Device(StrictModel):
    id: str
    siteId: str
    name: str
    type: DeviceType
    typeLabel: str
    status: Literal["working", "online", "standby", "offline", "alarm"]
    statusLabel: str
    riskLevel: RiskLevel
    lng: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    coordinateSystem: CoordinateSystem = "gcj02"
    heading: float | None = Field(None, ge=0, lt=360)
    lastHeartbeat: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Fence(StrictModel):
    id: str
    siteId: str
    name: str
    type: Literal["polygon"] = "polygon"
    typeLabel: str = "区域围栏"
    riskLevel: RiskLevel
    color: str
    enabled: bool = True
    coordinateSystem: CoordinateSystem = "gcj02"
    points: list[GeoPoint] = Field(..., min_length=3)
    ruleIds: list[str] = Field(default_factory=list)
    deviceIds: list[str] = Field(default_factory=list)


class AlarmEvidence(StrictModel):
    imageUrl: str | None = None
    videoUrl: str | None = None


class Alarm(StrictModel):
    id: str
    siteId: str
    deviceId: str | None = None
    fenceId: str | None = None
    type: str
    typeLabel: str
    title: str
    description: str
    level: RiskLevel
    levelLabel: str
    status: Literal["pending", "processing", "closed"]
    statusLabel: str
    lng: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)
    coordinateSystem: CoordinateSystem = "gcj02"
    occurredAt: str
    evidence: AlarmEvidence


class Weather(StrictModel):
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    windSpeed: float = Field(..., ge=0)
    windDirection: str
    condition: str
    safeForLifting: bool
    updatedAt: str


class MapOverview(StrictModel):
    siteId: str
    coordinateSystem: CoordinateSystem = "gcj02"
    center: GeoPoint
    zoom: int = Field(..., ge=3, le=20)
    site: Site
    devices: list[Device]
    fences: list[Fence]
    alarms: list[Alarm]
    weather: Weather


class DashboardStats(StrictModel):
    activeSites: int = Field(..., ge=0)
    totalDevices: int = Field(..., ge=0)
    onlineDevices: int = Field(..., ge=0)
    activeAlarms: int = Field(..., ge=0)
    criticalAlarms: int = Field(..., ge=0)
    todayAlerts: int = Field(..., ge=0)
    closedLoopRate: float = Field(..., ge=0, le=1)
    safeDays: int = Field(..., ge=0)


class TrendSeries(StrictModel):
    name: str
    data: list[int]


class Trend(StrictModel):
    dates: list[str]
    series: list[TrendSeries]


class DistributionItem(StrictModel):
    name: str
    value: int = Field(..., ge=0)
    color: str | None = None


class SiteSummary(StrictModel):
    totalSites: int = Field(..., ge=0)
    normalSites: int = Field(..., ge=0)
    warningSites: int = Field(..., ge=0)
    totalDevices: int = Field(..., ge=0)
    onlineDevices: int = Field(..., ge=0)


class DashboardOverview(StrictModel):
    stats: DashboardStats
    trend: Trend
    riskDistribution: list[DistributionItem]
    deviceStatus: list[DistributionItem]
    recentAlarms: list[Alarm]
    siteSummary: SiteSummary

