<script setup lang="ts">
import Sidebar from '@/components/MainSidebar.vue'
</script>

<template>
  <div class="h-screen flex bg-slate-900 text-white overflow-hidden">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main content area -->
    <main class="flex-1 overflow-y-auto p-6">
      <RouterView />
    </main>
  </div>
</template>
