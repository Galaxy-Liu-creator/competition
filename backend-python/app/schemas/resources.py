"""业务资源的 Pydantic 请求模型（snake_case）。

每个资源提供 Create（新增）与 Update（修改，全部可选）两个模型。
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


# --------------------------- 吊车 --------------------------- #
class CraneCreate(_Base):
    code: str
    name: str
    model: str = ""
    manufacturer: str = ""
    work_zone: str = ""
    status: str = "normal"
    install_date: str = ""
    linked_device_ids: list = []
    realtime: dict = {}


class CraneUpdate(_Base):
    code: str | None = None
    name: str | None = None
    model: str | None = None
    manufacturer: str | None = None
    work_zone: str | None = None
    status: str | None = None
    install_date: str | None = None
    linked_device_ids: list | None = None
    realtime: dict | None = None


# --------------------------- 摄像头 --------------------------- #
class CameraCreate(_Base):
    code: str
    name: str
    type: str = "perimeter"
    crane_id: int | None = None
    work_zone: str = ""
    ip: str = ""
    resolution: str = ""
    nvr_id: int | None = None
    rtsp_url: str = ""
    status: str = "online"


class CameraUpdate(_Base):
    code: str | None = None
    name: str | None = None
    type: str | None = None
    crane_id: int | None = None
    work_zone: str | None = None
    ip: str | None = None
    resolution: str | None = None
    nvr_id: int | None = None
    rtsp_url: str | None = None
    status: str | None = None


# --------------------------- 录像机 --------------------------- #
class NvrCreate(_Base):
    code: str
    name: str
    ip: str = ""
    channels_total: int = 16
    channels_used: int = 0
    storage_total_gb: int = 0
    storage_used_gb: int = 0
    retention_days: int = 30
    status: str = "online"


class NvrUpdate(_Base):
    code: str | None = None
    name: str | None = None
    ip: str | None = None
    channels_total: int | None = None
    channels_used: int | None = None
    storage_total_gb: int | None = None
    storage_used_gb: int | None = None
    retention_days: int | None = None
    status: str | None = None


# --------------------------- 音柱 --------------------------- #
class SpeakerCreate(_Base):
    code: str
    name: str
    work_zone: str = ""
    ip: str = ""
    volume: int = 70
    status: str = "online"


class SpeakerUpdate(_Base):
    code: str | None = None
    name: str | None = None
    work_zone: str | None = None
    ip: str | None = None
    volume: int | None = None
    status: str | None = None


class SpeakerLinkCreate(_Base):
    speaker_id: int
    target_type: str = "camera"
    target_id: int
    trigger_event: str = ""


# --------------------------- 边缘盒子 --------------------------- #
class EdgeBoxCreate(_Base):
    code: str
    name: str
    crane_id: int | None = None
    ip: str = ""
    version: str = ""
    cpu_percent: float = 0
    mem_percent: float = 0
    disk_percent: float = 0
    temperature: float = 0
    status: str = "online"


class EdgeBoxUpdate(_Base):
    code: str | None = None
    name: str | None = None
    crane_id: int | None = None
    ip: str | None = None
    version: str | None = None
    cpu_percent: float | None = None
    mem_percent: float | None = None
    disk_percent: float | None = None
    temperature: float | None = None
    status: str | None = None


# --------------------------- 雷达 --------------------------- #
class RadarCreate(_Base):
    code: str
    name: str
    crane_id: int | None = None
    work_zone: str = ""
    ip: str = ""
    range_m: float = 80
    angle_deg: float = 120
    status: str = "online"
    readings: list = []


class RadarUpdate(_Base):
    code: str | None = None
    name: str | None = None
    crane_id: int | None = None
    work_zone: str | None = None
    ip: str | None = None
    range_m: float | None = None
    angle_deg: float | None = None
    status: str | None = None
    readings: list | None = None


# --------------------------- 设备类型 --------------------------- #
class DeviceTypeCreate(_Base):
    code: str
    name: str
    category: str = ""
    icon: str = ""
    device_count: int = 0
    enabled: bool = True


class DeviceTypeUpdate(_Base):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    icon: str | None = None
    device_count: int | None = None
    enabled: bool | None = None


# --------------------------- 风险事件 --------------------------- #
class RiskEventCreate(_Base):
    event_no: str
    type: str = ""
    level: str = "general"
    status: str = "pending"
    work_zone: str = ""
    device_code: str = ""
    occurred_at: str = ""
    handler: str = ""
    handle_note: str = ""
    image_url: str = ""


class RiskEventUpdate(_Base):
    event_no: str | None = None
    type: str | None = None
    level: str | None = None
    status: str | None = None
    work_zone: str | None = None
    device_code: str | None = None
    occurred_at: str | None = None
    handler: str | None = None
    handle_note: str | None = None
    image_url: str | None = None


class RiskEventHandle(_Base):
    action: str
    handler: str = ""
    note: str = ""


# --------------------------- 违章大类 --------------------------- #
class ViolationCategoryCreate(_Base):
    code: str
    name: str
    level: str = "general"
    sub_count: int = 0
    enabled: bool = True
    description: str = ""
    sub_items: list = []


class ViolationCategoryUpdate(_Base):
    code: str | None = None
    name: str | None = None
    level: str | None = None
    sub_count: int | None = None
    enabled: bool | None = None
    description: str | None = None
    sub_items: list | None = None


# --------------------------- 设备关联 --------------------------- #
class DeviceLinkCreate(_Base):
    crane_id: int
    device_type: str = "camera"
    device_id: int


# --------------------------- 系统配置 --------------------------- #
class ConfigUpdate(_Base):
    value: dict[str, Any]
