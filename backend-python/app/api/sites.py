"""站点、设备、GIS 围栏与地图告警接口（改为从数据库读）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import ApiResponse, err_not_found, ok
from app.db.database import get_db
from app.schemas.models import Alarm, Device, Fence, MapOverview, Site
from app.services import legacy


router = APIRouter(prefix="/api/sites", tags=["Sites 站点地图"])


def _require_site(db: Session, site_id: str) -> dict:
    site = legacy.find_site(db, site_id)
    if not site:
        raise err_not_found("站点不存在")
    return site


@router.get("", response_model=ApiResponse[list[Site]], summary="站点列表")
def list_sites(db: Session = Depends(get_db)):
    return ok(legacy.list_sites(db))


@router.get("/{site_id}", response_model=ApiResponse[Site], summary="站点详情")
def get_site(site_id: str, db: Session = Depends(get_db)):
    return ok(_require_site(db, site_id))


@router.get(
    "/{site_id}/devices",
    response_model=ApiResponse[list[Device]],
    summary="站点设备点位",
)
def get_site_devices(site_id: str, db: Session = Depends(get_db)):
    _require_site(db, site_id)
    return ok(legacy.list_devices(db, site_id))


@router.get(
    "/{site_id}/fences",
    response_model=ApiResponse[list[Fence]],
    summary="站点 GIS 电子围栏",
)
def get_site_fences(site_id: str, db: Session = Depends(get_db)):
    _require_site(db, site_id)
    return ok(legacy.list_fences(db, site_id))


@router.get(
    "/{site_id}/alarms",
    response_model=ApiResponse[list[Alarm]],
    summary="站点地图告警",
)
def get_site_alarms(site_id: str, db: Session = Depends(get_db)):
    _require_site(db, site_id)
    return ok(legacy.list_alarms(db, site_id))


@router.get(
    "/{site_id}/map-overview",
    response_model=ApiResponse[MapOverview],
    summary="站点地图聚合数据",
)
def get_map_overview(site_id: str, db: Session = Depends(get_db)):
    _require_site(db, site_id)
    return ok(legacy.map_overview(db, site_id))
