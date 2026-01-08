<script setup lang="ts">
export type RangePreset = '1d' | '3d' | '5d' | '1w' | '1m' | '1y'

const props = defineProps<{
  modelValue: RangePreset
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: RangePreset]
}>()

const presets = [
  { value: '1d' as const, label: '1D' },
  { value: '3d' as const, label: '3D' },
  { value: '5d' as const, label: '5D' },
  { value: '1w' as const, label: '1W' },
  { value: '1m' as const, label: '1M' },
  { value: '1y' as const, label: '1Y' },
]

function isActive(value: RangePreset) {
  return props.modelValue === value
}

function select(event: Event, value: RangePreset) {
  event.preventDefault()
  event.stopPropagation()

  if (!props.disabled) {
    emit('update:modelValue', value)
  }
}
</script>

<template>
  <div class="flex gap-1 flex-wrap">
    <button
      v-for="preset in presets"
      :key="preset.value"
      type="button"
      :disabled="disabled"
      :class="[
        'px-3 py-1.5 rounded text-sm font-medium transition-colors',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        isActive(preset.value)
          ? 'bg-emerald-600 text-white'
          : 'bg-slate-700 text-slate-300 hover:bg-slate-600',
      ]"
      @click="select($event, preset.value)"
    >
      {{ preset.label }}
    </button>
  </div>
</template>
