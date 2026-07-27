# Frontend Licensed Dataset Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace unlicensed or broken demo-image references with a centralized, attributable licensed-media catalog, wire backend risk/GIS evidence to those assets, and verify the affected frontend flows.

**Architecture:** Store browser assets under `frontend-vue/public/dataset`, keep full provenance in `manifest.json`, and expose stable IDs through a small frontend catalog. Mirror only the stable path selection rules in a backend `demo_media.py` module so fresh and existing SQLite databases receive deterministic `/dataset/...` evidence URLs without changing API schemas.

**Tech Stack:** Vue 3, Vite, JavaScript modules, FastAPI, SQLAlchemy 2.0, SQLite, pytest, Wikimedia Commons API, Playwright CLI.

---

## File map

- Create `frontend-vue/public/dataset/construction/*.jpg`: exact Wikimedia Commons thumbnails downloaded from verified file pages.
- Create `frontend-vue/public/dataset/ppe/*.jpg`: verified Wikimedia Commons worker/PPE safety images with stable names.
- Create `frontend-vue/public/dataset/manifest.json`: canonical machine-readable asset provenance, license, tags, overlay semantics, and SHA-256.
- Create `frontend-vue/public/dataset/README.md`: human-readable attribution and “real image vs simulated telemetry” explanation.
- Create `frontend-vue/src/data/demoMedia.js`: stable frontend media IDs, helpers, and deterministic risk-type mapping.
- Create `backend-python/app/data/demo_media.py`: backend-safe path constants and deterministic risk/GIS mapping.
- Create `backend-python/tests/test_demo_media.py`: unit/API coverage for path rules and local-file existence.
- Modify `backend-python/app/db/seed.py`: assign licensed paths on fresh seed and normalize existing database rows idempotently.
- Modify `backend-python/app/data/mock_data.py`: give legacy GIS alarms licensed evidence paths.
- Modify `frontend-vue/src/views/crane/CraneMonitorView.vue`: use catalog paths.
- Modify `frontend-vue/src/views/crane/PerimeterCameraView.vue`: use catalog paths.
- Modify `frontend-vue/src/views/crane/RadarInfoView.vue`: use a licensed catalog frame and correctly map radar API fields.
- Modify `frontend-vue/src/views/ledger/RiskEventView.vue`: prefer backend `image_url` and use type-based fallback.
- Modify `frontend-vue/src/components/map/SiteMap.vue`: render an offline vector fallback when AMap credentials/SDK are unavailable.
- Modify `frontend-vue/src/views/WorkbenchView.vue`: map the actual nested dashboard API response.
- Modify `frontend-vue/src/views/ReportView.vue`: derive report KPIs/charts deterministically from risk-event and dashboard APIs.
- Modify `README.md`: document datasets, attribution location, simulated values, and AMap fallback.

### Task 1: Acquire and catalogue licensed assets

- [ ] **Step 1: Download exact verified Commons thumbnails**

Use `Invoke-WebRequest` with the verified `thumburl` values from the Commons API and save them as:

```text
construction/tower-crane-aerial-01.jpg
construction/tower-crane-aerial-02.jpg
construction/mobile-crane-e16.jpg
construction/mobile-crane-precast-wall.jpg
construction/liebherr-ltm1500-genie.jpg
```

Expected: five JPEGs, each non-empty and loadable, with metadata matching its Commons file page.

- [ ] **Step 2: Download selected worker/PPE Commons images to stable names**

Download six watermark-free images from their verified Commons file pages to:

```text
ppe/ppe-helmet-0014.jpg
ppe/ppe-site-0517.jpg
ppe/ppe-site-0637.jpg
ppe/ppe-site-0675.jpg
ppe/ppe-site-0701.jpg
ppe/ppe-site-0803.jpg
```

Expected: every stable copy is watermark-free, visually relevant, and traceable to its individual Commons author/license metadata.

- [ ] **Step 3: Compute local SHA-256 and write manifest/README**

Each `manifest.json` asset must contain this exact shape:

```json
{
  "id": "tower-crane-aerial-01",
  "path": "/dataset/construction/tower-crane-aerial-01.jpg",
  "kind": "construction",
  "tags": ["tower-crane", "construction-site", "aerial"],
  "source": {
    "name": "Wikimedia Commons",
    "page": "https://commons.wikimedia.org/wiki/File:Tower_crane_aerial_01.jpg",
    "author": "Wikideas1"
  },
  "license": {
    "spdx": "CC0-1.0",
    "name": "Creative Commons Zero v1.0 Universal",
    "url": "https://creativecommons.org/publicdomain/zero/1.0/"
  },
  "attribution": "Tower crane aerial 01 — Wikideas1 — CC0 1.0",
  "sha256": "<computed lowercase hex>",
  "displayOverlay": "demo-overlay"
}
```

Worker/PPE records use their individual Commons file pages and per-file public-domain/CC BY/CC BY-SA terms. UI boxes remain `demo-overlay` because no original annotation files are bundled.

### Task 2: Lock backend behavior with failing tests

**Files:**

- Create: `backend-python/tests/test_demo_media.py`
- Test: `backend-python/tests/test_demo_media.py`

