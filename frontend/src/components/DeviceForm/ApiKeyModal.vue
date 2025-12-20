<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  show: boolean
  apiKey: string
}>()

const emit = defineEmits<{
  close: []
}>()

const { success } = useToast()
const copied = ref(false)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.apiKey)
    copied.value = true
    success('Copied!', 'API key copied to clipboard')
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const handleClose = () => {
  copied.value = false
  emit('close')
}

const copyAndClose = async () => {
  await copyToClipboard()
  handleClose()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div
          class="bg-slate-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4 border border-slate-600"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="text-emerald-500 text-xl">🔑</span>
            <h3 class="text-lg font-bold text-white">API Key Generated</h3>
          </div>

          <div class="bg-yellow-500/10 border border-yellow-500/30 rounded p-3 mb-4">
            <p class="text-yellow-500 text-sm flex items-start gap-2">
              <span>⚠</span>
              <span>Copy this key now. You won't be able to see it again!</span>
            </p>
          </div>

          <div class="relative mb-6">
            <div
              class="bg-slate-900 p-4 rounded font-mono text-sm break-all text-emerald-400 border border-slate-700 pr-12"
            >
              {{ apiKey }}
            </div>
            <button
              @click="copyToClipboard"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-slate-700 rounded transition-colors"
              :title="copied ? 'Copied!' : 'Copy to clipboard'"
            >
              <span v-if="copied" class="text-emerald-500">✓</span>
              <span v-else class="text-slate-400">📋</span>
            </button>
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="handleClose"
              class="px-4 py-2 text-slate-400 hover:text-white transition-colors"
            >
              Close
            </button>
            <button
              @click="copyAndClose"
              class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded transition-colors"
            >
              {{ copied ? 'Copied!' : 'Copy & Close' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
