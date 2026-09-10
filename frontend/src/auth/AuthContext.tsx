import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { login as loginRequest } from '../api/auth'
import type { UserPublic } from '../types/api'
import { clearSession, loadToken, loadUser, saveSession } from './storage'

interface AuthContextValue {
  token: string | null
  user: UserPublic | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => loadToken())
  const [user, setUser] = useState<UserPublic | null>(() => loadUser())

  const login = useCallback(async (username: string, password: string) => {
    const response = await loginRequest(username, password)
    saveSession(response.access_token, response.user)
    setToken(response.access_token)
    setUser(response.user)
  }, [])

  const logout = useCallback(() => {
    clearSession()
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token, user, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return ctx
}
