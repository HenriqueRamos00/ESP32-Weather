<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDevice } from '@/composables/useDevice'
import { useToast } from '@/composables/useToast'
import type { DeviceCreate, DeviceUpdate } from '@/services/deviceService'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import ApiKeyModal from '@/components/ApiKeyModal.vue'

const route = useRoute()
const router = useRouter()
const {
  apiKeys,
  loading,
  fetchDevice,
  createDevice,
  updateDevice,
  deleteDevice,
  fetchApiKeys,
  generateApiKey,
  revokeApiKey,
  deleteApiKey,
  clearDevice,
} = useDevice()
const { success, error: showError } = useToast()

const isEditing = computed(() => route.params.id !== undefined)
const deviceId = computed(() => Number(route.params.id))

// Form State
const formData = ref<DeviceCreate>({
  type: 'ESP32',
  location: '',
  function: 'sensor',
})

// UI State
const saving = ref(false)
const initialLoading = ref(false)
const showDeleteModal = ref(false)
const showApiKeyModal = ref(false)
const generatedApiKey = ref('')
const apiKeyName = ref('')
const showApiKeyNameModal = ref(false)

onMounted(async () => {
  if (isEditing.value) {
    initialLoading.value = true
    try {
      const fetchedDevice = await fetchDevice(deviceId.value)
      if (fetchedDevice) {
        formData.value = {
          type: fetchedDevice.type,
          location: fetchedDevice.location,
          function: fetchedDevice.function,
        }
        await fetchApiKeys(deviceId.value)
      }
    } catch (err) {
      showError('Failed to load device', err instanceof Error ? err.message : undefined)
      router.push({ name: 'Devices' })
    } finally {
      initialLoading.value = false
    }
  }
})

onUnmounted(() => {
  clearDevice()
})

