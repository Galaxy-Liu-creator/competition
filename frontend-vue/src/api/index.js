import request from './request'

// 通用 CRUD 工厂:后端列表返回 { list, total, page, page_size }
const crud = (base) => ({
  list: (params) => request.get(base, { params }),
  detail: (id) => request.get(`${base}/${id}`),
  create: (data) => request.post(base, data),
  update: (id, data) => request.put(`${base}/${id}`, data),
  remove: (id) => request.delete(`${base}/${id}`),
})

export const craneApi = crud('/api/cranes')
export const cameraApi = crud('/api/cameras')
export const nvrApi = crud('/api/nvrs')
export const speakerApi = crud('/api/speakers')
export const speakerLinkApi = {
  list: (params) => request.get('/api/speaker-links', { params }),
  create: (data) => request.post('/api/speaker-links', data),
  remove: (id) => request.delete(`/api/speaker-links/${id}`),
}
export const edgeBoxApi = crud('/api/edge-boxes')
export const radarApi = {
  ...crud('/api/radars'),
  readings: (id) => request.get(`/api/radars/${id}/readings`),
}
export const heartbeatApi = {
  list: (params) => request.get('/api/heartbeats', { params }),
}
export const deviceLinkApi = {
  list: (params) => request.get('/api/device-links', { params }),
  create: (data) => request.post('/api/device-links', data),
  remove: (id) => request.delete(`/api/device-links/${id}`),
}
export const deviceTypeApi = crud('/api/device-types')
export const riskEventApi = {
  ...crud('/api/risk-events'),
  handle: (id, data) => request.post(`/api/risk-events/${id}/handle`, data),
}
export const violationCategoryApi = crud('/api/violation-categories')
export const configApi = {
  // 后端返回 { key, value },保存需以 { value } 包裹
  get: (key) => request.get(`/api/configs/${key}`).then((data) => data?.value ?? data),
  save: (key, value) => request.put(`/api/configs/${key}`, { value }),
}
export const auditLogApi = {
  list: (params) => request.get('/api/audit-logs', { params }),
}
export const dashboardApi = {
  overview: () => request.get('/api/dashboard/overview'),
  stats: () => request.get('/api/dashboard/stats'),
  trend: () => request.get('/api/dashboard/trend'),
  categoryDistribution: () => request.get('/api/dashboard/category-distribution'),
  recentAlarms: () => request.get('/api/dashboard/recent-alarms'),
}
export const siteApi = {
  list: () => request.get('/api/sites'),
  mapOverview: (siteId = 'site-001') => request.get(`/api/sites/${siteId}/map-overview`),
}
