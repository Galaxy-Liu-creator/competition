"""通用 CRUD 路由工厂与分页工具。

统一响应 {code:0,message:'ok',data}；列表返回 {list,total,page,page_size}，
支持 keyword/status/page/page_size 查询参数。
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.response import BizError, err_not_found, ok
from app.db.database import get_db


def paginate(items: list[Any], total: int, page: int, page_size: int) -> dict:
    return {"list": items, "total": total, "page": page, "page_size": page_size}


def query_list(
    db: Session,
    model: Any,
    keyword_fields: list[str],
    keyword: str | None,
    status: str | None,
    page: int,
    page_size: int,
    order_desc: bool = True,
) -> dict:
    stmt = select(model)
    count_stmt = select(func.count()).select_from(model)

    conditions = []
    if keyword and keyword_fields:
        likes = [getattr(model, f).ilike(f"%{keyword}%") for f in keyword_fields]
        conditions.append(or_(*likes))
    if status and hasattr(model, "status"):
        conditions.append(getattr(model, "status") == status)

    for cond in conditions:
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.scalar(count_stmt) or 0
    order_col = model.id.desc() if order_desc else model.id.asc()
    stmt = stmt.order_by(order_col).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(stmt).all()
    return paginate([r.to_dict() for r in rows], total, page, page_size)


def get_or_404(db: Session, model: Any, item_id: int):
    obj = db.get(model, item_id)
    if obj is None:
        raise err_not_found("资源不存在")
    return obj


def build_crud_router(
    *,
    prefix: str,
    tag: str,
    model: Any,
    create_schema: Any,
    update_schema: Any,
    keyword_fields: list[str],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", summary="列表")
    def list_items(
        keyword: str | None = Query(None),
        status: str | None = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=200),
        db: Session = Depends(get_db),
    ):
        return ok(query_list(db, model, keyword_fields, keyword, status, page, page_size))

    @router.get("/{item_id}", summary="详情")
    def get_item(item_id: int, db: Session = Depends(get_db)):
        return ok(get_or_404(db, model, item_id).to_dict())

    @router.post("", summary="新增")
    def create_item(payload: create_schema, db: Session = Depends(get_db)):  # type: ignore[valid-type]
        obj = model(**payload.model_dump(exclude_unset=True))
        db.add(obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise BizError("编码已存在或数据冲突", code=1003, http_status=409)
        db.refresh(obj)
        return ok(obj.to_dict())

    @router.put("/{item_id}", summary="修改")
    def update_item(item_id: int, payload: update_schema, db: Session = Depends(get_db)):  # type: ignore[valid-type]
        obj = get_or_404(db, model, item_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise BizError("编码已存在或数据冲突", code=1003, http_status=409)
        db.refresh(obj)
        return ok(obj.to_dict())

    @router.delete("/{item_id}", summary="删除")
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        obj = get_or_404(db, model, item_id)
        db.delete(obj)
        db.commit()
        return ok({"id": item_id, "deleted": True})

    return router