const handleSave = async () => {
  if (!formData.value.location.trim()) {
    showError('Validation Error', 'Location is required')
    return
  }

  saving.value = true
  try {
    if (isEditing.value) {
      const updateData: DeviceUpdate = {
        type: formData.value.type,
        location: formData.value.location,
        function: formData.value.function,
      }
      await updateDevice(deviceId.value, updateData)
      success('Device Updated', 'Your device has been updated successfully')
    } else {
      await createDevice(formData.value)
      success('Device Created', 'Your new device has been added')
    }
    router.push({ name: 'Devices' })
  } catch (err) {
    showError(
      isEditing.value ? 'Update Failed' : 'Creation Failed',
      err instanceof Error ? err.message : undefined,
    )
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  showDeleteModal.value = false
  saving.value = true
  try {
    await deleteDevice(deviceId.value)
    success('Device Deleted', 'The device has been removed')
    router.push({ name: 'Devices' })
  } catch (err) {
    showError('Delete Failed', err instanceof Error ? err.message : undefined)
  } finally {
    saving.value = false
  }
}

const openApiKeyNameModal = () => {
  apiKeyName.value = `Key for ${formData.value.location || 'Device'}`
  showApiKeyNameModal.value = true
}

const handleGenerateApiKey = async () => {
  showApiKeyNameModal.value = false
  saving.value = true
  try {
    const result = await generateApiKey(deviceId.value, apiKeyName.value)
    generatedApiKey.value = result.key
    showApiKeyModal.value = true
    success('API Key Generated', 'Your new API key has been created')
  } catch (err) {
    showError('Failed to Generate API Key', err instanceof Error ? err.message : undefined)
  } finally {
    saving.value = false
  }
}

const handleRevokeKey = async (keyId: number) => {
  try {
    await revokeApiKey(keyId)
    success('API Key Revoked', 'The API key has been deactivated')
  } catch (err) {
    showError('Failed to Revoke', err instanceof Error ? err.message : undefined)
  }
}

const handleDeleteKey = async (keyId: number) => {
  try {
    await deleteApiKey(keyId)
    success('API Key Deleted', 'The API key has been removed')
  } catch (err) {
    showError('Failed to Delete', err instanceof Error ? err.message : undefined)
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <!-- Loading Overlay -->
    <div v-if="initialLoading" class="flex justify-center items-center py-20">
      <LoadingSpinner size="lg" />
    </div>

    <template v-else>
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold">{{ isEditing ? 'Edit Device' : 'Add New Device' }}</h1>
        <button @click="router.back()" class="text-slate-400 hover:text-white transition-colors">
          Cancel
        </button>
      </div>

      <div class="bg-slate-800 p-6 rounded-lg shadow border border-slate-700 space-y-4">
        <!-- Board Type -->
        <div>
          <label class="block text-slate-400 mb-1 text-sm">Board Type</label>
          <select
            v-model="formData.type"
            class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="ESP32">ESP32</option>
            <option value="ESP8266">ESP8266</option>
            <option value="ESP32-S3">ESP32-S3</option>
          </select>
        </div>

        <!-- Location -->
        <div>
          <label class="block text-slate-400 mb-1 text-sm">Location</label>
          <input
            v-model="formData.location"
            type="text"
            placeholder="e.g. Kitchen"
            class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        <!-- Function -->
        <div>
          <label class="block text-slate-400 mb-1 text-sm">Function</label>
          <select
            v-model="formData.function"
            class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="sensor">Sensor</option>
            <option value="display">Display</option>
          </select>
        </div>
        <!-- API Keys Section (Only for editing) -->
        <div v-if="isEditing" class="pt-4 border-t border-slate-700">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-white font-medium">API Keys</h3>
            <button
              @click="openApiKeyNameModal"
              :disabled="saving"
              class="text-sm text-yellow-500 hover:text-yellow-400 transition-colors disabled:opacity-50"
            >
              + Generate New Key
            </button>
          </div>

          <!-- Existing Keys -->
          <div v-if="apiKeys.length > 0" class="space-y-2 mb-4">
            <div
              v-for="key in apiKeys"
              :key="key.id"
              class="bg-slate-900 rounded p-3 flex items-center justify-between"
            >
              <div>
                <p class="text-white text-sm font-medium">{{ key.name }}</p>
                <p class="text-slate-500 text-xs">
                  Created: {{ new Date(key.created_at).toLocaleDateString() }}
                  <span v-if="key.last_used">
                    • Last used: {{ new Date(key.last_used).toLocaleDateString() }}
                  </span>
                </p>
              </div>
              <div class="flex items-center gap-2">
                <span
                  :class="[
                    'text-xs px-2 py-1 rounded',
                    key.is_active
                      ? 'bg-emerald-500/20 text-emerald-500'
                      : 'bg-red-500/20 text-red-500',
                  ]"
                >
                  {{ key.is_active ? 'Active' : 'Revoked' }}
                </span>
                <button
                  v-if="key.is_active"
                  @click="handleRevokeKey(key.id)"
                  class="text-yellow-500 hover:text-yellow-400 text-sm transition-colors"
                >
                  Revoke
                </button>
                <button
                  @click="handleDeleteKey(key.id)"
                  class="text-red-500 hover:text-red-400 text-sm transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>

          <p v-else class="text-slate-500 text-sm">No API keys generated yet</p>
        </div>

        <!-- Action Buttons -->
        <div class="pt-4 flex flex-col gap-3">
          <div class="flex gap-3">
            <button
              @click="handleSave"
              :disabled="saving || loading"
              class="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white py-2 rounded font-medium transition-colors flex items-center justify-center gap-2"
            >
              <LoadingSpinner v-if="saving" size="sm" />
              {{ isEditing ? 'Save Changes' : 'Create Device' }}
            </button>

            <button
              v-if="isEditing"
              @click="showDeleteModal = true"
              :disabled="saving || loading"
              class="px-4 bg-red-600/20 hover:bg-red-600/40 disabled:opacity-50 text-red-500 border border-red-600/50 rounded transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Modal -->
    <ConfirmModal
      :show="showDeleteModal"
      title="Delete Device"
      message="Are you sure you want to delete this device? This action cannot be undone and will also delete all associated API keys."
      confirm-text="Delete"
      variant="danger"
      @confirm="handleDelete"
      @cancel="showDeleteModal = false"
    />

    <!-- API Key Name Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showApiKeyNameModal"
          class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
          @click.self="showApiKeyNameModal = false"
        >
          <div
            class="bg-slate-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4 border border-slate-600"
          >
            <h3 class="text-lg font-bold text-white mb-4">Generate API Key</h3>

            <div class="mb-4">
              <label class="block text-slate-400 mb-1 text-sm">Key Name</label>
              <input
                v-model="apiKeyName"
                type="text"
                placeholder="e.g. Production Key"
                class="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
                @keyup.enter="handleGenerateApiKey"
              />
              <p class="text-slate-500 text-xs mt-1">A descriptive name to identify this key</p>
            </div>

            <div class="flex justify-end gap-3">
              <button
                @click="showApiKeyNameModal = false"
                class="px-4 py-2 text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                @click="handleGenerateApiKey"
                :disabled="!apiKeyName.trim()"
                class="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 text-white rounded transition-colors"
              >
                Generate
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- API Key Display Modal -->
    <ApiKeyModal
      :show="showApiKeyModal"
      :api-key="generatedApiKey"
      @close="showApiKeyModal = false"
    />
  </div>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
