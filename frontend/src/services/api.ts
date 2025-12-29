import axios, { type AxiosError, type AxiosResponse } from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const status = error.response?.status

    if (status === 401) {
      const authStore = useAuthStore()
      authStore.clearAuth()

      if (router.currentRoute.value.name !== 'Login') {
        router.push({
          name: 'Login',
          query: { redirect: router.currentRoute.value.fullPath },
        })
      }
    }

    const message = extractErrorMessage(error)
    return Promise.reject(new ApiError(message, status))
  },
)

function extractErrorMessage(error: AxiosError): string {
  if (error.response?.data) {
    const data = error.response.data as Record<string, unknown>
    if (typeof data.detail === 'string') {
      return data.detail
    }
    if (typeof data.message === 'string') {
      return data.message
    }
  }
  if (error.message) return error.message
  return 'An unexpected error occurred'
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
