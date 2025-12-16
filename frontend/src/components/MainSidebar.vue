<script setup lang="ts">
import { useRoute, RouterLink } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore, type UserRole } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

type NavItem = {
  name: string
  label: string
  to: string
  roles?: UserRole[] // if omitted, visible to all authenticated users
}

const navItems: NavItem[] = [
  { name: 'Dashboard', label: 'Dashboard', to: '/', roles: ['admin', 'user'] },
  { name: 'Devices', label: 'Devices', to: '/devices', roles: ['admin'] },
  { name: 'Options', label: 'Options', to: '/options', roles: ['admin'] },
]

const visibleNavItems = computed(() => {
  if (!authStore.user) return []

  return navItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(authStore.user!.role)
  })
})
</script>

<template>
  <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
    <div class="h-16 flex items-center px-4 border-b border-slate-800 justify-between">
      <span class="text-xl font-bold">Weather App</span>
      <span v-if="authStore.user" class="text-xs text-slate-400">
        {{ authStore.user.full_name || authStore.user.email }} ({{ authStore.user.role }})
      </span>
    </div>
    <nav class="flex-1 py-4">
      <ul class="space-y-1">
        <li v-for="item in visibleNavItems" :key="item.name">
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
