// Stable licensed media IDs for demo surfaces. Full source, author, license,
// dimensions, and hashes live in /public/dataset/manifest.json.

const defineMedia = (media) => Object.freeze({ overlay: 'demo-overlay', ...media })

export const DEMO_MEDIA = Object.freeze({
  towerCraneAerial01: defineMedia({
    id: 'tower-crane-aerial-01', path: '/dataset/construction/tower-crane-aerial-01.jpg',
    kind: 'construction', tags: ['tower-crane', 'construction-site', 'aerial'], license: 'CC0-1.0',
  }),
  towerCraneAerial02: defineMedia({
    id: 'tower-crane-aerial-02', path: '/dataset/construction/tower-crane-aerial-02.jpg',
    kind: 'construction', tags: ['tower-crane', 'construction-site', 'aerial'], license: 'CC0-1.0',
  }),
  mobileCraneE16: defineMedia({
    id: 'mobile-crane-e16', path: '/dataset/construction/mobile-crane-e16.jpg',
    kind: 'construction', tags: ['mobile-crane', 'crane-truck'], license: 'CC-BY-SA-2.0',
  }),
  mobileCranePrecastWall: defineMedia({
    id: 'mobile-crane-precast-wall', path: '/dataset/construction/mobile-crane-precast-wall.jpg',
    kind: 'construction', tags: ['mobile-crane', 'precast-concrete', 'lifting'], license: 'CC-BY-SA-3.0-AU',
  }),
  liebherrLtm1500Genie: defineMedia({
    id: 'liebherr-ltm1500-genie', path: '/dataset/construction/liebherr-ltm1500-genie.jpg',
    kind: 'construction', tags: ['mobile-crane', 'construction-site'], license: 'CC-BY-SA-4.0',
  }),
  ppeHelmet0014: defineMedia({
    id: 'ppe-helmet-0014', path: '/dataset/ppe/ppe-helmet-0014.jpg',
    kind: 'ppe', tags: ['construction-worker', 'hard-hat', 'person'], license: 'CC-BY-SA-3.0',
  }),
  ppeSite0517: defineMedia({
    id: 'ppe-site-0517', path: '/dataset/ppe/ppe-site-0517.jpg',
    kind: 'ppe', tags: ['construction-worker', 'hard-hat', 'fall-protection'], license: 'CC-BY-SA-4.0',
  }),
  ppeSite0637: defineMedia({
    id: 'ppe-site-0637', path: '/dataset/ppe/ppe-site-0637.jpg',
    kind: 'ppe', tags: ['construction-worker', 'hard-hat', 'eye-protection'], license: 'CC-BY-2.0',
  }),
  ppeSite0675: defineMedia({
    id: 'ppe-site-0675', path: '/dataset/ppe/ppe-site-0675.jpg',
    kind: 'ppe', tags: ['construction-worker', 'hard-hat', 'person'], license: 'CC-BY-SA-3.0',
  }),
  ppeSite0701: defineMedia({
    id: 'ppe-site-0701', path: '/dataset/ppe/ppe-site-0701.jpg',
    kind: 'ppe', tags: ['construction-worker', 'no-fall-protection', 'safety-violation'], license: 'LicenseRef-Public-Domain',
  }),
  ppeSite0803: defineMedia({
    id: 'ppe-site-0803', path: '/dataset/ppe/ppe-site-0803.jpg',
    kind: 'ppe', tags: ['construction-worker', 'hard-hat', 'fall-protection'], license: 'CC-BY-2.0',
  }),
  workerWithoutPpe: defineMedia({
    id: 'worker-without-ppe', path: '/dataset/violations/worker-without-ppe.jpg',
    kind: 'violation', tags: ['construction-worker', 'no-hard-hat', 'no-ppe', 'work-at-height'], license: 'LicenseRef-Public-Domain',
  }),
  unsafeCraneParking: defineMedia({
    id: 'unsafe-crane-parking', path: '/dataset/violations/unsafe-crane-parking.jpg',
    kind: 'violation', tags: ['heavy-equipment', 'unsafe-parking', 'unsafe-operation'], license: 'LicenseRef-Public-Domain',
  }),
  drywallCraneWorksite: defineMedia({
    id: 'drywall-crane-worksite', path: '/dataset/lifting/drywall-crane-worksite.jpg',
    kind: 'lifting', tags: ['crane-truck', 'cluttered-worksite', 'material-yard'], license: 'LicenseRef-Public-Domain',
  }),
  heavyLoadLift: defineMedia({
    id: 'heavy-load-lift', path: '/dataset/lifting/heavy-load-lift.jpg',
    kind: 'lifting', tags: ['heavy-load', 'crane-lift', 'tag-line', 'worker'], license: 'LicenseRef-Public-Domain',
  }),
  trenchBoxGuidance: defineMedia({
    id: 'trench-box-guidance', path: '/dataset/lifting/trench-box-guidance.jpg',
    kind: 'lifting', tags: ['suspended-load', 'worker', 'danger-zone-context'], license: 'LicenseRef-Public-Domain',
  }),
  improperEyebolt: defineMedia({
    id: 'improper-eyebolt', path: '/dataset/lifting/improper-eyebolt.jpg',
    kind: 'lifting', tags: ['improper-rigging', 'unsafe-eyebolt', 'lifting-hardware'], license: 'LicenseRef-Public-Domain',
  }),
  craneHookGuidance: defineMedia({
    id: 'crane-hook-guidance', path: '/dataset/lifting/crane-hook-guidance.jpg',
    kind: 'lifting', tags: ['crane-hook', 'signal-person', 'scaffolding', 'compliant-ppe'], license: 'CC-BY-2.0',
  }),
  craneLiftingAshlars: defineMedia({
    id: 'crane-lifting-ashlars', path: '/dataset/lifting/crane-lifting-ashlars.jpg',
    kind: 'lifting', tags: ['crane-hook', 'workers', 'lifting-workface', 'no-hard-hat'], license: 'CC-BY-SA-3.0',
  }),
  towerCraneAnemometer: defineMedia({
    id: 'tower-crane-anemometer', path: '/dataset/equipment/tower-crane-anemometer.jpg',
    kind: 'equipment', tags: ['tower-crane', 'cabin', 'cup-anemometer'], license: 'CC-BY-SA-4.0',
  }),
  constructionSiteEntrance: defineMedia({
    id: 'construction-site-entrance', path: '/dataset/access-control/construction-site-entrance.jpg',
    kind: 'access-control', tags: ['construction-entrance', 'camera', 'safety-signage'], license: 'CC-BY-SA-3.0',
  }),
  restrictedConstructionFence: defineMedia({
    id: 'restricted-construction-fence', path: '/dataset/access-control/restricted-construction-fence.jpg',
    kind: 'access-control', tags: ['construction-fence', 'no-entry-sign', 'people'], license: 'CC-BY-2.0',
  }),
  siteGatePedestrians: defineMedia({
    id: 'site-gate-pedestrians', path: '/dataset/access-control/site-gate-pedestrians.jpg',
    kind: 'access-control', tags: ['site-hoarding', 'gate', 'pedestrians', 'no-hard-hat-visitors'], license: 'CC-BY-SA-3.0',
  }),
  siteFenceWarningSign: defineMedia({
    id: 'site-fence-warning-sign', path: '/dataset/access-control/site-fence-warning-sign.jpg',
    kind: 'access-control', tags: ['construction-fence', 'no-entry-sign', 'tower-crane', 'rebar-stacks'], license: 'CC-BY-SA-4.0',
  }),
  siteYardTowerCranes: defineMedia({
    id: 'site-yard-tower-cranes', path: '/dataset/construction/site-yard-tower-cranes.jpg',
    kind: 'construction', tags: ['tower-crane', 'site-yard', 'fence', 'machinery'], license: 'CC-BY-SA-4.0',
  }),
  girderHeavyLift: defineMedia({
    id: 'girder-heavy-lift', path: '/dataset/lifting/girder-heavy-lift.jpg',
    kind: 'lifting', tags: ['crawler-crane', 'concrete-girder', 'heavy-load'], license: 'CC-BY-2.0',
  }),
  angledGirderRigging: defineMedia({
    id: 'angled-girder-rigging', path: '/dataset/lifting/angled-girder-rigging.jpg',
    kind: 'lifting', tags: ['crane-hook', 'angled-rigging', 'concrete-girder', 'dusk'], license: 'CC-BY-2.0',
  }),
  girderLandingZone: defineMedia({
    id: 'girder-landing-zone', path: '/dataset/lifting/girder-landing-zone.jpg',
    kind: 'lifting', tags: ['suspended-girder', 'workers', 'landing-zone', 'cranes'], license: 'CC-BY-2.0',
  }),
  rebarDeckCrew: defineMedia({
    id: 'rebar-deck-crew', path: '/dataset/ppe/rebar-deck-crew.jpg',
    kind: 'ppe', tags: ['construction-workers', 'hard-hat', 'rebar-deck', 'tower-crane'], license: 'CC-BY-SA-3.0',
  }),
})

