<script setup lang="ts">
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore, type UserRole } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { logout } = useAuth()

type NavItem = {
  name: string
  label: string
  to: string
  roles?: UserRole[] // if omitted, visible to all authenticated users
}

const navItems: NavItem[] = [
  { name: 'Dashboard', label: 'Dashboard', to: '/', roles: ['admin', 'user'] },
  { name: 'Devices', label: 'Devices', to: '/devices', roles: ['admin'] },
  { name: 'Users', label: 'Users', to: '/users', roles: ['admin'] },
  { name: 'Options', label: 'Options', to: '/options', roles: ['admin'] },
]

const visibleNavItems = computed(() => {
  if (!authStore.user) return []

  return navItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(authStore.user!.role)
  })
})

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<template>
  <aside class="w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
    <!-- Header -->
    <div class="h-16 flex items-center px-4 border-b border-slate-800">
      <span class="text-xl font-bold">Weather App</span>
    </div>

    <!-- User info -->
    <div v-if="authStore.user" class="px-4 py-3 border-b border-slate-800">
      <p class="text-sm font-medium text-white truncate">
        {{ authStore.user.full_name || authStore.user.email }}
      </p>
      <p class="text-xs text-slate-400 capitalize">{{ authStore.user.role }}</p>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-4">
      <ul class="space-y-1 px-2">
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

    <!-- Logout button at bottom -->
    <div class="p-4 border-t border-slate-800">
      <button
        @click="handleLogout"
        class="w-full px-4 py-2 rounded-md text-slate-300 hover:bg-red-900 hover:text-white transition-colors text-left flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
          />
        </svg>
        <span>Logout</span>
      </button>
    </div>
  </aside>
</template>
