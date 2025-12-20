<script setup lang="ts">
export type MetricKey = 'temperature' | 'humidity' | 'pressure' | 'wind_speed' | 'rain_amount'

type SensorOption = {
  id: number
  label: string
}

defineProps<{
  sensors: SensorOption[]
  selectedSensorId: number | null
  selectedMetric: MetricKey
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:sensor', value: number | null): void
  (e: 'update:metric', value: MetricKey): void
}>()

const metricOptions: { value: MetricKey; label: string }[] = [
  { value: 'temperature', label: 'Temperature (°C)' },
  { value: 'humidity', label: 'Humidity (%)' },
  { value: 'pressure', label: 'Pressure (hPa)' },
  { value: 'wind_speed', label: 'Wind speed (m/s)' },
  { value: 'rain_amount', label: 'Rain amount (mm)' },
]
</script>

<template>
  <div
    class="bg-slate-800 border border-slate-700 rounded-lg p-4 flex flex-col gap-4 md:flex-row md:items-end"
  >
    <div class="flex-1">
      <label class="block text-sm text-slate-300 mb-2">Sensor board</label>
      <select
        class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white"
        :disabled="disabled"
        :value="selectedSensorId ?? ''"
        @change="
          emit(
            'update:sensor',
            ($event.target as HTMLSelectElement).value
              ? Number(($event.target as HTMLSelectElement).value)
              : null,
          )
        "
      >
        <option value="" disabled>Select a sensor...</option>
        <option v-for="s in sensors" :key="s.id" :value="s.id">
          {{ s.label }}
        </option>
      </select>
    </div>

    <div class="flex-1">
      <label class="block text-sm text-slate-300 mb-2">Metric</label>
      <select
        class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white"
        :disabled="disabled"
        :value="selectedMetric"
        @change="emit('update:metric', ($event.target as HTMLSelectElement).value as any)"
      >
        <option v-for="m in metricOptions" :key="m.value" :value="m.value">
          {{ m.label }}
        </option>
      </select>
    </div>
  </div>
</template>
