<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDevices } from '@/composables/useDevices'
import { useWeatherReadings } from '@/composables/useWeatherReading'
import { useToast } from '@/composables/useToast'

import LoadingSpinner from '@/components/LoadingSpinner.vue'
import DashboardFilters, { type MetricKey } from '@/components/DashboardFilter.vue'
import DateRangePicker from '@/components/DateRangePicker.vue'
import WeatherMetricChart from '@/components/WeatherMetricChart.vue'
import SensorSummaryCard from '@/components/SensorSummaryCard.vue'

import type { WeatherReading, WeatherSummary } from '@/services/weatherReadingService'

type MaybeWithStatus = {
  status?: number
  statusCode?: number
  response?: { status?: number }
}

const { devices, fetchDevices, loading: devicesLoading } = useDevices()
const { fetchSensorHistory, fetchSensorSummary, loading: weatherLoading } = useWeatherReadings()
const { error: showError } = useToast()

const initialLoading = ref(true)

const selectedSensorId = ref<number | null>(null)
const selectedMetric = ref<MetricKey>('temperature')

/** draft (what user is editing) */
const rangeStart = ref<Date | null>(null)
const rangeEnd = ref<Date | null>(null)

/** applied (what is actually used for querying) */
const appliedStart = ref<Date | null>(null)
const appliedEnd = ref<Date | null>(null)

/** local state to avoid “old data” sticking */
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

const isBusy = computed(() => devicesLoading.value || weatherLoading.value)

function isNotFound(err: unknown): boolean {
  if (!err || (typeof err !== 'object' && typeof err !== 'function')) {
    return false
  }

  const e = err as MaybeWithStatus

  return e.status === 404 || e.statusCode === 404 || e.response?.status === 404
}

async function loadForSensor(deviceId: number) {
  // IMPORTANT: clear immediately so old chart data never stays on screen
  chartReadings.value = []
  sensorSummary.value = null

  // History (graph)
  try {
    const history = await fetchSensorHistory(deviceId, {
      limit: 500,
      start_time: appliedStart.value,
      end_time: appliedEnd.value,
    })
    chartReadings.value = history.readings
  } catch (err) {
    // If no data exists, keep empty and don't toast as a "failure"
    if (!isNotFound(err)) throw err
    chartReadings.value = []
  }

  // Summary (optional card)
  try {
    sensorSummary.value = await fetchSensorSummary(deviceId, 24)
  } catch (err) {
    // No readings => summary may 404; that's okay
    if (!isNotFound(err)) throw err
    sensorSummary.value = null
  }
}

function applyRange() {
  appliedStart.value = rangeStart.value
  appliedEnd.value = rangeEnd.value
  if (selectedSensorId.value) {
    loadForSensor(selectedSensorId.value).catch((err) => {
      showError('Failed to load sensor data', err instanceof Error ? err.message : undefined)
    })
  }
}

function resetRange() {
  rangeStart.value = null
  rangeEnd.value = null
  appliedStart.value = null
  appliedEnd.value = null
  if (selectedSensorId.value) {
    loadForSensor(selectedSensorId.value).catch((err) => {
      showError('Failed to load sensor data', err instanceof Error ? err.message : undefined)
    })
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
  () => selectedSensorId.value,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return
    try {
      await loadForSensor(newId)
    } catch (err) {
      showError('Failed to load sensor data', err instanceof Error ? err.message : undefined)
    }
  },
)
</script>

<template>
  <div>
    <div class="flex justify-between items-start gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <p class="text-slate-400 text-sm">
          Select a sensor, metric, and date range to visualize readings.
        </p>
      </div>

      <button
        class="bg-slate-800 hover:bg-slate-700 border border-slate-700 px-4 py-2 rounded transition-colors disabled:opacity-50"
        :disabled="isBusy || !selectedSensorId"
        @click="selectedSensorId && loadForSensor(selectedSensorId)"
      >
        Refresh
      </button>
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
        <div v-if="weatherLoading" class="flex justify-center py-6">
          <LoadingSpinner />
        </div>

        <div v-else-if="chartReadings.length > 0">
          <WeatherMetricChart
            :readings="chartReadings"
            :metric="selectedMetric"
            :title="`${selectedSensorLabel} — ${selectedMetric}`"
          />

          <div class="mt-4">
            <DateRangePicker
              :start="rangeStart"
              :end="rangeEnd"
              :disabled="isBusy || !selectedSensorId"
              @update:start="rangeStart = $event"
              @update:end="rangeEnd = $event"
              @apply="applyRange"
              @reset="resetRange"
            />
          </div>
        </div>

        <div v-else class="bg-slate-800 border border-slate-700 rounded-lg p-6 text-slate-300">
          Start sending data from the ESP device.
        </div>
      </template>
    </div>
  </div>
</template>
