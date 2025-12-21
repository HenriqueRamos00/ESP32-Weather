<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useSettings } from '@/composables/useSettings'
import { useToast } from '@/composables/useToast'
import SettingCard from '@/components/Settings/SettingCard.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const { settings, loading, fetchSettings, updateSetting, clearError } = useSettings()
const { success, error: showError } = useToast()

// Get specific setting by key
const offlineThresholdSetting = computed(() => {
  return settings.value.find((s) => s.key === 'offline_threshold_seconds')
})

const offlineThresholdValue = computed(() => {
  if (!offlineThresholdSetting.value) return 300
  return parseInt(offlineThresholdSetting.value.value, 10)
})

const loadSettings = async () => {
  clearError()
  try {
    await fetchSettings()
  } catch (err) {
    showError('Failed to load settings', err instanceof Error ? err.message : undefined)
  }
}

const handleUpdateOfflineThreshold = async (value: string) => {
  clearError()
  try {
    await updateSetting('offline_threshold_seconds', { value })
    success('Settings saved', 'Offline threshold updated successfully')
  } catch (err) {
    showError('Failed to save settings', err instanceof Error ? err.message : undefined)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<template>
  <div class="w-full max-w-full">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white mb-2">Options</h1>
      <p class="text-slate-400">Configure system settings and preferences</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading && settings.length === 0" class="flex justify-center py-12">
      <LoadingSpinner size="lg" text="Loading settings..." />
    </div>

    <!-- Settings Content -->
    <div v-if="!loading || settings.length > 0" class="space-y-6">
      <!-- Device Settings Section -->
      <section>
        <h2 class="text-xl font-semibold text-white mb-4">Device Settings</h2>

        <div class="space-y-4">
          <SettingCard
            v-if="offlineThresholdSetting"
            title="Offline Threshold"
            description="Number of seconds of inactivity before a device is considered offline"
            :value="offlineThresholdValue"
            type="number"
            :min="1"
            :step="1"
            suffix="seconds"
            :disabled="loading"
            @update="handleUpdateOfflineThreshold"
          />

          <div
            v-else
            class="bg-slate-900 border border-slate-800 rounded-lg p-6 text-center text-slate-400"
          >
            <p>No device settings available</p>
          </div>
        </div>
      </section>

      <!-- Future sections can be added here -->
      <!--
      <section>
        <h2 class="text-xl font-semibold text-white mb-4">Notification Settings</h2>
        <div class="space-y-4">
          <SettingCard
            title="Email Notifications"
            description="Receive email notifications for device alerts"
            :value="emailNotifications"
            type="text"
            @update="handleUpdateEmailNotifications"
          />
        </div>
      </section>
      -->
    </div>
  </div>
</template>
