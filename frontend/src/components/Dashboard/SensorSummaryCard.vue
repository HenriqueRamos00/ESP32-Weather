<script setup lang="ts">
import type { WeatherSummary } from '@/services/weatherReadingService'

defineProps<{
  summary: WeatherSummary | null
}>()

function fmt(value: number | null | undefined, suffix = '') {
  if (value === null || value === undefined) return '—'
  return `${value.toFixed(2)}${suffix}`
}
</script>

<template>
  <div class="bg-slate-800 border border-slate-700 rounded-lg p-4">
    <h3 class="text-sm text-slate-300 mb-3">Summary (last 24h)</h3>

    <div v-if="!summary" class="text-slate-400 text-sm">No summary available</div>

    <div v-else class="grid grid-cols-1 xs:grid-cols-2 md:grid-cols-4 gap-3 text-sm">
      <div>
        <div class="text-slate-400">Avg Temp</div>
        <div class="font-semibold">{{ fmt(summary.avg_temperature, '°C') }}</div>
      </div>
      <div>
        <div class="text-slate-400">Min Temp</div>
        <div class="font-semibold">{{ fmt(summary.min_temperature, '°C') }}</div>
      </div>
      <div>
        <div class="text-slate-400">Max Temp</div>
        <div class="font-semibold">{{ fmt(summary.max_temperature, '°C') }}</div>
      </div>
      <div>
        <div class="text-slate-400">Avg Humidity</div>
        <div class="font-semibold">{{ fmt(summary.avg_humidity, '%') }}</div>
      </div>
      <div>
        <div class="text-slate-400">Avg Pressure</div>
        <div class="font-semibold">{{ fmt(summary.avg_pressure, ' hPa') }}</div>
      </div>
      <div>
        <div class="text-slate-400">Readings</div>
        <div class="font-semibold">{{ summary.reading_count }}</div>
      </div>
      <div class="xs:col-span-2">
        <div class="text-slate-400">Sensor</div>
        <div class="font-semibold">{{ summary.device_location }} (ID: {{ summary.device_id }})</div>
      </div>
    </div>
  </div>
</template>
