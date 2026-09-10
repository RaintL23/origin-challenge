import type { UserPublic } from '../types/api'

const TOKEN_KEY = 'challenge_acciones_token'
const USER_KEY = 'challenge_acciones_user'

export function loadToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function loadUser(): UserPublic | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserPublic
  } catch {
    return null
  }
}

export function saveSession(token: string, user: UserPublic): void {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
