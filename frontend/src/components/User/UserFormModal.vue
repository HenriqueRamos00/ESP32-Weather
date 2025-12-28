<script setup lang="ts">
import { ref, watch } from 'vue'
import type { User, UserCreate, UserUpdate } from '@/services/userService'

interface Props {
  show: boolean
  user?: User | null
  saving?: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'save', data: UserCreate | UserUpdate): void
}

const props = withDefaults(defineProps<Props>(), {
  user: null,
  saving: false,
})

const emit = defineEmits<Emits>()

const formData = ref({
  email: '',
  full_name: '',
  password: '',
  role: 'user' as 'admin' | 'user',
  is_active: true,
})

watch(
  () => props.show,
  (show) => {
    if (show) {
      if (props.user) {
        // Edit mode
        formData.value = {
          email: props.user.email,
          full_name: props.user.full_name || '',
          password: '', // leave empty for no password change
          role: props.user.role,
          is_active: props.user.is_active,
        }
      } else {
        // Create mode
        formData.value = {
          email: '',
          full_name: '',
          password: '',
          role: 'user',
          is_active: true,
        }
      }
    }
  },
)

const handleSubmit = () => {
  if (props.user) {
    // Update
    const updateData: UserUpdate = {
      email: formData.value.email,
      full_name: formData.value.full_name || null,
      role: formData.value.role,
      is_active: formData.value.is_active,
    }
    if (formData.value.password) {
      updateData.password = formData.value.password
    }
    emit('save', updateData)
  } else {
    // Create
    const createData: UserCreate = {
      email: formData.value.email,
      password: formData.value.password,
      full_name: formData.value.full_name || null,
      role: formData.value.role,
    }
    emit('save', createData)
  }
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-0 sm:p-4"
    @click.self="emit('close')"
  >
    <div
      class="bg-slate-800 rounded-t-lg sm:rounded-lg p-6 w-full sm:max-w-md shadow-xl max-h-[90vh] overflow-y-auto"
    >
      <h2 class="text-xl font-bold text-white mb-4">
        {{ user ? 'Edit User' : 'Create User' }}
      </h2>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <!-- Email -->
        <div>
          <label class="block text-sm text-slate-300 mb-1" for="email">Email</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <!-- Full Name -->
        <div>
          <label class="block text-sm text-slate-300 mb-1" for="full_name">Full Name</label>
          <input
            id="full_name"
            v-model="formData.full_name"
            type="text"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm text-slate-300 mb-1" for="password">
            Password
            <span v-if="user" class="text-xs text-slate-500">(leave blank to keep current)</span>
          </label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            :required="!user"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <!-- Role -->
        <div>
          <label class="block text-sm text-slate-300 mb-1" for="role">Role</label>
          <select
            id="role"
            v-model="formData.role"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <!-- Active Status (only on edit) -->
        <div v-if="user" class="flex items-center gap-2">
          <input
            id="is_active"
            v-model="formData.is_active"
            type="checkbox"
            class="w-4 h-4 rounded bg-slate-900 border-slate-700 text-sky-600 focus:ring-2 focus:ring-sky-500"
          />
          <label for="is_active" class="text-sm text-slate-300">Active</label>
        </div>

        <!-- Actions -->
        <div class="flex flex-col-reverse sm:flex-row gap-3 pt-2">
          <button
            type="button"
            :disabled="saving"
            class="w-full sm:flex-1 px-4 py-3 sm:py-2 rounded-md bg-slate-700 hover:bg-slate-600 text-white transition-colors disabled:opacity-50"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="w-full sm:flex-1 px-4 py-3 sm:py-2 rounded-md bg-sky-600 hover:bg-sky-700 text-white transition-colors disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : user ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
