import { create } from 'zustand'

interface UserData {
  email: string
  is_admin: boolean
}

export interface AuthState {
  user: UserData | null
  isAuthenticated: boolean
  isLoading: boolean

  setUser: (user: UserData | null) => void
  setLoading: (loading: boolean) => void
  reset: () => void
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
  setLoading: (isLoading) => set({ isLoading }),
  reset: () => set({ user: null, isAuthenticated: false, isLoading: false }),
}))
