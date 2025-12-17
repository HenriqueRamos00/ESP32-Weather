import { apiClient } from '@/services/api'

export interface TokenResponse {
  access_token: string
  token_type: string
}

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const form = new URLSearchParams()
    form.append('username', email) // OAuth2 uses "username", we send email here
    form.append('password', password)

    const { data } = await apiClient.post<TokenResponse>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },
}
