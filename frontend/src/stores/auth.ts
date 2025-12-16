import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export type UserRole = 'admin' | 'user'

export interface AuthUser {
  id: number
  email: string
  full_name: string | null
  role: UserRole
}

interface JwtPayload {
  sub: string
  exp: number
  role?: UserRole
  full_name?: string | null
  email?: string
}

function decodeJwt(token: string): JwtPayload | null {
  try {
    const payloadPart = token.split('.')[1]
    if (!payloadPart) {
      return null
    }

    const decoded = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded) as JwtPayload
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<AuthUser | null>(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('auth_token', newToken)

    const payload = decodeJwt(newToken)
    if (!payload || !payload.exp || payload.exp * 1000 < Date.now()) {
      clearAuth()
      return
    }

    user.value = {
      id: Number(payload.sub),
      email: payload.email ?? '',
      full_name: payload.full_name ?? null,
      role: payload.role ?? 'user',
    }
  }

  function initFromStorage() {
    if (initialized.value) return
    initialized.value = true

    const stored = localStorage.getItem('auth_token')
    if (!stored) return

    const payload = decodeJwt(stored)
    if (!payload || !payload.exp || payload.exp * 1000 < Date.now()) {
      clearAuth()
      return
    }

    token.value = stored
    user.value = {
      id: Number(payload.sub),
      email: payload.email ?? '',
      full_name: payload.full_name ?? null,
      role: payload.role ?? 'user',
    }
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    token,
    user,
    isAuthenticated,
    initialized,
    setToken,
    initFromStorage,
    clearAuth,
  }
})
