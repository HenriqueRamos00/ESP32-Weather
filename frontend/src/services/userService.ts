import { apiClient } from '@/services/api'

export type UserRole = 'admin' | 'user'

export interface User {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  role: UserRole
  created_at: string
}

export interface UserCreate {
  email: string
  password: string
  full_name?: string | null
  role?: UserRole
}

export interface UserUpdate {
  email?: string
  full_name?: string | null
  password?: string
  role?: UserRole
  is_active?: boolean
}

export interface UserListResponse {
  users: User[]
  total: number
}

export const userService = {
  async getAll(skip = 0, limit = 100): Promise<UserListResponse> {
    const { data } = await apiClient.get<UserListResponse>('/users', {
      params: { skip, limit },
    })
    return data
  },

  async getById(id: number): Promise<User> {
    const { data } = await apiClient.get<User>(`/users/${id}`)
    return data
  },

  async getMe(): Promise<User> {
    const { data } = await apiClient.get<User>('/users/me')
    return data
  },

  async create(userData: UserCreate): Promise<User> {
    const { data } = await apiClient.post<User>('/users', userData)
    return data
  },

  async update(id: number, userData: UserUpdate): Promise<User> {
    const { data } = await apiClient.put<User>(`/users/${id}`, userData)
    return data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/users/${id}`)
  },
}
