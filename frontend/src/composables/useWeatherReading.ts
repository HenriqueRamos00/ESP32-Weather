import { ref, readonly } from 'vue'
import {
  weatherReadingService,
  type WeatherReading,
  type WeatherReadingWithLocation,
  type LatestReadingsResponse,
  type WeatherSummary,
  type DateLike,
} from '@/services/weatherReadingService'

export function useWeatherReadings() {
  const readings = ref<WeatherReading[]>([])
  const total = ref(0)

  const latestReadings = ref<WeatherReadingWithLocation[]>([])
  const latestFetchedAt = ref<string | null>(null)

  const summary = ref<WeatherSummary | null>(null)

  const loading = ref(false)
  const error = ref<string | null>(null)

  const clearError = () => {
    error.value = null
  }

  const fetchAllReadings = async (params?: {
    skip?: number
    limit?: number
    start_time?: DateLike
    end_time?: DateLike
  }) => {
    loading.value = true
    error.value = null
    try {
      const response = await weatherReadingService.getAll(params)
      readings.value = response.readings
      total.value = response.total
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch readings'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchLatestForDisplay = async (): Promise<LatestReadingsResponse> => {
    loading.value = true
    error.value = null
    try {
      const response = await weatherReadingService.getLatestForDisplay()
      latestReadings.value = response.readings
      latestFetchedAt.value = response.fetched_at
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch latest readings'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSensorLatest = async (deviceId: number) => {
    loading.value = true
    error.value = null
    try {
      return await weatherReadingService.getSensorLatest(deviceId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch latest sensor reading'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSensorHistory = async (
    deviceId: number,
    params?: {
      skip?: number
      limit?: number
      start_time?: DateLike
      end_time?: DateLike
    },
  ) => {
    loading.value = true
    error.value = null
    try {
      const response = await weatherReadingService.getSensorHistory(deviceId, params)
      readings.value = response.readings
      total.value = response.total
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch sensor history'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSensorSummary = async (deviceId: number, hours = 24) => {
    loading.value = true
    error.value = null
    try {
      const response = await weatherReadingService.getSensorSummary(deviceId, hours)
      summary.value = response
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch sensor summary'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    readings: readonly(readings),
    total: readonly(total),

    latestReadings: readonly(latestReadings),
    latestFetchedAt: readonly(latestFetchedAt),

    summary: readonly(summary),

    loading: readonly(loading),
    error: readonly(error),

    fetchAllReadings,
    fetchLatestForDisplay,
    fetchSensorLatest,
    fetchSensorHistory,
    fetchSensorSummary,
    clearError,
  }
}
