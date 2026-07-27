"""Licensed demo media with explicit event-to-evidence semantics.

The image files live in ``frontend-vue/public/dataset``.  This module keeps the
runtime mapping deterministic while ``manifest.json`` remains the source of
truth for author, license, dimensions, and SHA-256 metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


EVIDENCE_MODES = frozenset({"direct-visual", "overlay-assisted", "sensor-context"})


@dataclass(frozen=True, slots=True)
class EvidenceMedia:
    """A stable media path plus the way a demo event is actually established."""

    media_id: str
    path: str
    evidence_mode: str
    evidence_label: str
    source_node: str
    note: str

    def __post_init__(self) -> None:
        if self.evidence_mode not in EVIDENCE_MODES:
            raise ValueError(f"unsupported evidence mode: {self.evidence_mode}")


CONSTRUCTION_IMAGES: tuple[str, ...] = (
    "/dataset/construction/tower-crane-aerial-01.jpg",
    "/dataset/construction/tower-crane-aerial-02.jpg",
    "/dataset/construction/mobile-crane-e16.jpg",
    "/dataset/construction/mobile-crane-precast-wall.jpg",
    "/dataset/construction/liebherr-ltm1500-genie.jpg",
    "/dataset/construction/site-yard-tower-cranes.jpg",
)

PPE_IMAGES: tuple[str, ...] = (
    "/dataset/ppe/rebar-deck-crew.jpg",
    "/dataset/ppe/ppe-helmet-0014.jpg",
    "/dataset/ppe/ppe-site-0517.jpg",
    "/dataset/ppe/ppe-site-0637.jpg",
    "/dataset/ppe/ppe-site-0675.jpg",
    "/dataset/ppe/ppe-site-0701.jpg",
    "/dataset/ppe/ppe-site-0803.jpg",
)

VIOLATION_IMAGES: tuple[str, ...] = (
    "/dataset/violations/worker-without-ppe.jpg",
    "/dataset/violations/unsafe-crane-parking.jpg",
)

LIFTING_IMAGES: tuple[str, ...] = (
    "/dataset/lifting/drywall-crane-worksite.jpg",
    "/dataset/lifting/heavy-load-lift.jpg",
    "/dataset/lifting/trench-box-guidance.jpg",
    "/dataset/lifting/improper-eyebolt.jpg",
    "/dataset/lifting/crane-hook-guidance.jpg",
    "/dataset/lifting/crane-lifting-ashlars.jpg",
    "/dataset/lifting/girder-heavy-lift.jpg",
    "/dataset/lifting/angled-girder-rigging.jpg",
    "/dataset/lifting/girder-landing-zone.jpg",
)

EQUIPMENT_IMAGES: tuple[str, ...] = (
    "/dataset/equipment/tower-crane-anemometer.jpg",
)

ACCESS_CONTROL_IMAGES: tuple[str, ...] = (
    "/dataset/access-control/construction-site-entrance.jpg",
    "/dataset/access-control/restricted-construction-fence.jpg",
    "/dataset/access-control/site-gate-pedestrians.jpg",
    "/dataset/access-control/site-fence-warning-sign.jpg",
)

DATASET_PATHS: tuple[str, ...] = (
    CONSTRUCTION_IMAGES
    + PPE_IMAGES
    + VIOLATION_IMAGES
    + LIFTING_IMAGES
    + EQUIPMENT_IMAGES
    + ACCESS_CONTROL_IMAGES
)


def _evidence(
    media_id: str,
    path: str,
    evidence_mode: str,
    evidence_label: str,
    source_node: str,
    note: str,
) -> EvidenceMedia:
    return EvidenceMedia(
        media_id=media_id,
        path=path,
        evidence_mode=evidence_mode,
        evidence_label=evidence_label,
        source_node=source_node,
        note=note,
    )


RISK_EVIDENCE_BY_TYPE: Mapping[str, EvidenceMedia] = MappingProxyType({
    "违规闯入": _evidence(
        "site-gate-pedestrians",
        "/dataset/access-control/site-gate-pedestrians.jpg",
        "overlay-assisted",
        "电子围栏联动",
        "FENCE_AI_NODE_02",
        "工地围挡与闸口处有人员靠近逗留，围挡、闸口和人员在画面中可见；越界关系由演示电子围栏叠加确定。",
    ),
    "超载起吊": _evidence(
        "girder-heavy-lift",
        "/dataset/lifting/girder-heavy-lift.jpg",
        "sensor-context",
        "载荷传感器联动",
        "LOAD_SENSOR_CR-02",
        "履带吊正在起吊大型预制梁，重载吊装场景可见；是否超过额定载荷由确定性演示载荷遥测判定。",
    ),
    "未佩戴安全帽": _evidence(
        "worker-without-ppe",
        "/dataset/violations/worker-without-ppe.jpg",
        "direct-visual",
        "视觉识别证据",
        "PPE_VISION_NODE_01",
        "高处作业人员未佩戴安全帽且缺少个人防护装备，关键事实可直接观察。",
    ),
    "违章操作": _evidence(
        "unsafe-crane-parking",
        "/dataset/violations/unsafe-crane-parking.jpg",
        "direct-visual",
        "现场巡检证据",
        "SAFETY_AUDIT_NODE_01",
        "NIOSH 图片直接展示重型设备处于危险垫高和停放状态。",
    ),
    "斜拉斜吊": _evidence(
        "angled-girder-rigging",
        "/dataset/lifting/angled-girder-rigging.jpg",
        "sensor-context",
        "吊钩姿态传感器联动",
        "HOOK_POSE_SENSOR_02",
        "吊钩与索具带载呈明显倾斜姿态，梁体斜置于画面中；斜拉角度由吊钩姿态与摆角遥测判定。",
    ),
    "设备离线": _evidence(
        "construction-site-entrance",
        "/dataset/access-control/construction-site-entrance.jpg",
        "sensor-context",
        "设备心跳联动",
        "HEARTBEAT_GATEWAY_01",
        "入口摄像头和工地环境可见；离线结论来自设备心跳而不是静态照片。",
    ),
    "大风超阈值起吊": _evidence(
        "tower-crane-anemometer",
        "/dataset/equipment/tower-crane-anemometer.jpg",
        "sensor-context",
        "风速传感器联动",
        "ANEMOMETER_TC-04",
        "塔吊驾驶室和杯式风速仪可见；风速是否超阈值由演示传感器读数判定。",
    ),
    "吊物下方站人": _evidence(
        "girder-landing-zone",
        "/dataset/lifting/girder-landing-zone.jpg",
        "overlay-assisted",
        "吊装危险区联动",
        "LIFTING_ZONE_VISION_01",
        "预制梁悬吊于落梁区上方，多名作业人员位于吊物邻近区域；进入关系由演示危险区叠加确定。",
    ),
    "未系安全带": _evidence(
        "ppe-site-0701",
        "/dataset/ppe/ppe-site-0701.jpg",
        "direct-visual",
        "视觉识别证据",
        "PPE_VISION_NODE_02",
        "高处作业人员未使用适当防坠设备，关键事实可直接观察。",
    ),
    "限位失效": _evidence(
        "tower-crane-anemometer",
        "/dataset/equipment/tower-crane-anemometer.jpg",
        "sensor-context",
        "限位传感器联动",
        "LIMIT_SWITCH_TC-04",
        "照片提供塔吊控制设备场景；限位开关状态只能由传感器和控制器诊断确定。",
    ),
})


ALARM_EVIDENCE_BY_TYPE: Mapping[str, EvidenceMedia] = MappingProxyType({
    "person_in_rotation_radius": _evidence(
        "crane-lifting-ashlars",
        "/dataset/lifting/crane-lifting-ashlars.jpg",
        "overlay-assisted",
        "回转半径雷视联动",
        "RADAR_VISION_FUSION_03",
        "人员、吊钩和吊装作业面可见；是否进入回转半径由雷达与演示区域叠加确定。",
    ),
    "overload_risk": RISK_EVIDENCE_BY_TYPE["超载起吊"],
    "device_offline": RISK_EVIDENCE_BY_TYPE["设备离线"],
    "cross_fence": RISK_EVIDENCE_BY_TYPE["违规闯入"],
    "no_helmet": RISK_EVIDENCE_BY_TYPE["未佩戴安全帽"],
})


DEFAULT_EVIDENCE = _evidence(
    "tower-crane-aerial-01",
    "/dataset/construction/tower-crane-aerial-01.jpg",
    "sensor-context",
    "场景参考",
    "DEMO_CONTEXT_NODE",
    "该图片只提供施工现场上下文，具体事件结论以演示业务数据为准。",
)

_RISK_TYPE_ALIASES = {
    "人员违规闯入": "违规闯入",
    "安全帽未佩戴": "未佩戴安全帽",
    "违规超载告警": "超载起吊",
    "周界越界": "违规闯入",
}


def evidence_for_risk_event(event_type: str) -> EvidenceMedia:
    """Return explicit evidence metadata for a risk-event type."""
    normalized = (event_type or "").strip()
    normalized = _RISK_TYPE_ALIASES.get(normalized, normalized)
    return RISK_EVIDENCE_BY_TYPE.get(normalized, DEFAULT_EVIDENCE)


def evidence_for_alarm(alarm_type: str) -> EvidenceMedia:
    """Return explicit evidence metadata for a GIS alarm type."""
    return ALARM_EVIDENCE_BY_TYPE.get((alarm_type or "").strip(), DEFAULT_EVIDENCE)


def image_for_risk_event(event_type: str, ordinal: int = 0) -> str:
    """Compatibility wrapper returning the deterministic risk-event path."""
    del ordinal
    return evidence_for_risk_event(event_type).path


def image_for_alarm(alarm_type: str, ordinal: int = 0) -> str:
    """Compatibility wrapper returning the deterministic GIS-alarm path."""
    del ordinal
    return evidence_for_alarm(alarm_type).path