- [ ] **Step 1: Write deterministic path unit tests**

```python
from pathlib import Path

from app.data.demo_media import DATASET_PATHS, image_for_alarm, image_for_risk_event


def test_risk_media_mapping_is_deterministic():
    assert image_for_risk_event("未佩戴安全帽", 3) == image_for_risk_event("未佩戴安全帽", 3)
    assert image_for_alarm("no_helmet", 2) == image_for_alarm("no_helmet", 2)


def test_demo_media_paths_are_licensed_frontend_assets():
    public_dir = Path(__file__).resolve().parents[2] / "frontend-vue" / "public"
    for path in DATASET_PATHS:
        assert path.startswith("/dataset/")
        assert "aswin_hoist_" not in path
        assert "/static/events" not in path
        assert (public_dir / path.removeprefix("/")).is_file()
```

- [ ] **Step 2: Write API assertions**

```python
def test_risk_and_map_api_evidence_uses_dataset_assets(authenticated_client):
    risk_items = ok_data(authenticated_client.get("/api/risk-events"))["list"]
    overview = ok_data(authenticated_client.get("/api/sites/site-001/map-overview"))
    paths = [item["image_url"] for item in risk_items]
    paths.extend(a["evidence"]["imageUrl"] for a in overview["alarms"])
    assert all(path and path.startswith("/dataset/") for path in paths)
    assert not any("aswin_hoist_" in path or "/static/events" in path for path in paths)
```

Use the existing `client()` and `ok_data()` helpers if introducing a fixture would duplicate test infrastructure.

- [ ] **Step 3: Run the focused tests and confirm RED**

Run: `pytest tests/test_demo_media.py -v`

Expected: collection/import failure because `app.data.demo_media` does not exist yet.

### Task 3: Implement deterministic backend media mapping

**Files:**

- Create: `backend-python/app/data/demo_media.py`
- Modify: `backend-python/app/data/mock_data.py`
- Modify: `backend-python/app/db/seed.py`

- [ ] **Step 1: Add the minimal mapping module**

```python
CONSTRUCTION_IMAGES = (
    "/dataset/construction/tower-crane-aerial-01.jpg",
    "/dataset/construction/tower-crane-aerial-02.jpg",
    "/dataset/construction/mobile-crane-e16.jpg",
    "/dataset/construction/mobile-crane-precast-wall.jpg",
    "/dataset/construction/liebherr-ltm1500-genie.jpg",
)
PPE_IMAGES = (
    "/dataset/ppe/ppe-helmet-0014.jpg",
    "/dataset/ppe/ppe-site-0517.jpg",
    "/dataset/ppe/ppe-site-0637.jpg",
    "/dataset/ppe/ppe-site-0675.jpg",
    "/dataset/ppe/ppe-site-0701.jpg",
    "/dataset/ppe/ppe-site-0803.jpg",
)
DATASET_PATHS = CONSTRUCTION_IMAGES + PPE_IMAGES


def _pick(items: tuple[str, ...], ordinal: int) -> str:
    return items[ordinal % len(items)]


def image_for_risk_event(event_type: str, ordinal: int = 0) -> str:
    text = event_type or ""
    if any(token in text for token in ("安全帽", "安全带", "反光衣")):
        return _pick(PPE_IMAGES, ordinal)
    return _pick(CONSTRUCTION_IMAGES, ordinal)


def image_for_alarm(alarm_type: str, ordinal: int = 0) -> str:
    if alarm_type in {"no_helmet", "no_vest", "ppe_violation"}:
        return _pick(PPE_IMAGES, ordinal)
    return _pick(CONSTRUCTION_IMAGES, ordinal)
```

- [ ] **Step 2: Seed fresh risk and GIS rows with licensed paths**

Replace `image_url=f"/static/events/EV{i:04d}.jpg"` with `image_for_risk_event(etype, i)`. Set every `mock_data.ALARMS[*]["evidence"]["imageUrl"]` using `image_for_alarm(type, index)`.

- [ ] **Step 3: Normalize existing SQLite rows idempotently**

Add a helper called on every `seed(db)` execution:

```python
def _sync_demo_media(db: Session) -> bool:
    changed = False
    for index, event in enumerate(db.scalars(select(m.RiskEvent).order_by(m.RiskEvent.id)).all()):
        expected = image_for_risk_event(event.type, index)
        if event.image_url != expected:
            event.image_url = expected
            changed = True
    for index, alarm in enumerate(db.scalars(select(m.LegacyAlarm).order_by(m.LegacyAlarm.id)).all()):
        payload = dict(alarm.payload)
        evidence = dict(payload.get("evidence") or {})
        expected = image_for_alarm(payload.get("type", ""), index)
        if evidence.get("imageUrl") != expected:
            evidence["imageUrl"] = expected
            payload["evidence"] = evidence
            alarm.payload = payload
            changed = True
    return changed
```

Commit when seeding or syncing changed data, but preserve `seed()`'s boolean meaning (“fresh rows were inserted”).

- [ ] **Step 4: Run focused and full backend tests**

Run: `pytest tests/test_demo_media.py -v`

Expected: PASS.

