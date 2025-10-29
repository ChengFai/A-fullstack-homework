import axios from 'axios'
import { store } from '../store'
import { logoutUser } from '../store/slices/authSlice'

export const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    ;(config.headers as any)['Authorization'] = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      // 使用Redux dispatch来登出用户
      store.dispatch(logoutUser())
    }
    return Promise.reject(err)
  }
)


