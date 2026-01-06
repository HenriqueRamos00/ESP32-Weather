<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDevices } from '@/composables/useDevices'
import { useWeatherReadings } from '@/composables/useWeatherReading'
import { useToast } from '@/composables/useToast'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import DashboardFilters, { type MetricKey } from '@/components/Dashboard/DashboardFilter.vue'
import DateRangeButtons, { type RangePreset } from '@/components/Dashboard/DateRangeButtons.vue'
import WeatherMetricChart from '@/components/Dashboard/WeatherMetricChart.vue'
import SensorSummaryCard from '@/components/Dashboard/SensorSummaryCard.vue'
import type { WeatherReading, WeatherSummary } from '@/services/weatherReadingService'

type MaybeWithStatus = {
  status?: number
  statusCode?: number
  response?: { status?: number }
}

const { devices, fetchDevices, loading: devicesLoading } = useDevices()
const { fetchSensorHistory, fetchSensorSummary } = useWeatherReadings()
const { error: showError } = useToast()

const initialLoading = ref(true)
const selectedSensorId = ref<number | null>(null)
const selectedMetric = ref<MetricKey>('temperature')
const selectedRange = ref<RangePreset>('1d')
const chartLoading = ref(false)

const chartReadings = ref<WeatherReading[]>([])
const sensorSummary = ref<WeatherSummary | null>(null)

const sensors = computed(() =>
  devices.value
    .filter((d) => d.function === 'sensor')
    .map((d) => ({
      id: d.id,
      label: `${d.location} — ${d.type} (#${d.id})`,
    })),
)

const selectedSensorLabel = computed(() => {
  const opt = sensors.value.find((s) => s.id === selectedSensorId.value)
  return opt?.label ?? 'No sensor selected'
})

const isBusy = computed(() => devicesLoading.value || initialLoading.value)

/**
 * Convert RangePreset to start/end dates
 */
function getDateRangeFromPreset(preset: RangePreset): {
  start: Date | null
  end: Date | null
  limit: number
} {
  const now = new Date()
  const end = now

  switch (preset) {
    case '1d':
      return {
        start: new Date(now.getTime() - 24 * 60 * 60 * 1000),
        end,
        limit: 300, // ~288 readings for 5min intervals
      }
    case '3d':
      return {
        start: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000),
        end,
        limit: 900,
      }
    case '5d':
      return {
        start: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000),
        end,
        limit: 1500,
      }
    case '1w':
      return {
        start: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
        end,
        limit: 2100,
      }
    case '1m':
      return {
        start: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000),
        end,
        limit: 5000,
      }
    case 'all':
      return {
        start: null,
        end: null,
        limit: 10000, // Safety limit
      }
    default:
      return { start: null, end: null, limit: 500 }
  }
}

function isNotFound(err: unknown): boolean {
  if (!err || (typeof err !== 'object' && typeof err !== 'function')) {
    return false
  }
  const e = err as MaybeWithStatus
  return e.status === 404 || e.statusCode === 404 || e.response?.status === 404
}

async function loadForSensor(deviceId: number, clearData = true) {
  if (clearData) {
    chartReadings.value = []
    sensorSummary.value = null
  }

  chartLoading.value = true

  const { start, end, limit } = getDateRangeFromPreset(selectedRange.value)

  try {
    // History (graph)
    try {
      const history = await fetchSensorHistory(deviceId, {
        limit,
        start_time: start,
        end_time: end,
      })
      chartReadings.value = history.readings
    } catch (err) {
      if (!isNotFound(err)) throw err
      if (clearData) chartReadings.value = []
    }

    // Summary - only fetch when loading new sensor, not on date range change
    if (clearData) {
      try {
        const summary = await fetchSensorSummary(deviceId, 24)
        sensorSummary.value = summary
      } catch (err) {
        if (!isNotFound(err)) throw err
        sensorSummary.value = null
      }
    }
  } finally {
    chartLoading.value = false
  }
}

onMounted(async () => {
  try {
    await fetchDevices()
    const firstSensor = sensors.value[0]
    if (firstSensor) {
      selectedSensorId.value = firstSensor.id
      await loadForSensor(firstSensor.id)
    }
  } catch (err) {
    showError('Failed to load dashboard', err instanceof Error ? err.message : undefined)
  } finally {
    initialLoading.value = false
  }
})

watch(
  () => selectedRange.value,
  async (newVal, oldVal) => {
    if (newVal === oldVal) return
    if (!selectedSensorId.value) return
    try {
      await loadForSensor(selectedSensorId.value, false)
    } catch (err) {
      showError('Failed to load sensor data', err instanceof Error ? err.message : undefined)
    }
  },
)
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
      <!-- header content unchanged -->
    </div>

    <div v-if="initialLoading" class="flex justify-center items-center py-20">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else class="space-y-4">
      <DashboardFilters
        :sensors="sensors"
        :selected-sensor-id="selectedSensorId"
        :selected-metric="selectedMetric"
        :disabled="isBusy"
        @update:sensor="selectedSensorId = $event"
        @update:metric="selectedMetric = $event"
      />

      <div v-if="sensors.length === 0" class="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <p class="text-slate-300">
          No sensor boards found. Add a device with <code>function: "sensor"</code>.
        </p>
      </div>

      <div
        v-else-if="!selectedSensorId"
        class="bg-slate-800 border border-slate-700 rounded-lg p-6"
      >
        <p class="text-slate-300">Select a sensor to view its chart.</p>
      </div>

      <template v-else>
        <SensorSummaryCard :summary="sensorSummary" />

        <!-- Date Range Buttons -->
        <div class="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <label class="block text-sm font-medium text-slate-300 mb-2">Time Range</label>
          <DateRangeButtons v-model="selectedRange" :disabled="chartLoading" />
        </div>

        <!-- Chart section with stable key -->
        <div :key="selectedSensorId" class="relative min-h-[300px]">
          <!-- Loading overlay -->
          <div
            v-show="chartLoading"
            class="absolute inset-0 bg-slate-900/50 flex items-center justify-center z-10 rounded-lg"
          >
            <LoadingSpinner />
          </div>

          <WeatherMetricChart
            v-if="chartReadings.length > 0"
            :readings="chartReadings"
            :metric="selectedMetric"
            :title="`${selectedSensorLabel} — ${selectedMetric}`"
          />

          <div
            v-else-if="!chartLoading"
            class="bg-slate-800 border border-slate-700 rounded-lg p-6 text-slate-300"
          >
            No data available for the selected time range.
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
