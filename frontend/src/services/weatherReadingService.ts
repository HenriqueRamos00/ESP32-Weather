import { apiClient, ApiError } from './api'

export type ISODateString = string
export type DateLike = string | Date | null | undefined

function toIso(value: DateLike): string | undefined {
  if (!value) return undefined
  return value instanceof Date ? value.toISOString() : value
}

export interface WeatherReading {
  id: number
  device_id: number
  temperature: number | null
  humidity: number | null
  pressure: number | null
  wind_speed: number | null
  rain_amount: number | null
  recorded_at: ISODateString
  created_at: ISODateString
}

export interface WeatherReadingWithLocation extends WeatherReading {
  device_location: string
}

export interface WeatherReadingListResponse {
  readings: WeatherReading[]
  total: number
}

export interface LatestReadingsResponse {
  readings: WeatherReadingWithLocation[]
  fetched_at: ISODateString
}

export interface WeatherSummary {
  device_id: number
  device_location: string
  avg_temperature: number | null
  min_temperature: number | null
  max_temperature: number | null
  avg_humidity: number | null
  avg_pressure: number | null
  reading_count: number
  period_start: ISODateString
  period_end: ISODateString
}

const WEATHER_BASE = '/weather'

export const weatherReadingService = {
  async getLatestForDisplay(): Promise<LatestReadingsResponse> {
    try {
      const response = await apiClient.get<LatestReadingsResponse>(`${WEATHER_BASE}/display/latest`)
      return response.data
    } catch (error) {
      throw error instanceof ApiError
        ? error
        : new ApiError('Failed to fetch latest readings for display')
    }
  },

  async getSensorLatest(deviceId: number): Promise<WeatherReadingWithLocation> {
    try {
      const response = await apiClient.get<WeatherReadingWithLocation>(
        `${WEATHER_BASE}/display/sensor/${deviceId}/latest`,
      )
      return response.data
    } catch (error) {
      throw error instanceof ApiError
        ? error
        : new ApiError('Failed to fetch latest reading for sensor')
    }
  },

  async getAll(params?: {
    skip?: number
    limit?: number
    start_time?: DateLike
    end_time?: DateLike
  }): Promise<WeatherReadingListResponse> {
    try {
      const response = await apiClient.get<WeatherReadingListResponse>(`${WEATHER_BASE}/readings`, {
        params: {
          skip: params?.skip ?? 0,
          limit: params?.limit ?? 100,
          start_time: toIso(params?.start_time),
          end_time: toIso(params?.end_time),
        },
      })
      return response.data
    } catch (error) {
      throw error instanceof ApiError ? error : new ApiError('Failed to fetch readings')
    }
  },

  async getSensorHistory(
    deviceId: number,
    params?: {
      skip?: number
      limit?: number
      start_time?: DateLike
      end_time?: DateLike
    },
  ): Promise<WeatherReadingListResponse> {
    try {
      const response = await apiClient.get<WeatherReadingListResponse>(
        `${WEATHER_BASE}/display/sensor/${deviceId}/history`,
        {
          params: {
            skip: params?.skip ?? 0,
            limit: params?.limit ?? 100,
            start_time: toIso(params?.start_time),
            end_time: toIso(params?.end_time),
          },
        },
      )
      return response.data
    } catch (error) {
      throw error instanceof ApiError
        ? error
        : new ApiError('Failed to fetch sensor reading history')
    }
  },

  async getSensorSummary(deviceId: number, hours = 24): Promise<WeatherSummary> {
    try {
      const response = await apiClient.get<WeatherSummary>(
        `${WEATHER_BASE}/display/sensor/${deviceId}/summary`,
        { params: { hours } },
      )
      return response.data
    } catch (error) {
      throw error instanceof ApiError
        ? error
        : new ApiError('Failed to fetch weather summary for sensor')
    }
  },
}
