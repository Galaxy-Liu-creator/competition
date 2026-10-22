"""油擎智安 FastAPI 入口。"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import auth, dashboard, sites
from app.api.resources import routers as resource_routers
from app.core.config import settings
from app.core.response import BizError, fail, ok
from app.core.security import get_current_user
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="油擎智安 API",
    description="吊装安全运营平台演示后端，提供态势总览与站点地图数据。",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BizError)
async def biz_error_handler(request: Request, exc: BizError):
    return JSONResponse(
        status_code=exc.http_status,
        content=fail(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(item) for item in first.get("loc", []) if item != "body")
    reason = first.get("msg", "参数校验失败")
    detail = f"{location}: {reason}" if location else reason
    return JSONResponse(status_code=422, content=fail(1002, f"参数校验失败 ({detail})"))


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    code_map = {404: 1004, 422: 1002}
    message = exc.detail if isinstance(exc.detail, str) else "请求错误"
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(code_map.get(exc.status_code, 1000), message),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=fail(1000, "服务器内部错误"))


app.include_router(auth.router)

# 业务接口统一要求 JWT 登录（/api/auth/login、/、/health 除外）
_protected = [Depends(get_current_user)]
app.include_router(dashboard.router, dependencies=_protected)
app.include_router(sites.router, dependencies=_protected)

for _router in resource_routers:
    app.include_router(_router, dependencies=_protected)


@app.get("/", tags=["Health"], summary="服务信息")
def root():
    return ok(
        {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }
    )


@app.get("/health", tags=["Health"], summary="健康检查")
def health():
    return ok({"status": "healthy", "service": settings.APP_NAME})

