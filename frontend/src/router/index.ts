import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import DevicesPage from '@/pages/DevicePage.vue'
import DeviceFormPage from '@/pages/DeviceFormPage.vue' // Import the form
import OptionsPage from '@/pages/OptionsPage.vue'
import LoginPage from '@/pages/auth/LoginPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage,
      },
      {
        path: 'devices',
        name: 'Devices',
        component: DevicesPage,
      },
      // New Routes for Add/Edit
      {
        path: 'devices/new',
        name: 'DeviceAdd',
        component: DeviceFormPage,
      },
      {
        path: 'devices/:id',
        name: 'DeviceEdit',
        component: DeviceFormPage,
      },
      {
        path: 'options',
        name: 'Options',
        component: OptionsPage,
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
