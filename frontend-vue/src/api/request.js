import axios from 'axios'

const request = axios.create({ baseURL: '', timeout: 8000 })

// 请求:注入 JWT
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('qa-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应:剥离 {code,message,data} 包装;401 统一登出跳登录页
request.interceptors.response.use(
  (res) => res.data?.data ?? res.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('qa-token')
      localStorage.removeItem('qa-user')
      if (!location.pathname.startsWith('/login')) {
        location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default request
