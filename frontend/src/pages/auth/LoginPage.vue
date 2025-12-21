<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const email = ref('')
const password = ref('')

const router = useRouter()
const route = useRoute()
const { login, loading, error: authError } = useAuth()

async function onSubmit() {
  if (loading.value) return

  try {
    await login(email.value, password.value)

    // Redirect to original target or default to '/'
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    // Error is already set by useAuth
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900">
    <div class="bg-slate-800 p-8 rounded-xl shadow-lg w-full max-w-sm">
      <!-- Logo and Icon -->
      <div class="flex flex-col items-center mb-8">
        <svg
          class="w-16 h-16 text-sky-400 mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"
          />
        </svg>
        <h1 class="text-2xl font-bold text-white">Weather App</h1>
        <p class="text-sm text-slate-400 mt-1">Sign in to your account</p>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div v-if="authError" class="text-sm text-red-400 bg-red-950/40 px-3 py-2 rounded">
          {{ authError }}
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
          <span v-else>Signing in...</span>
        </button>
      </form>
    </div>
  </div>
</template>
