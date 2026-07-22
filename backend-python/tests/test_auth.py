"""认证接口测试：登录、鉴权、资料与偏好、改密。"""

import importlib

from fastapi.testclient import TestClient


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
