<script setup lang="ts">
import { computed } from 'vue'
import type { WeatherReading } from '@/services/weatherReadingService'
import type { MetricKey } from './DashboardFilter.vue'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, TimeScale)

const props = defineProps<{
  readings: ReadonlyArray<WeatherReading>
  metric: MetricKey
  title?: string
}>()

const metricMeta = computed(() => {
  switch (props.metric) {
    case 'temperature':
      return { label: 'Temperature', unit: '°C' }
    case 'humidity':
      return { label: 'Humidity', unit: '%' }
    case 'pressure':
      return { label: 'Pressure', unit: 'hPa' }
    case 'wind_speed':
      return { label: 'Wind speed', unit: 'm/s' }
    case 'rain_amount':
      return { label: 'Rain amount', unit: 'mm' }
    default:
      return { label: 'Unknown', unit: '' }
  }
})

const sorted = computed(() =>
  [...props.readings].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
  ),
)

const chartData = computed(() => {
  const labels = sorted.value.map((r) => new Date(r.recorded_at).toLocaleString())

  // Keep nulls (Chart.js will break the line), which is usually better than forcing 0
  const values = sorted.value.map((r) => (r[props.metric] ?? null) as number | null)

  return {
    labels,
    datasets: [
      {
        label: `${metricMeta.value.label} (${metricMeta.value.unit})`,
        data: values,
        borderColor: '#34d399', // emerald-400
        backgroundColor: 'rgba(52, 211, 153, 0.15)',
        pointRadius: 1.5,
        tension: 0.25,
        spanGaps: false,
      },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#e2e8f0' } },
    tooltip: { enabled: true },
  },
  scales: {
    x: {
      ticks: { color: '#94a3b8', maxRotation: 0, autoSkip: true },
      grid: { color: 'rgba(148, 163, 184, 0.12)' },
    },
    y: {
      ticks: { color: '#94a3b8' },
      grid: { color: 'rgba(148, 163, 184, 0.12)' },
    },
  },
}))
</script>

<template>
  <div class="bg-slate-800 border border-slate-700 rounded-lg p-4">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-semibold">
        {{ title ?? `${metricMeta.label} over time` }}
      </h2>
    </div>

    <div class="h-[280px] sm:h-[360px]">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