export const CONSTRUCTION_MEDIA_IDS = Object.freeze([
  'towerCraneAerial01', 'towerCraneAerial02', 'mobileCraneE16',
  'mobileCranePrecastWall', 'liebherrLtm1500Genie',
])
export const PPE_MEDIA_IDS = Object.freeze([
  'ppeHelmet0014', 'ppeSite0517', 'ppeSite0637', 'ppeSite0675', 'ppeSite0701', 'ppeSite0803',
])
export const VIOLATION_MEDIA_IDS = Object.freeze(['workerWithoutPpe', 'unsafeCraneParking'])
export const LIFTING_MEDIA_IDS = Object.freeze([
  'drywallCraneWorksite', 'heavyLoadLift', 'trenchBoxGuidance',
  'improperEyebolt', 'craneHookGuidance', 'craneLiftingAshlars',
  'girderHeavyLift', 'angledGirderRigging', 'girderLandingZone',
])
export const EQUIPMENT_MEDIA_IDS = Object.freeze(['towerCraneAnemometer'])
export const ACCESS_CONTROL_MEDIA_IDS = Object.freeze([
  'constructionSiteEntrance', 'restrictedConstructionFence',
  'siteGatePedestrians', 'siteFenceWarningSign',
])

// Compatibility exports retained for existing pages and external demo code.
export const PEOPLE_MEDIA_IDS = Object.freeze(['workerWithoutPpe', 'ppeSite0637', 'ppeSite0675', 'craneLiftingAshlars'])
export const SITE_MEDIA_IDS = Object.freeze(['towerCraneAerial01', 'towerCraneAerial02', 'constructionSiteEntrance'])
export const NO_FALL_PROTECTION_ID = 'ppeSite0701'

