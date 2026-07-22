"""业务资源路由：标准 CRUD + 特殊端点。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api._crud import build_crud_router, get_or_404, paginate, query_list
from app.core.response import BizError, ok
from app.db import models as m
from app.db.database import get_db
from app.schemas import resources as s


routers: list[APIRouter] = []

# --------------------------- 标准 CRUD 资源 --------------------------- #
cranes_router = build_crud_router(
    prefix="/api/cranes", tag="Cranes 吊车", model=m.Crane,
    create_schema=s.CraneCreate, update_schema=s.CraneUpdate,
    keyword_fields=["code", "name", "model", "manufacturer", "work_zone"],
)
cameras_router = build_crud_router(
    prefix="/api/cameras", tag="Cameras 摄像头", model=m.Camera,
    create_schema=s.CameraCreate, update_schema=s.CameraUpdate,
    keyword_fields=["code", "name", "work_zone", "ip"],
)
nvrs_router = build_crud_router(
    prefix="/api/nvrs", tag="NVRs 录像机", model=m.Nvr,
    create_schema=s.NvrCreate, update_schema=s.NvrUpdate,
    keyword_fields=["code", "name", "ip"],
)
speakers_router = build_crud_router(
    prefix="/api/speakers", tag="Speakers 音柱", model=m.Speaker,
    create_schema=s.SpeakerCreate, update_schema=s.SpeakerUpdate,
    keyword_fields=["code", "name", "work_zone", "ip"],
)
edge_boxes_router = build_crud_router(
    prefix="/api/edge-boxes", tag="EdgeBoxes 边缘盒子", model=m.EdgeBox,
    create_schema=s.EdgeBoxCreate, update_schema=s.EdgeBoxUpdate,
    keyword_fields=["code", "name", "ip", "version"],
)
radars_router = build_crud_router(
    prefix="/api/radars", tag="Radars 雷达", model=m.Radar,
    create_schema=s.RadarCreate, update_schema=s.RadarUpdate,
    keyword_fields=["code", "name", "work_zone", "ip"],
)
device_types_router = build_crud_router(
    prefix="/api/device-types", tag="DeviceTypes 设备类型", model=m.DeviceType,
    create_schema=s.DeviceTypeCreate, update_schema=s.DeviceTypeUpdate,
    keyword_fields=["code", "name", "category"],
)
violation_categories_router = build_crud_router(
    prefix="/api/violation-categories", tag="ViolationCategories 违章大类",
    model=m.ViolationCategory,
    create_schema=s.ViolationCategoryCreate, update_schema=s.ViolationCategoryUpdate,
    keyword_fields=["code", "name", "description"],
)
risk_events_router = build_crud_router(
    prefix="/api/risk-events", tag="RiskEvents 风险事件", model=m.RiskEvent,
    create_schema=s.RiskEventCreate, update_schema=s.RiskEventUpdate,
    keyword_fields=["event_no", "type", "work_zone", "device_code", "handler"],
)

routers += [
    cranes_router, cameras_router, nvrs_router, speakers_router,
    edge_boxes_router, radars_router, device_types_router,
    violation_categories_router, risk_events_router,
]


# --------------------------- 雷达实时读数 --------------------------- #
@radars_router.get("/{item_id}/readings", summary="雷达实时目标读数")
def radar_readings(item_id: int, db: Session = Depends(get_db)):
    radar = get_or_404(db, m.Radar, item_id)
    return ok({
        "radar_id": radar.id,
        "code": radar.code,
        "status": radar.status,
        "targets": radar.readings or [],
    })


# --------------------------- 风险事件处置流转 --------------------------- #
_HANDLE_NEXT = {
    "accept": "processing",
    "process": "processing",
    "resolve": "resolved",
    "close": "closed",
}


@risk_events_router.post("/{item_id}/handle", summary="推进风险事件处置流程")
def handle_risk_event(item_id: int, payload: s.RiskEventHandle, db: Session = Depends(get_db)):
    event = get_or_404(db, m.RiskEvent, item_id)
    new_status = _HANDLE_NEXT.get(payload.action)
    if new_status is None:
        raise BizError("无效的处置动作 (accept/process/resolve/close)", code=1002)
    event.status = new_status
    if payload.handler:
        event.handler = payload.handler
    if payload.note:
        note = f"[{payload.action}] {payload.note}"
        event.handle_note = f"{event.handle_note}\n{note}".strip() if event.handle_note else note
    db.commit()
    db.refresh(event)
    return ok(event.to_dict())


# --------------------------- 音柱关联 --------------------------- #
speaker_links_router = APIRouter(prefix="/api/speaker-links", tags=["SpeakerLinks 音柱关联"])


@speaker_links_router.get("", summary="音柱关联列表")
def list_speaker_links(
    speaker_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(m.SpeakerLink)
    if speaker_id is not None:
        stmt = stmt.where(m.SpeakerLink.speaker_id == speaker_id)
    rows = db.scalars(stmt.order_by(m.SpeakerLink.id.desc())).all()
    items = [r.to_dict() for r in rows]
    return ok(paginate(items, len(items), 1, len(items) or 1))


@speaker_links_router.post("", summary="新增音柱关联")
def create_speaker_link(payload: s.SpeakerLinkCreate, db: Session = Depends(get_db)):
    obj = m.SpeakerLink(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ok(obj.to_dict())


@speaker_links_router.delete("/{item_id}", summary="删除音柱关联")
def delete_speaker_link(item_id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.SpeakerLink, item_id)
    db.delete(obj)
    db.commit()
    return ok({"id": item_id, "deleted": True})


routers.append(speaker_links_router)


# --------------------------- 设备关联（按吊车分组） --------------------------- #
device_links_router = APIRouter(prefix="/api/device-links", tags=["DeviceLinks 设备关联"])


@device_links_router.get("", summary="设备关联列表（按吊车分组）")
def list_device_links(
    crane_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(m.DeviceLink)
    if crane_id is not None:
        stmt = stmt.where(m.DeviceLink.crane_id == crane_id)
    rows = db.scalars(stmt).all()

    cranes = {c.id: c for c in db.scalars(select(m.Crane)).all()}
    grouped: dict[int, dict] = {}
    for link in rows:
        group = grouped.setdefault(link.crane_id, {
            "crane_id": link.crane_id,
            "crane_code": cranes[link.crane_id].code if link.crane_id in cranes else None,
            "crane_name": cranes[link.crane_id].name if link.crane_id in cranes else None,
            "camera": [], "radar": [], "speaker": [], "edge_box": [],
        })
        bucket = group.get(link.device_type)
        if bucket is not None:
            bucket.append({"link_id": link.id, "device_id": link.device_id})
    items = list(grouped.values())
    return ok(paginate(items, len(items), 1, len(items) or 1))


@device_links_router.post("", summary="绑定设备到吊车")
def bind_device(payload: s.DeviceLinkCreate, db: Session = Depends(get_db)):
    obj = m.DeviceLink(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ok(obj.to_dict())


@device_links_router.delete("/{item_id}", summary="解绑设备")
def unbind_device(item_id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.DeviceLink, item_id)
    db.delete(obj)
    db.commit()
    return ok({"id": item_id, "deleted": True})


routers.append(device_links_router)


# --------------------------- 心跳检测（仅列表） --------------------------- #
heartbeats_router = APIRouter(prefix="/api/heartbeats", tags=["Heartbeats 心跳检测"])


@heartbeats_router.get("", summary="心跳检测列表")
def list_heartbeats(
    keyword: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return ok(query_list(
        db, m.Heartbeat, ["device_code", "device_name", "device_type"],
        keyword, status, page, page_size,
    ))


routers.append(heartbeats_router)


# --------------------------- 审计日志（仅列表） --------------------------- #
audit_logs_router = APIRouter(prefix="/api/audit-logs", tags=["AuditLogs 审计日志"])


@audit_logs_router.get("", summary="审计日志列表")
def list_audit_logs(
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return ok(query_list(
        db, m.AuditLog, ["operator", "action", "module", "detail", "ip"],
        keyword, None, page, page_size,
    ))


routers.append(audit_logs_router)


# --------------------------- 系统配置（按 key） --------------------------- #
configs_router = APIRouter(prefix="/api/configs", tags=["Configs 系统配置"])
_CONFIG_KEYS = {"system", "approval", "threshold", "push"}


@configs_router.get("/{key}", summary="获取配置")
def get_config(key: str, db: Session = Depends(get_db)):
    row = db.scalar(select(m.Config).where(m.Config.key == key))
    if row is None:
        if key not in _CONFIG_KEYS:
            raise BizError("配置项不存在", code=1004, http_status=404)
        return ok({"key": key, "value": {}})
    return ok({"key": row.key, "value": row.value})


@configs_router.put("/{key}", summary="更新配置")
def update_config(key: str, payload: s.ConfigUpdate, db: Session = Depends(get_db)):
    row = db.scalar(select(m.Config).where(m.Config.key == key))
    if row is None:
        row = m.Config(key=key, value=payload.value)
        db.add(row)
    else:
        row.value = payload.value
    db.commit()
    db.refresh(row)
    return ok({"key": row.key, "value": row.value})


routers.append(configs_router)
