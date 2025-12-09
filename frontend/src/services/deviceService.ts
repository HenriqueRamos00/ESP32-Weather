import { apiClient, ApiError } from './api'

export interface Device {
  id: number
  type: 'ESP32' | 'ESP8266' | 'ESP32-S3'
  location: string
  function: 'sensor' | 'display'
  status: 'online' | 'offline'
  last_seen: string | null
  created_at: string
  updated_at: string
}

export interface DeviceCreate {
  type: 'ESP32' | 'ESP8266' | 'ESP32-S3'
  location: string
  function: 'sensor' | 'display'
}

export interface DeviceUpdate {
  type?: 'ESP32' | 'ESP8266' | 'ESP32-S3'
  location?: string
  function?: 'sensor' | 'display'
}

export interface DeviceListResponse {
  devices: Device[]
  total: number
}

export const deviceService = {
  async getAll(skip = 0, limit = 100): Promise<DeviceListResponse> {
    try {
      const response = await apiClient.get<DeviceListResponse>('/devices', {
        params: { skip, limit },
      })
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to fetch devices')
    }
  },

  async getById(id: number): Promise<Device> {
    try {
      const response = await apiClient.get<Device>(`/devices/${id}`)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to fetch device')
    }
  },

  async create(device: DeviceCreate): Promise<Device> {
    try {
      const response = await apiClient.post<Device>('/devices', device)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to create device')
    }
  },

  async update(id: number, device: DeviceUpdate): Promise<Device> {
    try {
      const response = await apiClient.put<Device>(`/devices/${id}`, device)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to update device')
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`/devices/${id}`)
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to delete device')
    }
  },
}