export const mediaById = (id, fallback = 'towerCraneAerial01') => (
  DEMO_MEDIA[id] || DEMO_MEDIA[fallback]
)

export const mediaPath = (id, fallback = 'towerCraneAerial01') => (
  mediaById(id, fallback).path
)

const defineEvidence = (mediaId, evidenceMode, evidenceLabel, sourceNode, note) => Object.freeze({
  mediaId, evidenceMode, evidenceLabel, sourceNode, note,
})

export const RISK_EVIDENCE_BY_TYPE = Object.freeze({
  违规闯入: defineEvidence(
    'siteGatePedestrians', 'overlay-assisted', '电子围栏联动', 'FENCE_AI_NODE_02',
    '工地围挡与闸口处有人员靠近逗留，围挡、闸口和人员在画面中可见；越界关系由演示电子围栏叠加确定。',
  ),
  超载起吊: defineEvidence(
    'girderHeavyLift', 'sensor-context', '载荷传感器联动', 'LOAD_SENSOR_CR-02',
    '履带吊正在起吊大型预制梁，重载吊装场景可见；是否超过额定载荷由确定性演示载荷遥测判定。',
  ),
  未佩戴安全帽: defineEvidence(
    'workerWithoutPpe', 'direct-visual', '视觉识别证据', 'PPE_VISION_NODE_01',
    '高处作业人员未佩戴安全帽且缺少个人防护装备，关键事实可直接观察。',
  ),
  违章操作: defineEvidence(
    'unsafeCraneParking', 'direct-visual', '现场巡检证据', 'SAFETY_AUDIT_NODE_01',
    'NIOSH 图片直接展示重型设备处于危险垫高和停放状态。',
  ),
  斜拉斜吊: defineEvidence(
    'angledGirderRigging', 'sensor-context', '吊钩姿态传感器联动', 'HOOK_POSE_SENSOR_02',
    '吊钩与索具带载呈明显倾斜姿态，梁体斜置于画面中；斜拉角度由吊钩姿态与摆角遥测判定。',
  ),
  设备离线: defineEvidence(
    'constructionSiteEntrance', 'sensor-context', '设备心跳联动', 'HEARTBEAT_GATEWAY_01',
    '入口摄像头和工地环境可见；离线结论来自设备心跳而不是静态照片。',
  ),
  大风超阈值起吊: defineEvidence(
    'towerCraneAnemometer', 'sensor-context', '风速传感器联动', 'ANEMOMETER_TC-04',
    '塔吊驾驶室和杯式风速仪可见；风速是否超阈值由演示传感器读数判定。',
  ),
  吊物下方站人: defineEvidence(
    'girderLandingZone', 'overlay-assisted', '吊装危险区联动', 'LIFTING_ZONE_VISION_01',
    '预制梁悬吊于落梁区上方，多名作业人员位于吊物邻近区域；进入关系由演示危险区叠加确定。',
  ),
  未系安全带: defineEvidence(
    'ppeSite0701', 'direct-visual', '视觉识别证据', 'PPE_VISION_NODE_02',
    '高处作业人员未使用适当防坠设备，关键事实可直接观察。',
  ),
  限位失效: defineEvidence(
    'towerCraneAnemometer', 'sensor-context', '限位传感器联动', 'LIMIT_SWITCH_TC-04',
    '照片提供塔吊控制设备场景；限位开关状态只能由传感器和控制器诊断确定。',
  ),
})

