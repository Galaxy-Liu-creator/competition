"""密码哈希与 JWT 工具，以及当前用户依赖。"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.response import BizError
from app.db import models as m
from app.db.database import get_db

_bearer = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _unauthorized(message: str = "登录状态无效或已过期，请重新登录") -> BizError:
    return BizError(message=message, code=401, http_status=401)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> m.User:
    if credentials is None:
        raise _unauthorized("未登录，请先登录")
    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise _unauthorized()
    user = db.get(m.User, int(payload.get("sub", 0)))
    if user is None:
        raise _unauthorized()
    return user
