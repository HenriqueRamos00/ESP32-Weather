<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
}>()

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
}
</script>

<template>
  <div
    :class="[
      'animate-spin rounded-full border-2 border-slate-600 border-t-blue-500',
      sizeClasses[size || 'md'],
    ]"
  ></div>
</template>
