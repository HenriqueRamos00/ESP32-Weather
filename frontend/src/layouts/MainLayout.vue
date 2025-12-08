<script setup lang="ts">
import Sidebar from '@/components/MainSidebar.vue'
</script>

<template>
  <div class="min-h-screen flex bg-slate-900 text-white">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main content area -->
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
</template>
