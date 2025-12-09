<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useDevices } from '@/composables/useDevices'
import { useToast } from '@/composables/useToast'
import DeviceCard from '@/components/DeviceCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { useRouter } from 'vue-router'

const { devices, total, loading, error, fetchDevices } = useDevices()
const router = useRouter()
const { error: showError } = useToast()

const initialLoading = ref(true)

onMounted(async () => {
  try {
    await fetchDevices()
  } catch (err) {
    showError('Failed to load devices', err instanceof Error ? err.message : undefined)
  } finally {
    initialLoading.value = false
  }
})

const handleRetry = async () => {
  try {
    await fetchDevices()
  } catch (err) {
    showError('Failed to load devices', err instanceof Error ? err.message : undefined)
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Devices</h1>
        <p class="text-slate-400 text-sm">
          Manage your ESP boards
          <span v-if="total > 0" class="text-slate-500">({{ total }} total)</span>
        </p>
      </div>
      <button
        @click="router.push({ name: 'DeviceAdd' })"
        class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded flex items-center gap-2 transition-colors"
      >
        <span>+</span> Add Board
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="initialLoading" class="flex justify-center items-center py-20">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error State -->
    <div
      v-else-if="error && devices.length === 0"
      class="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-center"
    >
      <p class="text-red-400 mb-4">{{ error }}</p>
      <button
        @click="handleRetry"
        :disabled="loading"
        class="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
      >
        Retry
      </button>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="devices.length === 0"
      class="bg-slate-800 rounded-lg p-12 text-center border border-slate-700"
    >
      <div class="text-4xl mb-4">📡</div>
      <h3 class="text-lg font-medium text-white mb-2">No devices yet</h3>
      <p class="text-slate-400 mb-6">Get started by adding your first ESP board</p>
      <button
        @click="router.push({ name: 'DeviceAdd' })"
        class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded transition-colors"
      >
        Add Your First Device
      </button>
    </div>

    <!-- Device Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <DeviceCard v-for="device in devices" :key="device.id" :device="device" />
    </div>
  </div>
</template>
