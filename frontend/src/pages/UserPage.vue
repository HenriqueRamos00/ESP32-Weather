<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUsers } from '@/composables/useUsers'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import type { User, UserCreate, UserUpdate } from '@/services/userService'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import UserFormModal from '@/components/User/UserFormModal.vue'

const { users, total, loading, fetchUsers, createUser, updateUser, deleteUser } = useUsers()
const { success, error: showError } = useToast()
const authStore = useAuthStore()

const showFormModal = ref(false)
const showDeleteModal = ref(false)
const selectedUser = ref<User | null>(null)
const saving = ref(false)

onMounted(async () => {
  try {
    await fetchUsers()
  } catch (err) {
    showError('Failed to load users', err instanceof Error ? err.message : undefined)
  }
})

const openCreateModal = () => {
  selectedUser.value = null
  showFormModal.value = true
}

const openEditModal = (user: User) => {
  selectedUser.value = user
  showFormModal.value = true
}

const openDeleteModal = (user: User) => {
  selectedUser.value = user
  showDeleteModal.value = true
}

const handleSave = async (data: UserCreate | UserUpdate) => {
  saving.value = true
  try {
    if (selectedUser.value) {
      await updateUser(selectedUser.value.id, data as UserUpdate)
      success('User Updated', 'The user has been updated successfully')
    } else {
      await createUser(data as UserCreate)
      success('User Created', 'The new user has been added')
    }
    showFormModal.value = false
  } catch (err) {
    showError(
      selectedUser.value ? 'Update Failed' : 'Creation Failed',
      err instanceof Error ? err.message : undefined,
    )
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  if (!selectedUser.value) return

  // Prevent self-deletion
  if (selectedUser.value.id === authStore.user?.id) {
    showError('Cannot Delete', 'You cannot delete your own account')
    showDeleteModal.value = false
    return
  }

  saving.value = true
  try {
    await deleteUser(selectedUser.value.id)
    success('User Deleted', 'The user has been removed')
    showDeleteModal.value = false
  } catch (err) {
    showError('Delete Failed', err instanceof Error ? err.message : undefined)
  } finally {
    saving.value = false
  }
}

const getRoleBadgeClass = (role: string) => {
  return role === 'admin'
    ? 'bg-purple-500/20 text-purple-300 border-purple-500/30'
    : 'bg-sky-500/20 text-sky-300 border-sky-500/30'
}

const getStatusBadgeClass = (isActive: boolean) => {
  return isActive
    ? 'bg-green-500/20 text-green-300 border-green-500/30'
    : 'bg-red-500/20 text-red-300 border-red-500/30'
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-white">Users</h1>
        <p class="text-slate-400 text-sm mt-1">Manage user accounts and permissions</p>
      </div>
      <button
        class="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-md transition-colors"
        @click="openCreateModal"
      >
        + Add User
      </button>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading && users.length === 0" />

    <!-- User List -->
    <div v-else-if="users.length > 0" class="bg-slate-800 rounded-lg overflow-hidden">
      <table class="w-full">
        <thead class="bg-slate-900">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-medium text-slate-300">Email</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-slate-300">Full Name</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-slate-300">Role</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-slate-300">Status</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-slate-300">Created</th>
            <th class="px-4 py-3 text-right text-sm font-medium text-slate-300">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-700">
          <tr v-for="user in users" :key="user.id" class="hover:bg-slate-700/50">
            <td class="px-4 py-3 text-sm text-white">{{ user.email }}</td>
            <td class="px-4 py-3 text-sm text-slate-300">
              {{ user.full_name || '—' }}
            </td>
            <td class="px-4 py-3">
              <span
                class="inline-block px-2 py-1 text-xs font-medium rounded border capitalize"
                :class="getRoleBadgeClass(user.role)"
              >
                {{ user.role }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                class="inline-block px-2 py-1 text-xs font-medium rounded border"
                :class="getStatusBadgeClass(user.is_active)"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-slate-400">
              {{ new Date(user.created_at).toLocaleDateString() }}
            </td>
            <td class="px-4 py-3 text-right">
              <button
                class="text-sky-400 hover:text-sky-300 text-sm mr-3"
                @click="openEditModal(user)"
              >
                Edit
              </button>
              <button
                class="text-red-400 hover:text-red-300 text-sm"
                :disabled="user.id === authStore.user?.id"
                :class="{ 'opacity-50 cursor-not-allowed': user.id === authStore.user?.id }"
                @click="openDeleteModal(user)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="px-4 py-3 bg-slate-900 text-sm text-slate-400">
        Total: {{ total }} user{{ total !== 1 ? 's' : '' }}
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="bg-slate-800 rounded-lg p-8 text-center text-slate-400">No users found</div>

    <!-- Form Modal -->
    <UserFormModal
      :show="showFormModal"
      :user="selectedUser"
      :saving="saving"
      @close="showFormModal = false"
      @save="handleSave"
    />

    <!-- Delete Confirmation -->
    <ConfirmModal
      :show="showDeleteModal"
      title="Delete User"
      :message="`Are you sure you want to delete ${selectedUser?.email}? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-class="bg-red-600 hover:bg-red-700"
      @confirm="handleDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>
