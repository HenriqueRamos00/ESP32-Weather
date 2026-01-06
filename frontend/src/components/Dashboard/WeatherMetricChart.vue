<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartOptions,
} from 'chart.js'
import { Line } from 'vue-chartjs'
import type { WeatherReading } from '@/services/weatherReadingService'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

type MetricKey = 'temperature' | 'humidity' | 'pressure' | 'wind_speed' | 'rain_amount'

const props = defineProps<{
  readings: WeatherReading[]
  metric: MetricKey
  title?: string
}>()

const metricConfig: Record<MetricKey, { label: string; unit: string; color: string }> = {
  temperature: { label: 'Temperature', unit: '°C', color: '#10b981' }, // emerald-500
  humidity: { label: 'Humidity', unit: '%', color: '#10b981' },
  pressure: { label: 'Pressure', unit: 'hPa', color: '#10b981' },
  wind_speed: { label: 'Wind Speed', unit: 'm/s', color: '#10b981' },
  rain_amount: { label: 'Rain Amount', unit: 'mm', color: '#10b981' },
}

const metricMeta = computed(() => metricConfig[props.metric])

// Sort readings by date ascending (oldest first, newest on right)
const sortedReadings = computed(() => {
  return [...props.readings].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
  )
})

const dataSpanHours = computed(() => {
  const readings = sortedReadings.value
  if (!readings || readings.length < 2) return 0

  const firstReading = readings[0]
  const lastReading = readings[readings.length - 1]

  if (!firstReading || !lastReading) return 0

  const first = new Date(firstReading.recorded_at).getTime()
  const last = new Date(lastReading.recorded_at).getTime()

  return Math.abs(last - first) / (1000 * 60 * 60)
})
/**
 * Format date based on data range span
 */
function formatDateLabel(dateStr: string, isTooltip = false): string {
  const date = new Date(dateStr)
  const hours = dataSpanHours.value

  if (isTooltip) {
    // Full format for tooltip
    return date.toLocaleString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  // Less than 24 hours: "2 PM" or "2:30 PM"
  if (hours <= 24) {
    const mins = date.getMinutes()
    if (mins === 0) {
      return date.toLocaleTimeString(undefined, {
        hour: 'numeric',
      })
    }
    return date.toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  // Less than 7 days: "Mon" or "Tue 2PM"
  if (hours <= 168) {
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    })
  }

  // More than 7 days: "Jan 15"
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Calculate appropriate max ticks based on data length
 */
const maxTicksLimit = computed(() => {
  const hours = dataSpanHours.value

  // 1 day: show every few hours
  if (hours <= 24) return 6
  // 3 days: show roughly per day
  if (hours <= 72) return 4
  // 1 week: show key days
  if (hours <= 168) return 5
  // 1 month: show weekly markers
  return 4
})

const chartData = computed(() => ({
  labels: sortedReadings.value.map((r) => r.recorded_at),
  datasets: [
    {
      label: `${metricMeta.value.label} (${metricMeta.value.unit})`,
      data: sortedReadings.value.map((r) => r[props.metric]),
      borderColor: metricMeta.value.color,
      backgroundColor: `${metricMeta.value.color}20`,
      fill: true,
      tension: 0.3,
      pointRadius: sortedReadings.value.length > 100 ? 0 : 2,
      pointHoverRadius: 4,
      borderWidth: 2,
    },
  ],
}))

const chartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index' as const, // <-- Add 'as const' here
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#e2e8f0',
      bodyColor: '#e2e8f0',
      borderColor: '#334155',
      borderWidth: 1,
      padding: 10,
      callbacks: {
        title: (items) => {
          const item = items[0]
          if (item?.label) {
            return formatDateLabel(item.label as string, true)
          }
          return ''
        },
        label: (context) => {
          const value = context.parsed.y
          if (value == null) return ''
          return `${metricMeta.value.label}: ${value.toFixed(1)} ${metricMeta.value.unit}`
        },
      },
    },
  },
  scales: {
    x: {
      grid: {
        color: '#334155',
        drawTicks: true,
      },
      border: {
        color: '#475569',
      },
      ticks: {
        color: '#94a3b8',
        maxRotation: 0,
        minRotation: 0,
        autoSkip: true,
        maxTicksLimit: maxTicksLimit.value,
        callback: function (_, index) {
          const label = this.getLabelForValue(index)
          return formatDateLabel(label as string)
        },
        font: {
          size: 11,
        },
        padding: 6,
      },
    },
    y: {
      grid: {
        color: '#334155',
        drawTicks: false,
      },
      border: {
        color: '#475569',
      },
      ticks: {
        color: '#94a3b8',
        padding: 8,
        callback: (value) => `${value} ${metricMeta.value.unit}`,
      },
    },
  },
}))
</script>

<template>
  <div class="bg-slate-800 border border-slate-700 rounded-lg p-3 sm:p-4">
    <div class="flex items-center justify-between mb-2 sm:mb-3">
      <h2 class="text-base sm:text-lg font-semibold truncate mr-2">
        {{ title ?? `${metricMeta.label} over time` }}
      </h2>
      <span class="text-xs text-slate-400 whitespace-nowrap">{{ sortedReadings.length }} pts</span>
    </div>

    <div class="h-[220px] sm:h-[320px]">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>
