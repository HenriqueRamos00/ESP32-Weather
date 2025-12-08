// stores/deviceStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Device {
  id: string
  type: 'ESP32' | 'ESP8266' | 'ESP32-S3' // Example types
  location: string
  status: 'online' | 'offline'
  lastSeen: string
}

export const useDeviceStore = defineStore('devices', () => {
  // Mock Data
  const devices = ref<Device[]>([
    {
      id: '1',
      type: 'ESP32',
      location: 'Living Room',
      status: 'online',
      lastSeen: '2023-10-27 10:30',
    },
    {
      id: '2',
      type: 'ESP32-S3',
      location: 'Garden',
      status: 'offline',
      lastSeen: '2023-10-26 14:00',
    },
  ])

  // Actions
  function addDevice(device: Omit<Device, 'id'>) {
    const newId = (Math.random() * 10000).toFixed(0) // Mock ID generation
    devices.value.push({ ...device, id: newId })
  }

  function updateDevice(updatedDevice: Device) {
    const index = devices.value.findIndex((d) => d.id === updatedDevice.id)
    if (index !== -1) devices.value[index] = updatedDevice
  }

  function deleteDevice(id: string) {
    devices.value = devices.value.filter((d) => d.id !== id)
  }

  function getDeviceById(id: string) {
    return devices.value.find((d) => d.id === id)
  }

  return { devices, addDevice, updateDevice, deleteDevice, getDeviceById }
})
