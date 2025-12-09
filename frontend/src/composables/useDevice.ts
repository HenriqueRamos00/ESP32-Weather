import { ref, readonly } from 'vue'
import {
  deviceService,
  type Device,
  type DeviceCreate,
  type DeviceUpdate,
} from '@/services/deviceService'
import { apiKeyService, type ApiKey, type ApiKeyWithSecret } from '@/services/apiKeyService'

export function useDevice() {
  const device = ref<Device | null>(null)
  const apiKeys = ref<ApiKey[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchDevice = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      device.value = await deviceService.getById(id)
      return device.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch device'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createDevice = async (deviceData: DeviceCreate) => {
    loading.value = true
    error.value = null
    try {
      const newDevice = await deviceService.create(deviceData)
      device.value = newDevice
      return newDevice
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create device'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateDevice = async (id: number, deviceData: DeviceUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedDevice = await deviceService.update(id, deviceData)
      device.value = updatedDevice
      return updatedDevice
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update device'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDevice = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await deviceService.delete(id)
      device.value = null
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete device'
      throw err
    } finally {
      loading.value = false
    }
  }

  // API Keys
  const fetchApiKeys = async (deviceId: number) => {
    try {
      const response = await apiKeyService.getByDeviceId(deviceId)
      apiKeys.value = response.api_keys
      return response.api_keys
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch API keys'
      throw err
    }
  }

  const generateApiKey = async (deviceId: number, name: string): Promise<ApiKeyWithSecret> => {
    try {
      const newKey = await apiKeyService.create({ device_id: deviceId, name })
      apiKeys.value.push(newKey)
      return newKey
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to generate API key'
      throw err
    }
  }

  const revokeApiKey = async (keyId: number) => {
    try {
      const revokedKey = await apiKeyService.revoke(keyId)
      const index = apiKeys.value.findIndex((k) => k.id === keyId)
      if (index !== -1) {
        apiKeys.value[index] = revokedKey
      }
      return revokedKey
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to revoke API key'
      throw err
    }
  }

  const deleteApiKey = async (keyId: number) => {
    try {
      await apiKeyService.delete(keyId)
      apiKeys.value = apiKeys.value.filter((k) => k.id !== keyId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete API key'
      throw err
    }
  }

  const clearDevice = () => {
    device.value = null
    apiKeys.value = []
    error.value = null
  }

  const clearError = () => {
    error.value = null
  }

  return {
    device: readonly(device),
    apiKeys: readonly(apiKeys),
    loading: readonly(loading),
    error: readonly(error),
    fetchDevice,
    createDevice,
    updateDevice,
    deleteDevice,
    fetchApiKeys,
    generateApiKey,
    revokeApiKey,
    deleteApiKey,
    clearDevice,
    clearError,
  }
}