export const ALARM_EVIDENCE_BY_TYPE = Object.freeze({
  person_in_rotation_radius: defineEvidence(
    'craneLiftingAshlars', 'overlay-assisted', '回转半径雷视联动', 'RADAR_VISION_FUSION_03',
    '人员、吊钩和吊装作业面可见；是否进入回转半径由雷达与演示区域叠加确定。',
  ),
  overload_risk: RISK_EVIDENCE_BY_TYPE.超载起吊,
  device_offline: RISK_EVIDENCE_BY_TYPE.设备离线,
  cross_fence: RISK_EVIDENCE_BY_TYPE.违规闯入,
  no_helmet: RISK_EVIDENCE_BY_TYPE.未佩戴安全帽,
})

const DEFAULT_EVIDENCE = defineEvidence(
  'towerCraneAerial01', 'sensor-context', '场景参考', 'DEMO_CONTEXT_NODE',
  '该图片只提供施工现场上下文，具体事件结论以演示业务数据为准。',
)

const RISK_TYPE_ALIASES = Object.freeze({
  人员违规闯入: '违规闯入',
  安全帽未佩戴: '未佩戴安全帽',
  违规超载告警: '超载起吊',
  周界越界: '违规闯入',
})

const hydrateEvidence = (evidence) => {
  const media = mediaById(evidence.mediaId)
  return Object.freeze({
    ...evidence,
    media,
    path: media.path,
    alt: `${evidence.evidenceLabel}：${media.tags.join('、')}`,
    captureLabel: evidence.evidenceMode === 'sensor-context' ? '遥测快照' : '证据帧',
    modeLabel: {
      'direct-visual': '画面直接可见',
      'overlay-assisted': '区域叠加辅助',
      'sensor-context': '传感器场景联动',
    }[evidence.evidenceMode],
  })
}

export const riskEvidenceFor = (type = '') => {
  const raw = String(type || '').trim()
  const normalized = RISK_TYPE_ALIASES[raw] || raw
  return hydrateEvidence(RISK_EVIDENCE_BY_TYPE[normalized] || DEFAULT_EVIDENCE)
}

export const alarmEvidenceFor = (type = '') => (
  hydrateEvidence(ALARM_EVIDENCE_BY_TYPE[String(type || '').trim()] || DEFAULT_EVIDENCE)
)

export const riskMediaPath = (type = '') => riskEvidenceFor(type).path
