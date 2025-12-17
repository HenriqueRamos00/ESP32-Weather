import { ref, readonly } from 'vue'
import { userService, type User, type UserCreate, type UserUpdate } from '@/services/userService'

export function useUsers() {
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchUsers = async (skip = 0, limit = 100) => {
    loading.value = true
    error.value = null
    try {
      const response = await userService.getAll(skip, limit)
      users.value = response.users
      total.value = response.total
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch users'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchUser = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const user = await userService.getById(id)
      currentUser.value = user
      return user
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch user'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData: UserCreate) => {
    loading.value = true
    error.value = null
    try {
      const newUser = await userService.create(userData)
      users.value.push(newUser)
      total.value++
      return newUser
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create user'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (id: number, userData: UserUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedUser = await userService.update(id, userData)
      const index = users.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser
      }
      return updatedUser
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update user'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteUser = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await userService.delete(id)
      users.value = users.value.filter((u) => u.id !== id)
      total.value--
      if (currentUser.value?.id === id) {
        currentUser.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete user'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentUser = () => {
    currentUser.value = null
  }

  return {
    users: readonly(users),
    currentUser: readonly(currentUser),
    total: readonly(total),
    loading: readonly(loading),
    error: readonly(error),
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    clearError,
    clearCurrentUser,
  }
}
