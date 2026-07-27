"""丰富的中文演示种子数据。

包含各业务资源（每类 8-15 条，风险事件 30+ 条）以及兼容旧 dashboard/sites
接口的地图数据（复用 mock_data 中的原始 camelCase payload）。
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data import mock_data as md
from app.data.demo_media import image_for_alarm, image_for_risk_event
from app.db import models as m


# --------------------------------------------------------------------------- #
# 吊车
# --------------------------------------------------------------------------- #
CRANES = [
    ("CR-8012", "1号塔式起重机", "TC6515", "中联重科", "A区-东侧", "normal", "2023-05-12"),
    ("CR-8013", "2号塔式起重机", "TC7020", "中联重科", "A区-西侧", "warning", "2023-06-01"),
    ("CR-8021", "1号履带起重机", "XGC85", "徐工", "B区-北侧", "normal", "2022-11-20"),
    ("CR-8022", "2号汽车起重机", "QY50K", "徐工", "B区-南侧", "danger", "2022-09-15"),
    ("CR-8031", "3号汽车起重机", "QY25K5", "徐工", "C区-中央", "normal", "2024-01-08"),
    ("CR-8032", "4号塔式起重机", "STT293", "波坦(Potain)", "C区-东侧", "offline", "2021-07-30"),
    ("CR-8041", "5号履带起重机", "SCC8100A", "三一重工", "D区-北侧", "normal", "2023-03-18"),
    ("CR-8042", "6号全地面起重机", "GMK5250L", "利勃海尔(Liebherr)", "D区-西侧", "warning", "2023-08-22"),
    ("CR-8051", "7号塔式起重机", "TC5613", "永茂建机", "E区-东侧", "normal", "2024-02-14"),
    ("CR-8052", "8号汽车起重机", "STC500", "三一重工", "E区-南侧", "normal", "2023-10-05"),
    ("CR-8061", "9号履带起重机", "QUY55", "抚顺永茂", "F区-中央", "normal", "2022-12-11"),
    ("CR-8062", "10号全地面起重机", "ATF220G-5", "塔德诺(Tadano)", "F区-西侧", "warning", "2023-04-27"),
]

CAMERAS = [
    ("CAM-01", "A区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.11"),
    ("CAM-02", "A区吊钩球机", "hook", "DS-2DC7523IW", "192.168.1.12"),
    ("CAM-03", "1号塔吊驾驶室摄像", "cab", "DS-2CD2T47G2", "192.168.1.13"),
    ("CAM-04", "B区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.14"),
    ("CAM-05", "B区吊钩球机", "hook", "DS-2DC7523IW", "192.168.1.15"),
    ("CAM-06", "C区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.16"),
    ("CAM-07", "2号汽车吊驾驶室摄像", "cab", "DS-2CD2T47G2", "192.168.1.17"),
    ("CAM-08", "C区吊钩球机", "hook", "DS-2DC7523IW", "192.168.1.18"),
    ("CAM-09", "D区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.19"),
    ("CAM-10", "E区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.20"),
    ("CAM-11", "E区吊钩球机", "hook", "DS-2DC7523IW", "192.168.1.21"),
    ("CAM-12", "F区周界枪机", "perimeter", "DS-2CD3T46WDV3", "192.168.1.22"),
]

NVRS = [
    ("NVR-01", "A区录像主机", "192.168.1.201", 32, 18, 8192, 5012, 30, "online"),
    ("NVR-02", "B区录像主机", "192.168.1.202", 32, 22, 8192, 6600, 30, "online"),
    ("NVR-03", "C区录像主机", "192.168.1.203", 16, 9, 4096, 2100, 30, "online"),
    ("NVR-04", "D区录像主机", "192.168.1.204", 16, 7, 4096, 1550, 30, "online"),
    ("NVR-05", "E区录像主机", "192.168.1.205", 32, 20, 8192, 7200, 30, "warning"),
    ("NVR-06", "F区录像主机", "192.168.1.206", 16, 11, 4096, 900, 30, "online"),
    ("NVR-07", "指挥中心汇聚主机", "192.168.1.207", 64, 40, 16384, 9800, 45, "online"),
    ("NVR-08", "备用录像主机", "192.168.1.208", 16, 0, 4096, 0, 30, "offline"),
]

SPEAKERS = [
    ("SPK-01", "A区语音警示音柱", "A区-东侧", "192.168.2.11", 75, "online"),
    ("SPK-02", "A区西侧音柱", "A区-西侧", "192.168.2.12", 70, "online"),
    ("SPK-03", "B区语音警示音柱", "B区-北侧", "192.168.2.13", 80, "online"),
    ("SPK-04", "C区语音警示音柱", "C区-中央", "192.168.2.14", 65, "online"),
    ("SPK-05", "D区语音警示音柱", "D区-北侧", "192.168.2.15", 72, "offline"),
    ("SPK-06", "E区语音警示音柱", "E区-东侧", "192.168.2.16", 78, "online"),
    ("SPK-07", "F区语音警示音柱", "F区-中央", "192.168.2.17", 68, "fault"),
    ("SPK-08", "指挥中心广播音柱", "指挥中心", "192.168.2.18", 60, "online"),
]

EDGE_BOXES = [
    ("BOX-011", "A区边缘AI盒", "192.168.3.11", "V2.6.1", 42.5, 61.0, 55.0, 48.2, "online"),
    ("BOX-012", "A区西侧边缘盒", "192.168.3.12", "V2.6.1", 38.0, 57.5, 50.0, 46.0, "online"),
    ("BOX-013", "B区边缘AI盒", "192.168.3.13", "V2.6.0", 66.0, 72.0, 61.0, 53.5, "warning"),
    ("BOX-014", "C区边缘AI盒", "192.168.3.14", "V2.6.1", 33.0, 48.0, 44.0, 44.8, "online"),
    ("BOX-015", "D区边缘AI盒", "192.168.3.15", "V2.5.9", 51.0, 63.0, 58.0, 50.1, "online"),
    ("BOX-016", "E区边缘AI盒", "192.168.3.16", "V2.6.1", 45.5, 60.0, 52.0, 49.0, "online"),
    ("BOX-017", "F区边缘AI盒", "192.168.3.17", "V2.6.0", 0.0, 0.0, 0.0, 0.0, "offline"),
    ("BOX-018", "指挥中心汇聚盒", "192.168.3.18", "V2.6.2", 58.0, 68.0, 63.0, 51.7, "online"),
]

RADARS = [
    ("RAD-01", "A区防碰撞雷达", "A区-东侧", "192.168.4.11", 80, 120, "online"),
    ("RAD-02", "A区回转雷达", "A区-西侧", "192.168.4.12", 60, 90, "online"),
    ("RAD-03", "B区防碰撞雷达", "B区-北侧", "192.168.4.13", 100, 120, "online"),
    ("RAD-04", "C区周界雷达", "C区-中央", "192.168.4.14", 80, 180, "online"),
    ("RAD-05", "D区防碰撞雷达", "D区-北侧", "192.168.4.15", 60, 120, "warning"),
    ("RAD-06", "E区周界雷达", "E区-东侧", "192.168.4.16", 80, 150, "online"),
    ("RAD-07", "F区防碰撞雷达", "F区-中央", "192.168.4.17", 100, 120, "online"),
    ("RAD-08", "指挥中心测试雷达", "指挥中心", "192.168.4.18", 40, 90, "offline"),
]

DEVICE_TYPES = [
    ("DT-CRANE", "起重机", "作业设备", "crane", 12, True),
    ("DT-CAMERA", "摄像头", "视频设备", "camera", 12, True),
    ("DT-NVR", "网络录像机", "视频设备", "nvr", 8, True),
    ("DT-SPEAKER", "语音音柱", "警示设备", "speaker", 8, True),
    ("DT-EDGE", "边缘计算盒", "算力设备", "chip", 8, True),
    ("DT-RADAR", "毫米波雷达", "感知设备", "radar", 8, True),
    ("DT-GATEWAY", "物联网关", "网络设备", "gateway", 4, True),
    ("DT-SENSOR", "载重传感器", "感知设备", "sensor", 6, True),
]

VIOLATION_CATEGORIES = [
    ("VC-01", "违规闯入", "critical", "作业区违规闯入相关行为", ["人员进入回转半径", "人员穿越警戒线", "吊物下方站人"]),
    ("VC-02", "超载起吊", "critical", "载荷超过额定值相关行为", ["超载起吊", "斜拉斜吊", "群吊超载"]),
    ("VC-03", "违章操作", "major", "违反操作规程的行为", ["无证操作", "违规指挥", "带载行走超速"]),
    ("VC-04", "防护缺失", "major", "个人防护装备缺失", ["未佩戴安全帽", "未系安全带", "未穿反光衣"]),
    ("VC-05", "设备隐患", "general", "设备状态异常隐患", ["设备离线", "限位失效", "钢丝绳磨损"]),
    ("VC-06", "环境风险", "general", "作业环境风险", ["大风超阈值起吊", "夜间违规作业", "视线遮挡作业"]),
    ("VC-07", "临时用电", "general", "临时用电违规", ["私拉乱接", "配电箱未接地", "电缆浸水"]),
    ("VC-08", "文明施工", "general", "文明施工相关", ["材料乱堆放", "通道占用", "未设警示标识"]),
]

# 风险事件类型/区域素材
RE_TYPES = [
    ("违规闯入", "critical"), ("超载起吊", "critical"), ("未佩戴安全帽", "major"),
    ("违章操作", "major"), ("斜拉斜吊", "critical"), ("设备离线", "general"),
    ("大风超阈值起吊", "major"), ("吊物下方站人", "critical"), ("未系安全带", "major"),
    ("限位失效", "general"),
]
RE_ZONES = ["A区-东侧", "A区-西侧", "B区-北侧", "B区-南侧", "C区-中央", "D区-北侧", "E区-东侧", "F区-中央"]
RE_STATUS_CYCLE = ["pending", "processing", "resolved", "closed"]
RE_HANDLERS = ["", "张安全", "李工", "王队长", "赵监理"]

HEARTBEAT_TYPES = [
    ("CR-8012", "crane", "1号塔式起重机", 30, 12, 0, "healthy"),
    ("CR-8022", "crane", "2号汽车起重机", 30, 210, 2, "delayed"),
    ("CR-8032", "crane", "4号塔式起重机", 30, 0, 15, "lost"),
    ("CAM-01", "camera", "A区周界枪机", 15, 8, 0, "healthy"),
    ("CAM-05", "camera", "B区吊钩球机", 15, 26, 1, "healthy"),
    ("NVR-05", "nvr", "E区录像主机", 60, 88, 0, "healthy"),
    ("SPK-05", "speaker", "D区语音警示音柱", 30, 0, 9, "lost"),
    ("SPK-07", "speaker", "F区语音警示音柱", 30, 320, 3, "delayed"),
    ("BOX-013", "edge_box", "B区边缘AI盒", 20, 45, 0, "healthy"),
    ("BOX-017", "edge_box", "F区边缘AI盒", 20, 0, 20, "lost"),
    ("RAD-03", "radar", "B区防碰撞雷达", 10, 6, 0, "healthy"),
    ("RAD-05", "radar", "D区防碰撞雷达", 10, 140, 1, "delayed"),
]

AUDIT_LOGS = [
    ("张安全", "登录", "系统", "管理员登录平台", "10.20.1.11", "2026-07-19T08:02:11+08:00"),
    ("李工", "新增", "吊车管理", "新增吊车 CR-8052", "10.20.1.15", "2026-07-19T09:14:30+08:00"),
    ("王队长", "处置", "风险事件", "处置事件 EV202607190035", "10.20.1.22", "2026-07-19T10:05:48+08:00"),
    ("赵监理", "修改", "系统配置", "更新风速报警阈值", "10.20.1.30", "2026-07-19T11:20:02+08:00"),
    ("张安全", "删除", "摄像头管理", "删除离线摄像头 CAM-99", "10.20.1.11", "2026-07-19T13:41:19+08:00"),
    ("李工", "绑定", "设备关联", "为 CR-8012 绑定 RAD-01", "10.20.1.15", "2026-07-19T14:02:55+08:00"),
    ("王队长", "导出", "风险事件", "导出7月事件台账", "10.20.1.22", "2026-07-19T15:30:41+08:00"),
    ("系统", "巡检", "心跳检测", "自动巡检发现 BOX-017 离线", "127.0.0.1", "2026-07-19T15:31:02+08:00"),
]

CONFIGS = {
    "system": {
        "platform_name": "擎安智吊 · 吊装安全巡检系统",
        "logo_url": "/static/logo.png",
        "session_timeout_min": 30,
        "watermark_enabled": True,
        "watermark_text": "擎安智吊",
        "theme": "dark",
    },
    "approval": {
        "risk_event_approval_enabled": True,
        "approval_levels": 2,
        "level_names": ["班组安全员", "项目安全总监"],
        "timeout_hours": 24,
        "auto_escalate": True,
    },
    "threshold": {
        "wind_speed_warning": 10.8,
        "wind_speed_danger": 13.9,
        "load_percent_warning": 90,
        "load_percent_danger": 100,
        "height_warning_m": 60,
        "temperature_warning_c": 70,
    },
    "push": {
        "sms": {"enabled": True, "receivers": ["13800000001", "13800000002"]},
        "email": {"enabled": True, "receivers": ["safety@qingan.com"]},
        "app": {"enabled": True, "receivers": ["安全部全员"]},
        "speaker_link": {"enabled": True, "trigger_levels": ["critical", "major"]},
    },
}


def _radar_readings(seed: int) -> list[dict]:
    levels = ["safe", "warning", "danger"]
    return [
        {
            "distance": round(8 + (seed * 3 + i * 5) % 60 + 0.5, 1),
            "angle": (seed * 17 + i * 40) % 360,
            "speed": round(0.4 + ((seed + i) % 5) * 0.6, 1),
            "level": levels[(seed + i) % 3],
        }
        for i in range(1 + seed % 3)
    ]


def _crane_realtime(idx: int) -> dict:
    return {
        "load": round(8 + idx * 1.3, 1),
        "load_max": 20 + (idx % 4) * 10,
        "height": round(30 + idx * 2.1, 1),
        "angle": (120 + idx * 23) % 360,
        "wind": round(3.5 + (idx % 5) * 0.9, 1),
    }


def _seed_business(db: Session) -> None:
    # 吊车
    cranes = []
    for i, (code, name, model, mfr, zone, status, install) in enumerate(CRANES):
        c = m.Crane(
            code=code, name=name, model=model, manufacturer=mfr, work_zone=zone,
            status=status, install_date=install, linked_device_ids=[],
            realtime=_crane_realtime(i),
        )
        cranes.append(c)
        db.add(c)
    db.flush()

    # 录像机
    nvrs = []
    for code, name, ip, ct, cu, st_g, su_g, ret, status in NVRS:
        n = m.Nvr(code=code, name=name, ip=ip, channels_total=ct, channels_used=cu,
                  storage_total_gb=st_g, storage_used_gb=su_g, retention_days=ret, status=status)
        nvrs.append(n)
        db.add(n)
    db.flush()

    # 摄像头（分配到吊车/录像机）
    cameras = []
    for i, (code, name, ctype, res, ip) in enumerate(CAMERAS):
        cam = m.Camera(
            code=code, name=name, type=ctype, crane_id=cranes[i % len(cranes)].id,
            work_zone=cranes[i % len(cranes)].work_zone, ip=ip, resolution=res,
            nvr_id=nvrs[i % len(nvrs)].id,
            rtsp_url=f"rtsp://{ip}:554/Streaming/Channels/101",
            status="online" if i % 6 else "offline",
        )
        cameras.append(cam)
        db.add(cam)

    # 音柱
    speakers = []
    for code, name, zone, ip, vol, status in SPEAKERS:
        sp = m.Speaker(code=code, name=name, work_zone=zone, ip=ip, volume=vol, status=status)
        speakers.append(sp)
        db.add(sp)

    # 边缘盒子
    for i, (code, name, ip, ver, cpu, mem, disk, temp, status) in enumerate(EDGE_BOXES):
        db.add(m.EdgeBox(code=code, name=name, crane_id=cranes[i % len(cranes)].id, ip=ip,
                         version=ver, cpu_percent=cpu, mem_percent=mem, disk_percent=disk,
                         temperature=temp, status=status))

    # 雷达
    radars = []
    for i, (code, name, zone, ip, rng, ang, status) in enumerate(RADARS):
        rd = m.Radar(code=code, name=name, crane_id=cranes[i % len(cranes)].id, work_zone=zone,
                     ip=ip, range_m=rng, angle_deg=ang, status=status, readings=_radar_readings(i))
        radars.append(rd)
        db.add(rd)
    db.flush()

    # 音柱关联
    for i, sp in enumerate(speakers[:6]):
        db.add(m.SpeakerLink(speaker_id=sp.id, target_type="camera",
                             target_id=cameras[i % len(cameras)].id, trigger_event="违规闯入"))
    db.add(m.SpeakerLink(speaker_id=speakers[0].id, target_type="fence",
                         target_id=1, trigger_event="人员越界"))

    # 设备关联（每台吊车绑定其区内的摄像头/雷达/音柱/边缘盒）
    for i, c in enumerate(cranes[:8]):
        db.add(m.DeviceLink(crane_id=c.id, device_type="camera", device_id=cameras[i % len(cameras)].id))
        db.add(m.DeviceLink(crane_id=c.id, device_type="radar", device_id=radars[i % len(radars)].id))
        db.add(m.DeviceLink(crane_id=c.id, device_type="speaker", device_id=speakers[i % len(speakers)].id))

    # 设备类型
    for code, name, cat, icon, cnt, enabled in DEVICE_TYPES:
        db.add(m.DeviceType(code=code, name=name, category=cat, icon=icon,
                            device_count=cnt, enabled=enabled))

    # 违章大类
    for code, name, level, desc, subs in VIOLATION_CATEGORIES:
        db.add(m.ViolationCategory(code=code, name=name, level=level, sub_count=len(subs),
                                   enabled=True, description=desc, sub_items=subs))

    # 风险事件 36 条
    for i in range(36):
        etype, level = RE_TYPES[i % len(RE_TYPES)]
        status = RE_STATUS_CYCLE[i % 4]
        handler = RE_HANDLERS[0] if status == "pending" else RE_HANDLERS[1 + i % 4]
        day = 19 - (i // 6)
        db.add(m.RiskEvent(
            event_no=f"EV202607{day:02d}{i:04d}",
            type=etype, level=level, status=status,
            work_zone=RE_ZONES[i % len(RE_ZONES)],
            device_code=CRANES[i % len(CRANES)][0],
            occurred_at=f"2026-07-{day:02d}T{8 + i % 12:02d}:{(i * 7) % 60:02d}:00+08:00",
            handler=handler,
            handle_note="" if status == "pending" else f"{handler} 已跟进处理",
            image_url=image_for_risk_event(etype, i),
        ))

    # 心跳
    for code, dtype, dname, interval, latency, miss, status in HEARTBEAT_TYPES:
        db.add(m.Heartbeat(device_code=code, device_type=dtype, device_name=dname,
                           interval_s=interval, last_at="2026-07-19T15:42:00+08:00",
                           latency_ms=latency, miss_count=miss, status=status))

    # 审计日志
    for operator, action, module, detail, ip, ts in AUDIT_LOGS:
        db.add(m.AuditLog(operator=operator, action=action, module=module,
                          detail=detail, ip=ip, created_at=ts))

    # 系统配置
    for key, value in CONFIGS.items():
        db.add(m.Config(key=key, value=value))


def _seed_legacy(db: Session) -> None:
    for site in md.SITES:
        db.add(m.LegacySite(id=site["id"], payload=site))
    for dev in md.DEVICES:
        db.add(m.LegacyDevice(id=dev["id"], site_id=dev["siteId"], payload=dev))
    for fence in md.FENCES:
        db.add(m.LegacyFence(id=fence["id"], site_id=fence["siteId"], payload=fence))
    for alarm in md.ALARMS:
        db.add(m.LegacyAlarm(id=alarm["id"], site_id=alarm["siteId"],
                             occurred_at=alarm["occurredAt"], payload=alarm))
    for site_id, weather in md.WEATHER.items():
        db.add(m.LegacyWeather(site_id=site_id, payload=weather))


def _seed_users(db: Session) -> None:
    from app.core.security import hash_password

    db.add(m.User(
        username="admin",
        password_hash=hash_password("admin123"),
        name="安全管理员",
        role="系统管理员",
        email="admin@qingan.com",
        avatar_text="安",
        preferences={},
    ))


def _sync_demo_media(db: Session) -> bool:
    """Refresh evidence paths in an existing database without changing schemas."""
    changed = False

    events = db.scalars(select(m.RiskEvent).order_by(m.RiskEvent.id)).all()
    for index, event in enumerate(events):
        expected = image_for_risk_event(event.type, index)
        if event.image_url != expected:
            event.image_url = expected
            changed = True

    alarms = db.scalars(select(m.LegacyAlarm).order_by(m.LegacyAlarm.id)).all()
    for index, alarm in enumerate(alarms):
        payload = dict(alarm.payload)
        evidence = dict(payload.get("evidence") or {})
        expected = image_for_alarm(payload.get("type", ""), index)
        if evidence.get("imageUrl") != expected:
            evidence["imageUrl"] = expected
            payload["evidence"] = evidence
            alarm.payload = payload
            changed = True

    return changed


def _sync_legacy_geo(db: Session) -> bool:
    """Keep legacy map payloads (site/device/fence/alarm) aligned with mock_data.

    地图坐标/围栏若在 mock_data 中调整，即使数据库已播种也能同步生效，
    无需删库重建。"""
    changed = False

    def _apply(model, items, id_key: str) -> None:
        nonlocal changed
        for item in items:
            row = db.get(model, item[id_key])
            if row is not None and row.payload != item:
                row.payload = item
                changed = True

    _apply(m.LegacySite, md.SITES, "id")
    _apply(m.LegacyDevice, md.DEVICES, "id")
    _apply(m.LegacyFence, md.FENCES, "id")
    _apply(m.LegacyAlarm, md.ALARMS, "id")
    return changed


def seed(db: Session) -> bool:
    """若吊车表与站点表均为空则播种，返回是否执行了播种。"""
    has_business = db.scalar(select(m.Crane.id).limit(1))
    has_legacy = db.scalar(select(m.LegacySite.id).limit(1))
    has_user = db.scalar(select(m.User.id).limit(1))
    seeded = False
    if not has_business:
        _seed_business(db)
        seeded = True
    if not has_legacy:
        _seed_legacy(db)
        seeded = True
    if not has_user:
        _seed_users(db)
        seeded = True

    if seeded:
        db.flush()
    geo_changed = _sync_legacy_geo(db)
    media_changed = _sync_demo_media(db)
    if seeded or geo_changed or media_changed:
        db.commit()
    return seeded
