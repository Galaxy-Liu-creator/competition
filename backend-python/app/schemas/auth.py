"""认证与个人设置相关的请求模型。"""

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=64)


class UpdateMeIn(BaseModel):
    name: str | None = None
    email: str | None = None
    avatar_text: str | None = Field(default=None, max_length=4)
    preferences: dict | None = None


class ChangePasswordIn(BaseModel):
    old_password: str = Field(min_length=1, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)
