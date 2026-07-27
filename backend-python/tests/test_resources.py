"""业务资源冒烟测试：列表 200 且 code=0，创建 + 删除闭环。"""

import importlib

from fastapi.testclient import TestClient


def client() -> TestClient:
    app = importlib.import_module("app.main").app
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {_token(c)}"})
    return c


_TOKEN_CACHE: dict[str, str] = {}


def _token(c: TestClient) -> str:
    if "token" not in _TOKEN_CACHE:
        res = c.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        _TOKEN_CACHE["token"] = res.json()["data"]["token"]
    return _TOKEN_CACHE["token"]


def ok_data(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 0
    return body["data"]


LIST_ENDPOINTS = [
    "/api/cranes",
    "/api/cameras",
    "/api/nvrs",
    "/api/speakers",
    "/api/speaker-links",
    "/api/edge-boxes",
    "/api/radars",
    "/api/heartbeats",
    "/api/device-links",
    "/api/device-types",
    "/api/risk-events",
    "/api/violation-categories",
    "/api/audit-logs",
]


def test_all_resource_list_endpoints_return_success_envelope():
    api = client()
    for path in LIST_ENDPOINTS:
        data = ok_data(api.get(path))
        assert "list" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data


def test_list_supports_pagination_and_keyword():
    api = client()
    data = ok_data(api.get("/api/cranes", params={"page": 1, "page_size": 5}))
    assert data["page_size"] == 5
    assert len(data["list"]) <= 5
    assert data["total"] >= 8

    filtered = ok_data(api.get("/api/cranes", params={"keyword": "徐工"}))
    assert filtered["total"] >= 1


def test_crane_detail_contains_realtime():
    api = client()
    first = ok_data(api.get("/api/cranes"))["list"][0]
    detail = ok_data(api.get(f"/api/cranes/{first['id']}"))
    assert set(detail["realtime"]) >= {"load", "load_max", "height", "angle", "wind"}


def test_crane_create_and_delete_roundtrip():
    api = client()
    payload = {
        "code": "CR-TEST-001",
        "name": "测试塔吊",
        "model": "TC6515",
        "manufacturer": "徐工",
        "work_zone": "测试区",
        "status": "normal",
    }
    created = ok_data(api.post("/api/cranes", json=payload))
    new_id = created["id"]
    assert created["code"] == "CR-TEST-001"

    fetched = ok_data(api.get(f"/api/cranes/{new_id}"))
    assert fetched["name"] == "测试塔吊"

    updated = ok_data(api.put(f"/api/cranes/{new_id}", json={"status": "warning"}))
    assert updated["status"] == "warning"

    deleted = ok_data(api.delete(f"/api/cranes/{new_id}"))
    assert deleted["deleted"] is True

    assert api.get(f"/api/cranes/{new_id}").status_code == 404


def test_radar_readings_endpoint():
    api = client()
    first = ok_data(api.get("/api/radars"))["list"][0]
    data = ok_data(api.get(f"/api/radars/{first['id']}/readings"))
    assert "targets" in data


def test_risk_event_handle_transitions_status():
    api = client()
    # 自建待处理事件，避免依赖并消耗共享库中的种子数据
    created = ok_data(api.post("/api/risk-events", json={
        "event_no": "PYTEST-RISK-001", "type": "越界闯入",
        "level": "general", "status": "pending",
    }))
    try:
        data = ok_data(api.post(
            f"/api/risk-events/{created['id']}/handle",
            json={"action": "accept", "handler": "测试员", "note": "受理"},
        ))
        assert data["status"] == "processing"
        assert data["handler"] == "测试员"
    finally:
        api.delete(f"/api/risk-events/{created['id']}")


def test_config_get_and_put():
    api = client()
    data = ok_data(api.get("/api/configs/threshold"))
    assert "value" in data
    updated = ok_data(api.put(
        "/api/configs/threshold",
        json={"value": {"wind_speed_warning": 12.0}},
    ))
    assert updated["value"]["wind_speed_warning"] == 12.0


def test_speaker_link_create_and_delete():
    api = client()
    created = ok_data(api.post(
        "/api/speaker-links",
        json={"speaker_id": 1, "target_type": "camera", "target_id": 2, "trigger_event": "违规闯入"},
    ))
    link_id = created["id"]
    assert api.delete(f"/api/speaker-links/{link_id}").status_code == 200


def test_audit_logs_filter_by_operator():
    api = client()
    data = ok_data(api.get("/api/audit-logs", params={"operator": "张安全"}))
    assert data["total"] >= 1
    assert all("张安全" in row["operator"] for row in data["list"])


def test_audit_logs_filter_by_module():
    api = client()
    data = ok_data(api.get("/api/audit-logs", params={"module": "风险事件"}))
    assert data["total"] >= 1
    assert all(row["module"] == "风险事件" for row in data["list"])


def test_audit_logs_filter_by_date_range():
    api = client()
    data = ok_data(api.get(
        "/api/audit-logs",
        params={"start": "2026-07-19", "end": "2026-07-19"},
    ))
    assert data["total"] >= 1
    assert all(str(row["created_at"]).startswith("2026-07-19") for row in data["list"])

    empty = ok_data(api.get(
        "/api/audit-logs",
        params={"start": "2020-01-01", "end": "2020-12-31"},
    ))
    assert empty["total"] == 0


def test_camera_list_filter_by_type():
    api = client()
    data = ok_data(api.get("/api/cameras", params={"type": "hook"}))
    assert data["total"] >= 1
    assert all(row["type"] == "hook" for row in data["list"])

    unfiltered = ok_data(api.get("/api/cameras"))
    assert unfiltered["total"] > data["total"]
