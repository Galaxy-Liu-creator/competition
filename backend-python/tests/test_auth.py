"""认证接口测试：登录、注册、鉴权、资料与偏好、改密、头像。"""

import importlib

from fastapi.testclient import TestClient

REG_USERNAME = "pytest_reg_user"


def client() -> TestClient:
    app = importlib.import_module("app.main").app
    return TestClient(app)


def login(c: TestClient, username="admin", password="admin123"):
    return c.post("/api/auth/login", json={"username": username, "password": password})


def auth_client() -> TestClient:
    c = client()
    token = login(c).json()["data"]["token"]
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


def _delete_user(username: str) -> None:
    from sqlalchemy import delete

    from app.db import models as m
    from app.db.database import SessionLocal

    with SessionLocal() as db:
        db.execute(delete(m.User).where(m.User.username == username))
        db.commit()


def test_login_success_returns_token_and_user():
    res = login(client())
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["token"]
    assert data["user"]["username"] == "admin"
    assert "password_hash" not in data["user"]
    assert data["user"]["preferences"]["theme"] in ("dark", "light", "auto")


def test_login_wrong_password_fails():
    res = login(client(), password="wrong")
    assert res.status_code == 400
    assert res.json()["code"] == 1001


def test_protected_api_requires_token():
    res = client().get("/api/cranes")
    assert res.status_code == 401
    assert res.json()["code"] == 401


def test_protected_api_accepts_valid_token():
    res = auth_client().get("/api/cranes")
    assert res.status_code == 200
    assert res.json()["code"] == 0


def test_me_read_and_update_preferences():
    c = auth_client()
    me = c.get("/api/auth/me").json()["data"]
    assert me["username"] == "admin"

    res = c.put("/api/auth/me", json={"name": "安全管理员", "preferences": {"theme": "light"}})
    assert res.json()["data"]["preferences"]["theme"] == "light"
    # 还原，避免影响其他用例
    c.put("/api/auth/me", json={"preferences": {"theme": "dark"}})


def test_change_password_flow():
    c = auth_client()
    res = c.put("/api/auth/password", json={"old_password": "bad", "new_password": "abc12345"})
    assert res.status_code == 400

    assert c.put("/api/auth/password",
                 json={"old_password": "admin123", "new_password": "abc12345"}).status_code == 200
    assert login(client(), password="abc12345").status_code == 200
    # 还原密码
    assert c.put("/api/auth/password",
                 json={"old_password": "abc12345", "new_password": "admin123"}).status_code == 200


def test_register_login_and_avatar_flow():
    _delete_user(REG_USERNAME)
    try:
        c = client()
        res = c.post("/api/auth/register", json={
            "username": REG_USERNAME, "password": "secret66",
            "name": "测试注册", "preferences": {"theme": "light"},
        })
        assert res.status_code == 200, res.text
        data = res.json()["data"]
        assert data["token"]
        assert data["user"]["username"] == REG_USERNAME
        assert data["user"]["name"] == "测试注册"
        assert data["user"]["avatar_text"] == "测"
        assert data["user"]["preferences"]["theme"] == "light"
        assert "password_hash" not in data["user"]

        # 注册后可直接用新账号登录
        assert login(client(), REG_USERNAME, "secret66").status_code == 200

        # 用注册返回的 token 上传/清除头像
        c.headers.update({"Authorization": f"Bearer {data['token']}"})
        avatar = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
        assert c.put("/api/auth/me", json={"avatar": avatar}).json()["data"]["avatar"] == avatar
        assert c.put("/api/auth/me", json={"avatar": ""}).json()["data"]["avatar"] == ""
    finally:
        _delete_user(REG_USERNAME)


def test_register_rejects_duplicate_and_bad_username():
    _delete_user(REG_USERNAME)
    try:
        c = client()
        body = {"username": REG_USERNAME, "password": "secret66"}
        assert c.post("/api/auth/register", json=body).status_code == 200

        dup = c.post("/api/auth/register", json=body)
        assert dup.status_code == 400
        assert dup.json()["code"] == 1001

        bad = c.post("/api/auth/register", json={"username": "a!", "password": "secret66"})
        assert bad.status_code == 400
        assert bad.json()["code"] == 1002

        short = c.post("/api/auth/register", json={"username": "okuser01", "password": "123"})
        assert short.status_code == 422
    finally:
        _delete_user(REG_USERNAME)
