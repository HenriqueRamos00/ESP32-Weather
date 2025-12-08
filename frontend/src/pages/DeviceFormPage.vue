<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDeviceStore, type Device } from '@/stores/deviceStore'

const route = useRoute()
const router = useRouter()
const store = useDeviceStore()

const isEditing = computed(() => route.params.id !== undefined)
const deviceId = route.params.id as string

// Form State
const formData = ref({
  type: 'ESP32',
  location: '',
  status: 'offline' as 'online' | 'offline', // Default for new
  lastSeen: 'Never',
})

// Modal State
const showKeyModal = ref(false)
const generatedKey = ref('')

onMounted(() => {
  if (isEditing.value) {
    const existing = store.getDeviceById(deviceId)
    if (existing) {
      formData.value = { ...existing }
    }
  }
})

const handleSave = () => {
  if (isEditing.value) {
    store.updateDevice({ ...formData.value, id: deviceId } as Device)
  } else {
    store.addDevice({ ...formData.value } as Device)
  }
  router.push({ name: 'Devices' })
}

const handleDelete = () => {
  if (confirm('Are you sure you want to delete this device?')) {
    store.deleteDevice(deviceId)
    router.push({ name: 'Devices' })
  }
}

const generateApiKey = () => {
  // Mock Key Generation
  generatedKey.value = 'sk_esp32_' + Math.random().toString(36).substring(2, 15)
  showKeyModal.value = true
}

const copyToClipboard = () => {
  navigator.clipboard.writeText(generatedKey.value)
  alert('API Key copied!')
  showKeyModal.value = false
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">{{ isEditing ? 'Edit Device' : 'Add New Device' }}</h1>
      <button @click="router.back()" class="text-slate-400 hover:text-white">Cancel</button>
    </div>

    <div class="bg-slate-800 p-6 rounded-lg shadow border border-slate-700 space-y-4">
      <div>
        <label class="block text-slate-400 mb-1 text-sm">Board Type</label>
        <select
          v-model="formData.type"
          class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
        >
          <option value="ESP32">ESP32</option>
          <option value="ESP8266">ESP8266</option>
          <option value="ESP32-S3">ESP32-S3</option>
        </select>
      </div>

      <div>
        <label class="block text-slate-400 mb-1 text-sm">Location</label>
        <input
          v-model="formData.location"
          type="text"
          placeholder="e.g. Kitchen"
          class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
        />
      </div>

      <div class="pt-4 flex flex-col gap-3">
        <button
          type="button"
          @click="generateApiKey"
          class="w-full border border-yellow-600 text-yellow-500 hover:bg-yellow-600/10 py-2 rounded transition-colors text-sm"
        >
          Generate API Key
        </button>

        <div class="flex gap-3 mt-4">
          <button
            @click="handleSave"
            class="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded font-medium"
          >
            {{ isEditing ? 'Save Changes' : 'Create Device' }}
          </button>

          <button
            v-if="isEditing"
            @click="handleDelete"
            class="px-4 bg-red-600/20 hover:bg-red-600/40 text-red-500 border border-red-600/50 rounded"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showKeyModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
    >
      <div class="bg-slate-800 p-6 rounded-lg shadow-xl max-w-sm w-full border border-slate-600">
        <h3 class="text-lg font-bold mb-2">New API Key</h3>
        <p class="text-slate-400 text-sm mb-4">Copy this key now. You won't see it again.</p>

        <div
          class="bg-slate-900 p-3 rounded font-mono text-sm break-all mb-4 text-emerald-400 border border-slate-700"
        >
          {{ generatedKey }}
        </div>

        <div class="flex justify-end gap-2">
          <button @click="showKeyModal = false" class="text-slate-400 hover:text-white px-3 py-1">
            Close
          </button>
          <button
            @click="copyToClipboard"
            class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded text-sm"
          >
            Copy & Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
