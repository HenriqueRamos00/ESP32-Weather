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
        class="fixed inset-0 bg-black/70 flex items-end sm:items-center justify-center z-50 p-0 sm:p-4"
        @click.self="emit('cancel')"
      >
        <div
          class="bg-slate-800 p-6 rounded-t-lg sm:rounded-lg shadow-xl max-w-md w-full border border-slate-600 border-b-0 sm:border-b"
        >
          <h3 class="text-lg font-bold text-white mb-2">{{ title }}</h3>
          <p class="text-slate-400 mb-6">{{ message }}</p>

          <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
            <button
              @click="emit('cancel')"
              class="w-full sm:w-auto px-4 py-3 sm:py-2 text-slate-400 hover:text-white hover:bg-slate-700 sm:hover:bg-transparent rounded-md sm:rounded-none transition-colors"
            >
              {{ cancelText || 'Cancel' }}
            </button>
            <button
              @click="emit('confirm')"
              :class="[
                'w-full sm:w-auto px-4 py-3 sm:py-2 rounded-md text-white transition-colors',
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

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: translateY(100%);
}

@media (min-width: 640px) {
  .modal-enter-from > div,
  .modal-leave-to > div {
    transform: translateY(0) scale(0.95);
  }
}
</style>
