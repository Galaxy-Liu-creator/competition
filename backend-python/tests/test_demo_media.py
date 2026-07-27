"""Tests for licensed, semantically explicit frontend evidence media."""

import hashlib
import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient


def _client() -> TestClient:
    app = importlib.import_module("app.main").app
    client = TestClient(app)
    token = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    ).json()["data"]["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def _data(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 0
    return body["data"]


def _public_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "frontend-vue" / "public"


def _jpeg_dimensions(path: Path) -> tuple[int, int]:
    """Read JPEG dimensions without adding a Pillow test dependency."""
    data = path.read_bytes()
    assert data[:2] == b"\xff\xd8", f"not a JPEG: {path}"
    offset = 2
    start_of_frame = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while offset < len(data):
        while offset < len(data) and data[offset] != 0xFF:
            offset += 1
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        assert offset < len(data), f"invalid JPEG marker stream: {path}"
        marker = data[offset]
        offset += 1
        if marker in {0x01, 0xD8, 0xD9}:
            continue
        assert offset + 2 <= len(data), f"truncated JPEG segment: {path}"
        segment_length = int.from_bytes(data[offset:offset + 2], "big")
        assert segment_length >= 2, f"invalid JPEG segment length: {path}"
        if marker in start_of_frame:
            assert offset + 7 <= len(data), f"truncated JPEG SOF: {path}"
            height = int.from_bytes(data[offset + 3:offset + 5], "big")
            width = int.from_bytes(data[offset + 5:offset + 7], "big")
            return width, height
        offset += segment_length
    raise AssertionError(f"JPEG dimensions not found: {path}")


def test_risk_media_mapping_is_explicit_and_semantically_typed():
    from app.data.demo_media import (
        ALARM_EVIDENCE_BY_TYPE,
        RISK_EVIDENCE_BY_TYPE,
        evidence_for_alarm,
        evidence_for_risk_event,
        image_for_alarm,
        image_for_risk_event,
    )
    from app.db.seed import RE_TYPES

    risk_types = {event_type for event_type, _level in RE_TYPES}
    assert set(RISK_EVIDENCE_BY_TYPE) == risk_types
    assert set(ALARM_EVIDENCE_BY_TYPE) == {
        "person_in_rotation_radius",
        "overload_risk",
        "device_offline",
        "cross_fence",
        "no_helmet",
    }

    for event_type in risk_types:
        evidence = evidence_for_risk_event(event_type)
        assert evidence.path.startswith("/dataset/")
        assert evidence.evidence_mode in {"direct-visual", "overlay-assisted", "sensor-context"}
        assert evidence.evidence_label
        assert evidence.source_node
        assert evidence.note
        assert image_for_risk_event(event_type, 0) == evidence.path
        assert image_for_risk_event(event_type, 99) == evidence.path

    for alarm_type in ALARM_EVIDENCE_BY_TYPE:
        evidence = evidence_for_alarm(alarm_type)
        assert image_for_alarm(alarm_type, 0) == evidence.path
        assert image_for_alarm(alarm_type, 99) == evidence.path


def test_ppe_and_sensor_event_evidence_modes_are_truthful():
    from app.data.demo_media import evidence_for_alarm, evidence_for_risk_event

    no_helmet = evidence_for_risk_event("未佩戴安全帽")
    no_harness = evidence_for_risk_event("未系安全带")
    assert no_helmet.path == "/dataset/violations/worker-without-ppe.jpg"
    assert no_helmet.evidence_mode == "direct-visual"
    assert no_harness.path == "/dataset/ppe/ppe-site-0701.jpg"
    assert no_harness.evidence_mode == "direct-visual"

    for event_type in ("超载起吊", "斜拉斜吊", "设备离线", "大风超阈值起吊", "限位失效"):
        assert evidence_for_risk_event(event_type).evidence_mode == "sensor-context"

    assert evidence_for_risk_event("违规闯入").evidence_mode == "overlay-assisted"
    assert evidence_for_risk_event("吊物下方站人").evidence_mode == "overlay-assisted"
    assert evidence_for_alarm("no_helmet").path == no_helmet.path
    assert evidence_for_alarm("cross_fence").evidence_mode == "overlay-assisted"
    assert evidence_for_alarm("person_in_rotation_radius").evidence_mode == "overlay-assisted"
    assert evidence_for_alarm("overload_risk").evidence_mode == "sensor-context"
    assert evidence_for_alarm("device_offline").evidence_mode == "sensor-context"


def test_demo_media_manifest_matches_files_and_semantics():
    from app.data.demo_media import DATASET_PATHS, RISK_EVIDENCE_BY_TYPE, ALARM_EVIDENCE_BY_TYPE

    public_dir = _public_dir()
    manifest_path = public_dir / "dataset" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = {asset["path"]: asset for asset in manifest["assets"]}
    assert DATASET_PATHS
    assert set(DATASET_PATHS) == set(assets)

    for path in DATASET_PATHS:
        assert path.startswith("/dataset/")
        assert "aswin_hoist_" not in path
        assert "/static/events" not in path
        file_path = public_dir / path.removeprefix("/")
        assert file_path.is_file()

        asset = assets[path]
        assert asset["source"]["name"]
        assert asset["source"]["page"].startswith("https://commons.wikimedia.org/")
        assert asset["source"]["assetUrl"].startswith("https://upload.wikimedia.org/")
        assert asset["source"]["author"]
        assert asset["license"]["spdx"]
        assert asset["license"]["name"]
        assert asset["license"]["url"].startswith("http")
        assert asset["attribution"]
        assert asset["evidenceMode"] in {"direct-visual", "overlay-assisted", "sensor-context"}
        assert asset["evidenceFor"]
        assert asset["sha256"] == hashlib.sha256(file_path.read_bytes()).hexdigest()
        assert asset["dimensions"] == dict(zip(("width", "height"), _jpeg_dimensions(file_path)))

    no_helmet_asset = assets["/dataset/violations/worker-without-ppe.jpg"]
    assert "no-hard-hat" in no_helmet_asset["tags"]
    assert "hard-hat" not in no_helmet_asset["tags"]
    assert "未佩戴安全帽" in no_helmet_asset["evidenceFor"]
    assert "no_helmet" in no_helmet_asset["evidenceFor"]

    for event_type, evidence in RISK_EVIDENCE_BY_TYPE.items():
        assert event_type in assets[evidence.path]["evidenceFor"]
    for alarm_type, evidence in ALARM_EVIDENCE_BY_TYPE.items():
        assert alarm_type in assets[evidence.path]["evidenceFor"]


def test_risk_and_map_api_evidence_uses_dataset_assets():
    api = _client()
    risk_items = _data(api.get("/api/risk-events", params={"page_size": 200}))["list"]
    overview = _data(api.get("/api/sites/site-001/map-overview"))
    paths = [item["image_url"] for item in risk_items]
    paths.extend(
        alarm["evidence"]["imageUrl"]
        for alarm in overview["alarms"]
    )
    assert paths
    assert all(path and path.startswith("/dataset/") for path in paths)
    assert not any(
        "aswin_hoist_" in path or "/static/events" in path
        for path in paths
    )

    from app.data.demo_media import evidence_for_alarm, evidence_for_risk_event

    assert all(
        item["image_url"] == evidence_for_risk_event(item["type"]).path
        for item in risk_items
    )
    assert all(
        alarm["evidence"]["imageUrl"] == evidence_for_alarm(alarm["type"]).path
        for alarm in overview["alarms"]
    )
