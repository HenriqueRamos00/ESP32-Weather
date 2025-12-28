<script setup lang="ts">
import Sidebar from '@/components/MainSidebar.vue'
import { ref } from 'vue'

const sidebarOpen = ref(false)
</script>

<template>
  <div class="h-screen flex bg-slate-900 text-white overflow-hidden">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Mobile header -->
    <header
      class="fixed top-0 left-0 right-0 h-14 bg-slate-800 border-b border-slate-700 flex items-center px-4 z-30 lg:hidden"
    >
      <button
        class="p-2 -ml-2 text-slate-300 hover:text-white"
        @click="sidebarOpen = !sidebarOpen"
        aria-label="Toggle menu"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
      <span class="ml-3 font-semibold">Weather App</span>
    </header>

    <!-- Sidebar wrapper -->
    <div
      class="fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <Sidebar @navigate="sidebarOpen = false" />
    </div>

    <!-- Main content area -->
    <main class="flex-1 overflow-y-auto p-4 pt-[4.5rem] lg:p-6 lg:pt-6">
      <RouterView />
    </main>
  </div>
</template>
