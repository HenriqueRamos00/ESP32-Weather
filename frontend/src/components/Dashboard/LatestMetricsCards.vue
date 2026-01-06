<script setup lang="ts">
import { computed } from 'vue'
import type { WeatherReading } from '@/services/weatherReadingService'

const props = defineProps<{
  readings: WeatherReading[]
}>()

type MetricConfig = {
  key: keyof WeatherReading
  label: string
  unit: string
  icon: string
  colorClass: string
}

const metrics: MetricConfig[] = [
  {
    key: 'temperature',
    label: 'Temperature',
    unit: '°C',
    icon: '🌡️',
    colorClass: 'text-orange-400',
  },
  { key: 'humidity', label: 'Humidity', unit: '%', icon: '💧', colorClass: 'text-blue-400' },
  { key: 'pressure', label: 'Pressure', unit: 'hPa', icon: '📊', colorClass: 'text-purple-400' },
  { key: 'wind_speed', label: 'Wind Speed', unit: 'm/s', icon: '💨', colorClass: 'text-cyan-400' },
  { key: 'rain_amount', label: 'Rain', unit: 'mm', icon: '🌧️', colorClass: 'text-indigo-400' },
]

const latestReading = computed(() => {
  if (!props.readings.length) return null
  // Find the most recent reading by date
  return (
    [...props.readings].sort(
      (a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime(),
    )[0] ?? null
  )
})

const availableMetrics = computed(() => {
  if (!latestReading.value) return []
  return metrics.filter((m) => {
    const value = latestReading.value![m.key]
    return value !== null && value !== undefined
  })
})

const lastUpdated = computed(() => {
  if (!latestReading.value) return ''
  const date = new Date(latestReading.value.recorded_at)
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
})

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '--'
  if (typeof value === 'number') {
    return value.toFixed(1)
  }
  return String(value)
}
</script>

<template>
  <div v-if="latestReading && availableMetrics.length > 0" class="space-y-2">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium text-slate-300">Latest Readings</h3>
      <span class="text-xs text-slate-500">Updated: {{ lastUpdated }}</span>
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      <div
        v-for="metric in availableMetrics"
        :key="metric.key"
        class="bg-slate-800 border border-slate-700 rounded-lg p-3 sm:p-4 hover:border-slate-600 transition-colors"
      >
        <div class="flex items-center gap-2 mb-1">
          <span class="text-base sm:text-lg">{{ metric.icon }}</span>
          <span class="text-xs text-slate-400 truncate">{{ metric.label }}</span>
        </div>
        <div class="flex items-baseline gap-1">
          <span :class="['text-xl sm:text-2xl font-bold', metric.colorClass]">
            {{ formatValue(latestReading[metric.key]) }}
          </span>
          <span class="text-xs sm:text-sm text-slate-500">{{ metric.unit }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
