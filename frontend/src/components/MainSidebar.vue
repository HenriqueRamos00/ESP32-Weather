<script setup lang="ts">
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useAuthStore, type UserRole } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'

import CloudIcon from '@/assets/cloud.svg'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { logout } = useAuth()

const isCollapsed = ref(false)

const emit = defineEmits<{
  navigate: []
}>()

// Mobile detection
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 1024)

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

type NavItem = {
  name: string
  label: string
  to: string
  icon: string // SVG path data
  roles?: UserRole[]
}

const navItems: NavItem[] = [
  {
    name: 'Dashboard',
    label: 'Dashboard',
    to: '/',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    roles: ['admin', 'user'],
  },
  {
    name: 'Devices',
    label: 'Devices',
    to: '/devices',
    icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    roles: ['admin'],
  },
  {
    name: 'Users',
    label: 'Users',
    to: '/users',
    icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    roles: ['admin'],
  },
  {
    name: 'Options',
    label: 'Options',
    to: '/options',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    roles: ['admin'],
  },
]

const visibleNavItems = computed(() => {
  if (!authStore.user) return []

  return navItems.filter((item) => {
    if (!item.roles) return true
    return item.roles.includes(authStore.user!.role)
  })
})

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleLogout = () => {
  logout()
  router.push('/login')
}

// Get user initials for avatar
const userInitials = computed(() => {
  if (!authStore.user) return ''
  const name = authStore.user.full_name || authStore.user.email
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})
</script>

<template>
  <aside
    class="bg-slate-950 border-r border-slate-800 flex flex-col transition-all duration-300 h-full"
    :class="[isCollapsed ? 'lg:w-20' : 'lg:w-64', 'w-64']"
  >
    <!-- Header -->
    <div
      class="h-16 flex items-center border-b border-slate-800"
      :class="isCollapsed && !isMobile ? 'justify-center px-2' : 'justify-between px-4'"
    >
      <!-- Mobile header content -->
      <div class="flex items-center gap-2 lg:hidden">
        <CloudIcon class="w-8 h-8 text-sky-400 flex-shrink-0" />
        <span class="text-xl font-bold truncate">Weather App</span>
      </div>

      <!-- Mobile close button -->
      <button
        class="p-2 -mr-2 rounded-md hover:bg-slate-800 transition-colors lg:hidden"
        @click="emit('navigate')"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>

      <!-- Desktop expanded state -->
      <template v-if="!isCollapsed">
        <span class="text-xl font-bold truncate hidden lg:block">Weather App</span>
        <button
          @click="toggleSidebar"
          class="p-2 rounded-md hover:bg-slate-800 transition-colors hidden lg:block"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
      </template>

      <!-- Desktop collapsed state - Clickable cloud icon -->
      <button
        v-if="isCollapsed && !isMobile"
        @click="toggleSidebar"
        class="p-2 rounded-md hover:bg-slate-800 transition-colors group relative hidden lg:block"
        title="Expand sidebar"
      >
        <CloudIcon class="w-10 h-10 text-sky-400 flex-shrink-0" />

        <!-- Small chevron indicator on hover -->
        <div
          class="absolute -right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <svg class="w-3 h-3 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </button>
    </div>

    <!-- User info -->
    <div v-if="authStore.user" class="px-4 py-3 border-b border-slate-800">
      <div v-if="!isCollapsed || isMobile">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-full bg-sky-600 flex items-center justify-center text-sm font-semibold flex-shrink-0"
          >
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">
              {{ authStore.user.full_name || authStore.user.email }}
            </p>
            <p class="text-xs text-slate-400 capitalize">{{ authStore.user.role }}</p>
          </div>
        </div>
      </div>
      <div v-else class="flex justify-center">
        <div
          class="w-10 h-10 rounded-full bg-sky-600 flex items-center justify-center text-sm font-semibold"
          :title="authStore.user.full_name || authStore.user.email"
        >
          {{ userInitials }}
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav
      class="flex-1 py-4"
      :class="isCollapsed && !isMobile ? 'overflow-visible' : 'overflow-y-auto'"
    >
      <ul class="space-y-1 px-2">
        <li v-for="item in visibleNavItems" :key="item.name">
          <RouterLink
            :to="item.to"
            class="flex items-center gap-3 px-4 py-3 lg:py-2 rounded-md transition-colors group relative"
            :class="[
              route.path === item.to
                ? 'bg-slate-800 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white',
              isCollapsed && !isMobile ? 'lg:justify-center' : '',
            ]"
            :title="isCollapsed && !isMobile ? item.label : ''"
            @click="emit('navigate')"
          >
            <svg
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="item.icon"
              />
            </svg>

            <span v-if="!isCollapsed || isMobile" class="truncate">{{ item.label }}</span>

            <!-- Tooltip for collapsed state (desktop only) -->
            <div
              v-if="isCollapsed && !isMobile"
              class="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-sm rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 hidden lg:block"
            >
              {{ item.label }}
            </div>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Logout button at bottom -->
    <div class="p-4 border-t border-slate-800">
      <button
        @click="handleLogout"
        class="w-full px-4 py-3 lg:py-2 rounded-md text-slate-300 hover:bg-red-900 hover:text-white transition-colors flex items-center gap-3 group relative"
        :class="isCollapsed && !isMobile ? 'lg:justify-center' : ''"
        :title="isCollapsed && !isMobile ? 'Logout' : ''"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
          />
        </svg>
        <span v-if="!isCollapsed || isMobile">Logout</span>

        <!-- Tooltip for collapsed state (desktop only) -->
        <div
          v-if="isCollapsed && !isMobile"
          class="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-sm rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 hidden lg:block"
        >
          Logout
        </div>
      </button>
    </div>
  </aside>
</template>
