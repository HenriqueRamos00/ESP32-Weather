<script setup lang="ts">
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()

type NavItem = {
  name: string
  label: string
  to: string
}

const navItems: NavItem[] = [
  { name: 'Dashboard', label: 'Dashboard', to: '/' },
  { name: 'Devices', label: 'Devices', to: '/devices' },
  { name: 'Options', label: 'Options', to: '/options' },
]
</script>

<template>
  <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
    <div class="h-16 flex items-center px-4 border-b border-slate-800">
      <span class="text-xl font-bold">Weather App</span>
    </div>

    <nav class="flex-1 py-4">
      <ul class="space-y-1">
        <li v-for="item in navItems" :key="item.name">
          <RouterLink
            :to="item.to"
            class="block px-4 py-2 rounded-md transition-colors"
            :class="[
              route.path === item.to
                ? 'bg-slate-800 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white',
            ]"
          >
            {{ item.label }}
          </RouterLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>
