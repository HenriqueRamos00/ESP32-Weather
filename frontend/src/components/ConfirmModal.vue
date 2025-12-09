<script setup lang="ts">
defineProps<{
  show: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const variantClasses = {
  danger: 'bg-red-600 hover:bg-red-500',
  warning: 'bg-yellow-600 hover:bg-yellow-500',
  info: 'bg-blue-600 hover:bg-blue-500',
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
        @click.self="emit('cancel')"
      >
        <div
          class="bg-slate-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4 border border-slate-600"
        >
          <h3 class="text-lg font-bold text-white mb-2">{{ title }}</h3>
          <p class="text-slate-400 mb-6">{{ message }}</p>

          <div class="flex justify-end gap-3">
            <button
              @click="emit('cancel')"
              class="px-4 py-2 text-slate-400 hover:text-white transition-colors"
            >
              {{ cancelText || 'Cancel' }}
            </button>
            <button
              @click="emit('confirm')"
              :class="[
                'px-4 py-2 rounded text-white transition-colors',
                variantClasses[variant || 'danger'],
              ]"
            >
              {{ confirmText || 'Confirm' }}
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
