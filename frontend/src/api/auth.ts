import { apiRequest } from './client'
import type { LoginResponse, UserPublic } from '../types/api'

export function login(username: string, password: string): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    body: { username, password },
  })
}

export function getMe(token: string): Promise<UserPublic> {
  return apiRequest<UserPublic>('/auth/me', { token })
}
