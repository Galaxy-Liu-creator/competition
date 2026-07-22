import request from './request'
export const getDashboardOverview=()=>request.get('/api/dashboard/overview')
export const getMapOverview=(siteId='site-001')=>request.get(`/api/sites/${siteId}/map-overview`)