Run: `pytest -q`

Expected: all backend tests pass.

### Task 4: Centralize frontend media usage

**Files:**

- Create: `frontend-vue/src/data/demoMedia.js`
- Modify: four visual pages listed in the file map.

- [ ] **Step 1: Add catalog helpers**

```javascript
export const DEMO_MEDIA = Object.freeze({
  towerAerial01: { id: 'tower-crane-aerial-01', path: '/dataset/construction/tower-crane-aerial-01.jpg', kind: 'construction', tags: ['tower-crane'], license: 'CC0-1.0', overlay: 'demo-overlay' },
  noHelmet0014: { id: 'ppe-helmet-0014', path: '/dataset/ppe/ppe-helmet-0014.jpg', kind: 'ppe', tags: ['person', 'helmet'], license: 'CC-BY-4.0', overlay: 'demo-overlay' },
})

export const mediaPath = (id, fallback = 'towerAerial01') =>
  (DEMO_MEDIA[id] || DEMO_MEDIA[fallback]).path

export const riskMediaPath = (type = '') => {
  const text = String(type).toLowerCase()
  if (text.includes('安全帽') || text.includes('安全带') || text.includes('helmet') || text.includes('ppe')) {
    return mediaPath('noHelmet0014')
  }
  return mediaPath('towerAerial01')
}
```

Expand `DEMO_MEDIA` to all 11 manifest assets and export grouped IDs for monitor pages.

- [ ] **Step 2: Replace page-local hardcoded paths**

Import `mediaPath` in Crane Monitor, Perimeter Camera, and Radar Info. Replace every `/dataset/aswin_hoist_*` and flat `/dataset/site_*`/`crane_*` reference with stable catalog IDs.

- [ ] **Step 3: Make Risk Events prefer backend evidence**

```javascript
img: r.image_url || riskMediaPath(r.type),
```

Delete `imgPool`; update demo rows to use `riskMediaPath(type)` or `mediaPath(id)`.

- [ ] **Step 4: Search for forbidden references**

Run: `rg -n "aswin_hoist_|/static/events|const imgPool" frontend-vue/src backend-python/app`

Expected: no matches.

### Task 5: Make dashboard, reports, and map fallback data-coherent

**Files:**

- Modify: `frontend-vue/src/components/map/SiteMap.vue`
- Modify: `frontend-vue/src/views/WorkbenchView.vue`
- Modify: `frontend-vue/src/views/ReportView.vue`

- [ ] **Step 1: Fetch map data before deciding renderer**

Always call `loadOverview()`. If AMap credentials are present, render the SDK map. Otherwise set `fallbackOverview` and render a local SVG/canvas plane that normalizes longitude/latitude into percentages, draws polygons, devices, alarms, a legend, and a “离线示意图 · GCJ-02 演示坐标” badge.

- [ ] **Step 2: Map the actual dashboard response**

Use `ov.stats`, `ov.trend`, `ov.recentAlarms`, `ov.riskDistribution`, and `ov.siteSummary`; compute online rate from `onlineDevices / totalDevices`. Do not expect nonexistent flat fields such as `ov.craneOnline`.

- [ ] **Step 3: Build report charts from APIs deterministically**

Load up to 200 risk events with `riskEventApi.list`, group them by date/type/work zone/status, and build KPIs and charts without `Math.random()`. If the API is unavailable, use a fixed fallback array so two reloads produce identical charts.

- [ ] **Step 4: Build frontend**

Run: `npm run build`

Expected: Vite build succeeds with no missing imports or asset-resolution errors.

### Task 6: Update project documentation

**Files:**

- Modify: `README.md`
- Create: `frontend-vue/public/dataset/README.md`

- [ ] **Step 1: Document source and attribution**

List every Commons file page, author, license, and `manifest.json` as the authoritative machine-readable inventory. Record that watermarked third-party candidates were evaluated and excluded.

- [ ] **Step 2: Document simulation boundaries and map behavior**

State that media are real public images, overlays and structured telemetry are deterministic demo data, and AMap automatically degrades to an offline GCJ-02 schematic when credentials are missing.

### Task 7: Verify the complete system

- [ ] **Step 1: Run static checks**

```text
pytest -q
npm run build
rg -n "aswin_hoist_|/static/events" frontend-vue/src backend-python/app
```

Expected: tests/build pass; forbidden-reference search has no output.

- [ ] **Step 2: Start backend and frontend**

Run FastAPI on `127.0.0.1:8000` and Vite on `127.0.0.1:5173` in hidden background processes, reusing installed dependencies.

- [ ] **Step 3: Browser QA**

Using a unique Playwright CLI session, log in with the demo account and visit:

```text
/workbench
/crane/monitor
/crane/perimeter-camera
/crane/radar-info
/ledger/risk-event
/fence
/report
```

For each route, verify the primary panel is visible, `<img>` elements have `naturalWidth > 0`, the map fallback or AMap canvas is visible, and there are no console errors or failed `/dataset` requests.

- [ ] **Step 4: Inspect final diff and status**

Run `git diff --check`, `git diff --stat`, and `git status --short`. Preserve unrelated user files and do not commit unless explicitly requested.
