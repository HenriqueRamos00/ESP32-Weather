import { apiClient, ApiError } from './api'

export interface ApiKey {
  id: number
  name: string
  device_id: number
  is_active: boolean
  last_used: string | null
  created_at: string
}

export interface ApiKeyWithSecret extends ApiKey {
  key: string
}

export interface ApiKeyCreate {
  name: string
  device_id: number
}

export interface ApiKeyListResponse {
  api_keys: ApiKey[]
  total: number
}

export const apiKeyService = {
  async getAll(skip = 0, limit = 100): Promise<ApiKeyListResponse> {
    try {
      const response = await apiClient.get<ApiKeyListResponse>('/api-keys', {
        params: { skip, limit },
      })
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to fetch API keys')
    }
  },

  async getByDeviceId(deviceId: number): Promise<ApiKeyListResponse> {
    try {
      const response = await apiClient.get<ApiKeyListResponse>(`/api-keys/device/${deviceId}`)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to fetch device API keys')
    }
  },

  async create(apiKey: ApiKeyCreate): Promise<ApiKeyWithSecret> {
    try {
      const response = await apiClient.post<ApiKeyWithSecret>('/api-keys', apiKey)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to create API key')
    }
  },

  async revoke(id: number): Promise<ApiKey> {
    try {
      const response = await apiClient.post<ApiKey>(`/api-keys/${id}/revoke`)
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to revoke API key')
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`/api-keys/${id}`)
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to delete API key')
    }
  },
}
