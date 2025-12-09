import { ref, readonly } from 'vue'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration: number
}

export type ToastInput = Omit<Toast, 'id' | 'duration'> & { duration?: number }

const toasts = ref<Toast[]>([])

export function useToast() {
  const addToast = (toast: ToastInput) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`
    const duration = toast.duration ?? 5000

    const newToast: Toast = {
      ...toast,
      id,
      duration,
    }

    toasts.value.push(newToast)

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  const success = (title: string, message?: string) => {
    return addToast({ type: 'success', title, message })
  }

  const error = (title: string, message?: string) => {
    return addToast({ type: 'error', title, message, duration: 7000 })
  }

  const warning = (title: string, message?: string) => {
    return addToast({ type: 'warning', title, message })
  }

  const info = (title: string, message?: string) => {
    return addToast({ type: 'info', title, message })
  }

  const clearAll = () => {
    toasts.value = []
  }

  return {
    toasts: readonly(toasts),
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
    clearAll,
  }
}
