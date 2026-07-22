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


def assert_success(response):
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["message"] == "ok"
    return body["data"]


def assert_gcj02_point(point: dict):
    assert isinstance(point["lng"], (int, float))
    assert isinstance(point["lat"], (int, float))
    assert point["coordinateSystem"] == "gcj02"


def test_health_checks_are_public_and_use_the_standard_envelope():
    root = assert_success(client().get("/"))
    health = assert_success(client().get("/health"))

    assert root["name"] == "擎安智吊"
    assert root["docs"] == "/docs"
    assert health["status"] == "healthy"


def test_cors_allows_the_vite_development_origin():
    response = client().options(
        "/api/dashboard/overview",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_dashboard_overview_contains_first_screen_sections():
    overview = assert_success(client().get("/api/dashboard/overview"))

    assert set(overview) >= {
        "stats",
        "trend",
        "riskDistribution",
        "deviceStatus",
        "recentAlarms",
        "siteSummary",
    }
    assert overview["stats"]["activeSites"] >= 1
    assert overview["stats"]["totalDevices"] >= 1
    assert overview["trend"]["dates"]
    assert overview["recentAlarms"]
    assert overview["siteSummary"]["totalSites"] >= 1


def test_legacy_dashboard_sections_remain_individually_available():
    api = client()

    assert_success(api.get("/api/dashboard/stats"))
    assert_success(api.get("/api/dashboard/trend"))
    assert_success(api.get("/api/dashboard/category-distribution"))
    assert_success(api.get("/api/dashboard/status-distribution"))
    assert_success(api.get("/api/dashboard/recent-alarms"))


def test_site_list_and_detail_expose_gcj02_coordinates():
    api = client()
    sites = assert_success(api.get("/api/sites"))

    assert sites
    site = sites[0]
    assert site["id"] == "site-001"
    assert site["coordinateSystem"] == "gcj02"
    assert_gcj02_point(site["center"])

    detail = assert_success(api.get(f"/api/sites/{site['id']}"))
    assert detail["id"] == site["id"]
    assert detail["defaultZoom"] >= 10
    assert_gcj02_point(detail["center"])


def test_site_resource_endpoints_match_map_overview():
    api = client()
    overview = assert_success(api.get("/api/sites/site-001/map-overview"))
    devices = assert_success(api.get("/api/sites/site-001/devices"))
    fences = assert_success(api.get("/api/sites/site-001/fences"))
    alarms = assert_success(api.get("/api/sites/site-001/alarms"))

    assert overview["siteId"] == "site-001"
    assert overview["coordinateSystem"] == "gcj02"
    assert_gcj02_point(overview["center"])
    assert devices == overview["devices"]
    assert fences == overview["fences"]
    assert alarms == overview["alarms"]
    assert overview["weather"]["safeForLifting"] in (True, False)


def test_map_resources_use_gis_coordinates_not_video_pixel_coordinates():
    overview = assert_success(client().get("/api/sites/site-001/map-overview"))

    assert overview["devices"]
    assert overview["fences"]
    assert overview["alarms"]

    for device in overview["devices"]:
        assert_gcj02_point(device)

    for fence in overview["fences"]:
        assert fence["coordinateSystem"] == "gcj02"
        assert len(fence["points"]) >= 3
        for point in fence["points"]:
            assert_gcj02_point(point)
            assert -180 <= point["lng"] <= 180
            assert -90 <= point["lat"] <= 90

    for alarm in overview["alarms"]:
        assert_gcj02_point(alarm)


def test_unknown_site_uses_uniform_not_found_response():
    response = client().get("/api/sites/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "code": 1004,
        "message": "站点不存在",
        "data": None,
    }

