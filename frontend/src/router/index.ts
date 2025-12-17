import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import DevicesPage from '@/pages/DevicePage.vue'
import DeviceFormPage from '@/pages/DeviceFormPage.vue'
import UserPage from '@/pages/UserPage.vue'
import OptionsPage from '@/pages/OptionsPage.vue'
import LoginPage from '@/pages/auth/LoginPage.vue'
import { useAuthStore, type UserRole } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { roles: ['admin', 'user'] as UserRole[] },
      },
      {
        path: 'devices',
        name: 'Devices',
        component: DevicesPage,
        meta: { roles: ['admin'] as UserRole[] },
      },
      {
        path: 'devices/new',
        name: 'DeviceAdd',
        component: DeviceFormPage,
        meta: { roles: ['admin'] as UserRole[] },
      },
      {
        path: 'devices/:id',
        name: 'DeviceEdit',
        component: DeviceFormPage,
        meta: { roles: ['admin'] as UserRole[] },
      },
      {
        path: 'users',
        name: 'Users',
        component: UserPage,
        meta: { roles: ['admin'] as UserRole[] },
      },
      {
        path: 'options',
        name: 'Options',
        component: OptionsPage,
        meta: { roles: ['admin'] as UserRole[] },
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false, guestOnly: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Global guard
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // On first navigation, restore from localStorage
  if (!auth.initialized) {
    auth.initFromStorage()
  }

  const requiresAuth = to.meta.requiresAuth ?? true

  if (requiresAuth && !auth.isAuthenticated) {
    return next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    // prevent logged-in users from going to login again
    return next({ name: 'Dashboard' })
  }

  const allowedRoles = (to.meta.roles as UserRole[] | undefined) ?? undefined
  if (requiresAuth && allowedRoles && auth.user && !allowedRoles.includes(auth.user.role)) {
    // user is logged in but not allowed to see this route
    return next({ name: 'Dashboard' })
  }

  next()
})

export default router
