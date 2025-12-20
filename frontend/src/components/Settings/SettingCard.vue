<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  title: string
  description: string
  value: string | number
  type?: 'text' | 'number' | 'textarea'
  min?: number
  step?: number
  suffix?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
})

const emit = defineEmits<{
  update: [value: string]
}>()

const localValue = ref(props.value)

// Sync local value with prop changes
watch(
  () => props.value,
  (newVal) => {
    localValue.value = newVal
  },
)

const handleUpdate = () => {
  emit('update', String(localValue.value))
}

const handleReset = () => {
  localValue.value = props.value
}

const hasChanges = () => {
  return String(localValue.value) !== String(props.value)
}

// Format display value
const displayValue = () => {
  if (props.type === 'number' && typeof localValue.value === 'number') {
    return `${localValue.value} ${props.suffix || ''}`
  }
  return localValue.value
}

// Calculate minutes if suffix is seconds
const minutesDisplay = () => {
  if (props.suffix === 'seconds' && typeof localValue.value === 'number') {
    const minutes = Math.floor(localValue.value / 60)
    const seconds = localValue.value % 60
    if (seconds === 0) {
      return `(${minutes} ${minutes === 1 ? 'minute' : 'minutes'})`
    }
    return `(${minutes}m ${seconds}s)`
  }
  return null
}
</script>

<template>
  <div class="bg-slate-900 border border-slate-800 rounded-lg p-6">
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-white mb-2">{{ title }}</h3>
      <p class="text-sm text-slate-400">{{ description }}</p>
    </div>

    <div class="space-y-3">
      <div v-if="type === 'textarea'">
        <textarea
          v-model="localValue"
          :disabled="disabled"
          rows="4"
          class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>
      <div v-else>
        <input
          v-model="localValue"
          :type="type"
          :min="min"
          :step="step"
          :disabled="disabled"
          class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      <div class="flex items-center justify-between text-xs text-slate-500">
        <span>
          Current: {{ displayValue() }}
          <span v-if="minutesDisplay()" class="ml-1">{{ minutesDisplay() }}</span>
        </span>
        <span v-if="hasChanges()" class="text-yellow-500">• Unsaved changes</span>
      </div>

      <div class="flex gap-2 pt-2">
        <button
          @click="handleUpdate"
          :disabled="!hasChanges() || disabled"
          class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-md transition-colors font-medium"
        >
          Save
        </button>
        <button
          @click="handleReset"
          :disabled="!hasChanges() || disabled"
          class="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:cursor-not-allowed rounded-md transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  </div>
</template>
