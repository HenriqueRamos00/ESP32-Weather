<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  start: Date | null
  end: Date | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:start', value: Date | null): void
  (e: 'update:end', value: Date | null): void
  (e: 'apply'): void
  (e: 'reset'): void
}>()

const isOpen = ref(false)

function toInputValue(d: Date | null): string {
  if (!d) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  const yyyy = d.getFullYear()
  const mm = pad(d.getMonth() + 1)
  const dd = pad(d.getDate())
  const hh = pad(d.getHours())
  const mi = pad(d.getMinutes())
  return `${yyyy}-${mm}-${dd}T${hh}:${mi}`
}

function fromInputValue(v: string): Date | null {
  if (!v) return null
  const d = new Date(v)
  return isNaN(d.getTime()) ? null : d
}

const isInvalidRange = computed(() => {
  if (!props.start || !props.end) return false
  return props.start.getTime() > props.end.getTime()
})

const formattedRange = computed(() => {
  if (!props.start && !props.end) return 'No range selected'
  const fmt = (d: Date | null) =>
    d
      ? `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
          d.getDate(),
        ).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(
          d.getMinutes(),
        ).padStart(2, '0')}`
      : '—'
  return `${fmt(props.start)} → ${fmt(props.end)}`
})
</script>

<template>
  <div class="bg-slate-800 border border-slate-700 rounded-lg">
    <!-- header / collapsed view -->
    <button
      class="w-full flex items-center justify-between px-4 py-3 text-left"
      type="button"
      @click="isOpen = !isOpen"
    >
      <div class="text-sm text-slate-300">
        <div class="font-medium">Date range</div>
        <div class="text-xs text-slate-400 mt-1">
          {{ formattedRange }}
        </div>
      </div>

      <!-- simple chevron icon (not emoji) -->
      <span
        class="ml-2 inline-flex h-4 w-4 items-center justify-center text-slate-400 transition-transform duration-200"
        :class="{ 'rotate-90': isOpen }"
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 16 16"
          class="h-3 w-3"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <!-- chevron pointing right; rotation handles open/closed -->
          <path d="M5 3l5 5-5 5" />
        </svg>
      </span>
    </button>

    <!-- animated expand/collapse -->
    <transition
      name="collapse"
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="max-h-0 opacity-0"
      enter-to-class="max-h-96 opacity-100"
      leave-from-class="max-h-96 opacity-100"
      leave-to-class="max-h-0 opacity-0"
    >
      <div v-if="isOpen" class="border-t border-slate-700 overflow-hidden">
        <div class="p-4">
          <div class="flex flex-col gap-4 md:flex-row md:items-end">
            <div class="flex-1">
              <label class="block text-sm text-slate-300 mb-2">Start</label>
              <input
                class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white"
                type="datetime-local"
                :disabled="disabled"
                :value="toInputValue(start)"
                @input="
                  emit('update:start', fromInputValue(($event.target as HTMLInputElement).value))
                "
              />
            </div>
            <div class="flex-1">
              <label class="block text-sm text-slate-300 mb-2">End</label>
              <input
                class="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white"
                type="datetime-local"
                :disabled="disabled"
                :value="toInputValue(end)"
                @input="
                  emit('update:end', fromInputValue(($event.target as HTMLInputElement).value))
                "
              />
            </div>
            <div class="flex gap-2 w-full md:w-auto">
              <button
                class="flex-1 md:flex-initial bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
                :disabled="disabled || isInvalidRange"
                @click="emit('apply')"
              >
                Apply
              </button>
              <button
                class="flex-1 md:flex-initial bg-slate-900 hover:bg-slate-700 border border-slate-700 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
                :disabled="disabled"
                @click="emit('reset')"
              >
                Reset
              </button>
            </div>
          </div>
          <p v-if="isInvalidRange" class="text-sm text-red-400 mt-2">Start must be before End.</p>
        </div>
      </div>
    </transition>
  </div>
</template>
