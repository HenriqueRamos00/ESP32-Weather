import { ref, readonly } from 'vue'
import {
  deviceService,
  type Device,
  type DeviceCreate,
  type DeviceUpdate,
} from '@/services/deviceService'

export function useDevices() {
  const devices = ref<Device[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchDevices = async (skip = 0, limit = 100) => {
    loading.value = true
    error.value = null
    try {
      const response = await deviceService.getAll(skip, limit)
      devices.value = response.devices
      total.value = response.total
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch devices'
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
      devices.value.push(newDevice)
      total.value++
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
      const index = devices.value.findIndex((d) => d.id === id)
      if (index !== -1) {
        devices.value[index] = updatedDevice
      }
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
      devices.value = devices.value.filter((d) => d.id !== id)
      total.value--
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete device'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    devices: readonly(devices),
    total: readonly(total),
    loading: readonly(loading),
    error: readonly(error),
    fetchDevices,
    createDevice,
    updateDevice,
    deleteDevice,
    clearError,
  }
}
