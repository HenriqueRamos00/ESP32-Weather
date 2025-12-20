import { apiClient } from '@/services/api'

export interface Setting {
  key: string
  value: string
  description: string | null
}

export interface SettingUpdate {
  value: string
}

export const settingService = {
  async getAll(): Promise<Setting[]> {
    const { data } = await apiClient.get<Setting[]>('/settings/')
    return data
  },

  async getByKey(key: string): Promise<Setting> {
    const { data } = await apiClient.get<Setting>(`/settings/${key}`)
    return data
  },

  async update(key: string, settingData: SettingUpdate): Promise<Setting> {
    const { data } = await apiClient.put<Setting>(`/settings/${key}`, settingData)
    return data
  },
}
