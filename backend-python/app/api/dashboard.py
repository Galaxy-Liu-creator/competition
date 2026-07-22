"""态势总览接口（改为从数据库聚合）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import ApiResponse, ok
from app.db.database import get_db
from app.schemas.models import (
    Alarm,
    DashboardOverview,
    DashboardStats,
    DistributionItem,
    Trend,
)
from app.services import legacy


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard 态势总览"])


@router.get("/overview", response_model=ApiResponse[DashboardOverview], summary="首屏聚合数据")
def overview(db: Session = Depends(get_db)):
    return ok(legacy.dashboard_overview(db))


@router.get("/stats", response_model=ApiResponse[DashboardStats], summary="核心统计卡片")
def stats(db: Session = Depends(get_db)):
    return ok(legacy.dashboard_stats(db))


@router.get("/trend", response_model=ApiResponse[Trend], summary="近七日安全趋势")
def trend(db: Session = Depends(get_db)):
    return ok(legacy.dashboard_trend(db))


@router.get(
    "/category-distribution",
    response_model=ApiResponse[list[DistributionItem]],
    summary="事件类别分布",
)
def category_distribution(db: Session = Depends(get_db)):
    return ok(legacy.category_distribution(db))


@router.get(
    "/status-distribution",
    response_model=ApiResponse[list[DistributionItem]],
    summary="事件处置状态分布",
)
def status_distribution(db: Session = Depends(get_db)):
    return ok(legacy.alarm_status_distribution(db))


@router.get(
    "/recent-alarms",
    response_model=ApiResponse[list[Alarm]],
    summary="最新安全事件",
)
def recent_alarms(db: Session = Depends(get_db)):
    return ok(legacy.list_alarms(db)[:8])
