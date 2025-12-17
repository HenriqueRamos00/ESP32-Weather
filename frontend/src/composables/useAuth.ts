import { ref, readonly } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/authService'
import type { ApiError } from '@/services/api'

export function useAuth() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const authStore = useAuthStore()

  const login = async (email: string, password: string) => {
    loading.value = true
    error.value = null
    try {
      const data = await authService.login(email, password)
      authStore.setToken(data.access_token)
      return data
    } catch (e) {
      const apiErr = e as ApiError
      error.value = apiErr.message || 'Login failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    authStore.clearAuth()
  }

  const clearError = () => {
    error.value = null
  }

  return {
    login,
    logout,
    loading: readonly(loading),
    error: readonly(error),
    clearError,
  }
}
