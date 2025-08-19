import axios from 'axios'
import { useUserStore } from '../store'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.token
    
    // 添加防缓存头部
    config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    config.headers['Pragma'] = 'no-cache'
    config.headers['Expires'] = '0'
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除用户信息
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export const generateDocument = (reqId) => api.post(`/requirements/${reqId}/generate-document`);
export const exportPdf = (reqId) => api.get(`/requirements/${reqId}/export-pdf`, { responseType: 'blob' });
export const getDocumentVersions = (reqId) => api.get(`/requirements/${reqId}/documents`);
export const getDocumentByVersion = (reqId, version) => api.get(`/requirements/${reqId}/documents/${version}`);
export default api