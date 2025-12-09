<script setup lang="ts">
import { RouterView } from 'vue-router'
import ToastContainer from '@/components/ToastContainer.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-white">
    <RouterView />
    <ToastContainer />
  </div>
</template>

<style scoped></style>
