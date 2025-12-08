<script setup lang="ts">
import type { Device } from '@/stores/deviceStore'
import { useRouter } from 'vue-router'

const props = defineProps<{
  device: Device
}>()

const router = useRouter()

const navigateToEdit = () => {
  router.push({ name: 'DeviceEdit', params: { id: props.device.id } })
}
</script>

<template>
  <div
    class="bg-slate-800 rounded-lg p-5 shadow-lg border border-slate-700 flex flex-col justify-between"
  >
    <div>
      <div class="flex justify-between items-start mb-4">
        <div>
          <h3 class="font-bold text-lg text-white">{{ device.location }}</h3>
          <span class="text-sm text-slate-400">{{ device.type }}</span>
        </div>
        <div class="flex items-center gap-2 bg-slate-900 px-2 py-1 rounded-full text-xs">
          <span
            class="w-2 h-2 rounded-full"
            :class="device.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'"
          ></span>
          <span :class="device.status === 'online' ? 'text-emerald-500' : 'text-red-500'">
            {{ device.status.toUpperCase() }}
          </span>
        </div>
      </div>

      <div class="text-sm text-slate-400 mb-6">
        <p>Last Seen:</p>
        <p class="text-slate-200">{{ device.lastSeen }}</p>
      </div>
    </div>

    <button
      @click="navigateToEdit"
      class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded transition-colors text-sm font-medium"
    >
      Update Info
    </button>
  </div>
</template>
