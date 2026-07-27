"""认证与个人设置接口。"""

import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.response import BizError, ok
from app.core.security import (
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db import models as m
from app.db.database import get_db
from app.schemas.auth import ChangePasswordIn, LoginIn, RegisterIn, UpdateMeIn

router = APIRouter(prefix="/api/auth", tags=["Auth"])

DEFAULT_PREFERENCES = {
    "theme": "dark",
    "sidebarCollapsed": False,
    "notifyRisk": True,
    "notifyDeviceOffline": True,
    "notifyApproval": False,
    "landingPage": "/workbench",
}


def _now_str() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def _user_payload(user: m.User) -> dict:
    data = user.to_dict()
    data.pop("password_hash", None)
    data["preferences"] = {**DEFAULT_PREFERENCES, **(user.preferences or {})}
    return data


@router.post("/login", summary="账号密码登录")
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(m.User).where(m.User.username == body.username))
    if user is None or not verify_password(body.password, user.password_hash):
        raise BizError(message="账号或密码错误", code=1001, http_status=400)

    ip = request.client.host if request.client else ""
    user.last_login_at = _now_str()
    user.last_login_ip = ip
    db.add(m.AuditLog(operator=user.name or user.username, action="登录",
                      module="用户登录", detail=f"{user.username} 登录系统",
                      ip=ip, created_at=_now_str()))
    db.commit()
    db.refresh(user)
    return ok({"token": create_token(user.id), "user": _user_payload(user)})


@router.post("/register", summary="注册账号")
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    username = body.username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        raise BizError(message="账号需为 3-20 位字母、数字或下划线", code=1002, http_status=400)
    if db.scalar(select(m.User).where(m.User.username == username)) is not None:
        raise BizError(message="该账号已被注册，请更换账号或直接登录", code=1001, http_status=400)

    name = (body.name or "").strip() or username
    ip = request.client.host if request.client else ""
    user = m.User(
        username=username,
        password_hash=hash_password(body.password),
        name=name,
        role="安全员",
        email=(body.email or "").strip(),
        avatar_text=name[0],
        last_login_at=_now_str(),
        last_login_ip=ip,
        preferences=body.preferences or {},
    )
    db.add(user)
    db.add(m.AuditLog(operator=name, action="注册", module="用户注册",
                      detail=f"{username} 注册账号", ip=ip, created_at=_now_str()))
    db.commit()
    db.refresh(user)
    return ok({"token": create_token(user.id), "user": _user_payload(user)}, message="注册成功")


@router.get("/me", summary="当前用户信息")
def me(user: m.User = Depends(get_current_user)):
    return ok(_user_payload(user))


@router.put("/me", summary="更新资料与偏好")
def update_me(
    body: UpdateMeIn,
    user: m.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        user.email = body.email
    if body.avatar_text is not None:
        user.avatar_text = body.avatar_text
    if body.avatar is not None:
        user.avatar = body.avatar
    if body.preferences is not None:
        user.preferences = {**DEFAULT_PREFERENCES, **(user.preferences or {}), **body.preferences}
    db.commit()
    db.refresh(user)
    return ok(_user_payload(user))


@router.put("/password", summary="修改登录密码")
def change_password(
    body: ChangePasswordIn,
    user: m.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.old_password, user.password_hash):
        raise BizError(message="原密码不正确", code=1001, http_status=400)
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return ok(message="密码修改成功")
