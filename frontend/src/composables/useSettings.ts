import { ref, readonly } from 'vue'
import { settingService, type Setting, type SettingUpdate } from '@/services/settingService'

export function useSettings() {
  const settings = ref<Setting[]>([])
  const currentSetting = ref<Setting | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchSettings = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await settingService.getAll()
      settings.value = data
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch settings'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSetting = async (key: string) => {
    loading.value = true
    error.value = null
    try {
      const setting = await settingService.getByKey(key)
      currentSetting.value = setting
      return setting
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch setting'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSetting = async (key: string, settingData: SettingUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedSetting = await settingService.update(key, settingData)

      // Update in the settings array
      const index = settings.value.findIndex((s) => s.key === key)
      if (index !== -1) {
        settings.value[index] = updatedSetting
      }

      // Update current setting if it matches
      if (currentSetting.value?.key === key) {
        currentSetting.value = updatedSetting
      }

      return updatedSetting
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update setting'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentSetting = () => {
    currentSetting.value = null
  }

  return {
    settings: readonly(settings),
    currentSetting: readonly(currentSetting),
    loading: readonly(loading),
    error: readonly(error),
    fetchSettings,
    fetchSetting,
    updateSetting,
    clearError,
    clearCurrentSetting,
  }
}
