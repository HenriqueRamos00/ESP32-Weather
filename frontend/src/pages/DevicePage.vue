<script setup lang="ts">
import { useDeviceStore } from '@/stores/deviceStore'
import DeviceCard from '@/components/DeviceCard.vue'
import { useRouter } from 'vue-router'

const store = useDeviceStore()
const router = useRouter()
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Devices</h1>
        <p class="text-slate-400 text-sm">Manage your ESP boards</p>
      </div>
      <button
        @click="router.push({ name: 'DeviceAdd' })"
        class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded flex items-center gap-2"
      >
        <span>+</span> Add Board
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <DeviceCard v-for="device in store.devices" :key="device.id" :device="device" />
    </div>
  </div>
</template>
