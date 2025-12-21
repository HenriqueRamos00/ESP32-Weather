<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push({ name: 'Dashboard' })
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 px-4">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-sky-500 mb-4">404</h1>
      <h2 class="text-3xl font-semibold text-white mb-4">Page Not Found</h2>
      <p class="text-slate-400 mb-8 max-w-md">
        The page you're looking for doesn't exist or has been moved.
      </p>

      <div class="flex gap-4 justify-center">
        <button
          @click="goBack"
          class="px-6 py-3 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-medium border border-slate-700 transition-colors"
        >
          Go Back
        </button>
        <button
          @click="goHome"
          class="px-6 py-3 rounded-md bg-sky-600 hover:bg-sky-700 text-white font-medium transition-colors"
        >
          Go to Dashboard
        </button>
      </div>
    </div>
  </div>
</template>
