<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiClient } from '@/services/api'
import type { ApiError } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref<string | null>(null)

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

async function onSubmit() {
  if (loading.value) return
  loading.value = true
  errorMessage.value = null

  try {
    const { data } = await apiClient.post('/auth/login', {
      email: email.value,
      password: password.value,
    })

    // Backend returns: { access_token: string, token_type: "bearer" }
    authStore.setToken(data.access_token)

    // Redirect to original target or default to '/'
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err) {
    const apiErr = err as ApiError
    errorMessage.value = apiErr.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900">
    <div class="bg-slate-800 p-8 rounded-xl shadow-lg w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-white text-center">Login</h1>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div v-if="errorMessage" class="text-sm text-red-400 bg-red-950/40 px-3 py-2 rounded">
          {{ errorMessage }}
        </div>

        <div>
          <label class="block text-sm text-slate-300 mb-1" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <div>
          <label class="block text-sm text-slate-300 mb-1" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 rounded-md bg-sky-600 hover:bg-sky-700 text-white font-medium disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <span v-if="!loading">Sign in</span>
          <span v-else> Signing in... </span>
        </button>
      </form>
    </div>
  </div>
</template>
