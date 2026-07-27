"""业务模块 ORM 模型（snake_case）。

包含：吊车、摄像头、录像机、音柱、边缘盒子、雷达、心跳、设备关联、
设备类型、风险事件、违章大类、系统配置、审计日志，以及用于兼容旧
dashboard/sites 接口的地图数据表（以 JSON payload 原样存储）。
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )


# --------------------------------------------------------------------------- #
# 业务资源
# --------------------------------------------------------------------------- #
class Crane(Base, TimestampMixin):
    __tablename__ = "cranes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(64), default="")
    manufacturer: Mapped[str] = mapped_column(String(64), default="")
    work_zone: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(16), default="normal", index=True)
    install_date: Mapped[str] = mapped_column(String(32), default="")
    linked_device_ids: Mapped[list] = mapped_column(JSON, default=list)
    realtime: Mapped[dict] = mapped_column(JSON, default=dict)


class Camera(Base, TimestampMixin):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(16), default="perimeter")
    crane_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_zone: Mapped[str] = mapped_column(String(64), default="")
    ip: Mapped[str] = mapped_column(String(32), default="")
    resolution: Mapped[str] = mapped_column(String(32), default="")
    nvr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rtsp_url: Mapped[str] = mapped_column(String(256), default="")
    status: Mapped[str] = mapped_column(String(16), default="online", index=True)


class Nvr(Base, TimestampMixin):
    __tablename__ = "nvrs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    ip: Mapped[str] = mapped_column(String(32), default="")
    channels_total: Mapped[int] = mapped_column(Integer, default=16)
    channels_used: Mapped[int] = mapped_column(Integer, default=0)
    storage_total_gb: Mapped[int] = mapped_column(Integer, default=0)
    storage_used_gb: Mapped[int] = mapped_column(Integer, default=0)
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(16), default="online", index=True)


class Speaker(Base, TimestampMixin):
    __tablename__ = "speakers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    work_zone: Mapped[str] = mapped_column(String(64), default="")
    ip: Mapped[str] = mapped_column(String(32), default="")
    volume: Mapped[int] = mapped_column(Integer, default=70)
    status: Mapped[str] = mapped_column(String(16), default="online", index=True)


class SpeakerLink(Base, TimestampMixin):
    __tablename__ = "speaker_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    speaker_id: Mapped[int] = mapped_column(Integer, index=True)
    target_type: Mapped[str] = mapped_column(String(16), default="camera")
    target_id: Mapped[int] = mapped_column(Integer)
    trigger_event: Mapped[str] = mapped_column(String(64), default="")


class EdgeBox(Base, TimestampMixin):
    __tablename__ = "edge_boxes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    crane_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ip: Mapped[str] = mapped_column(String(32), default="")
    version: Mapped[str] = mapped_column(String(32), default="")
    cpu_percent: Mapped[float] = mapped_column(Float, default=0)
    mem_percent: Mapped[float] = mapped_column(Float, default=0)
    disk_percent: Mapped[float] = mapped_column(Float, default=0)
    temperature: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(16), default="online", index=True)


class Radar(Base, TimestampMixin):
    __tablename__ = "radars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    crane_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_zone: Mapped[str] = mapped_column(String(64), default="")
    ip: Mapped[str] = mapped_column(String(32), default="")
    range_m: Mapped[float] = mapped_column(Float, default=80)
    angle_deg: Mapped[float] = mapped_column(Float, default=120)
    status: Mapped[str] = mapped_column(String(16), default="online", index=True)
    readings: Mapped[list] = mapped_column(JSON, default=list)


class Heartbeat(Base, TimestampMixin):
    __tablename__ = "heartbeats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_code: Mapped[str] = mapped_column(String(32), index=True)
    device_type: Mapped[str] = mapped_column(String(16), default="")
    device_name: Mapped[str] = mapped_column(String(64), default="")
    interval_s: Mapped[int] = mapped_column(Integer, default=30)
    last_at: Mapped[str] = mapped_column(String(32), default="")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    miss_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="healthy", index=True)


class DeviceLink(Base, TimestampMixin):
    __tablename__ = "device_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crane_id: Mapped[int] = mapped_column(Integer, index=True)
    device_type: Mapped[str] = mapped_column(String(16), default="camera")
    device_id: Mapped[int] = mapped_column(Integer)


class DeviceType(Base, TimestampMixin):
    __tablename__ = "device_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(32), default="")
    icon: Mapped[str] = mapped_column(String(64), default="")
    device_count: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class RiskEvent(Base, TimestampMixin):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32), default="", index=True)
    level: Mapped[str] = mapped_column(String(16), default="general", index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    work_zone: Mapped[str] = mapped_column(String(64), default="")
    device_code: Mapped[str] = mapped_column(String(32), default="")
    occurred_at: Mapped[str] = mapped_column(String(32), default="")
    handler: Mapped[str] = mapped_column(String(32), default="")
    handle_note: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(256), default="")


class ViolationCategory(Base, TimestampMixin):
    __tablename__ = "violation_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    level: Mapped[str] = mapped_column(String(16), default="general")
    sub_count: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(Text, default="")
    sub_items: Mapped[list] = mapped_column(JSON, default=list)


class Config(Base, TimestampMixin):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON, default=dict)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(32), default="")
    role: Mapped[str] = mapped_column(String(32), default="系统管理员")
    email: Mapped[str] = mapped_column(String(64), default="")
    avatar_text: Mapped[str] = mapped_column(String(4), default="")
    avatar: Mapped[str] = mapped_column(Text, default="")  # 头像图片 DataURL，空串表示未上传
    last_login_at: Mapped[str] = mapped_column(String(32), default="")
    last_login_ip: Mapped[str] = mapped_column(String(32), default="")
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operator: Mapped[str] = mapped_column(String(32), default="")
    action: Mapped[str] = mapped_column(String(32), default="")
    module: Mapped[str] = mapped_column(String(32), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    ip: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[str] = mapped_column(String(32), default="")


# --------------------------------------------------------------------------- #
# 兼容旧 dashboard/sites 的地图数据（payload 原样存储 camelCase JSON）
# --------------------------------------------------------------------------- #
class LegacySite(Base):
    __tablename__ = "legacy_sites"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)


class LegacyDevice(Base):
    __tablename__ = "legacy_devices"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class LegacyFence(Base):
    __tablename__ = "legacy_fences"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class LegacyAlarm(Base):
    __tablename__ = "legacy_alarms"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    site_id: Mapped[str] = mapped_column(String(32), index=True)
    occurred_at: Mapped[str] = mapped_column(String(32), default="")
    payload: Mapped[dict] = mapped_column(JSON)


class LegacyWeather(Base):
    __tablename__ = "legacy_weather"

    site_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
