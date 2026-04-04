import type { Dividend } from '@/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface DividendsState {
  dividends: Dividend[]
  loading: boolean

  setDividends: (dividends: Dividend[]) => void
  setLoading: (loading: boolean) => void
}

export const useDividendsStore = create<DividendsState>()(
  persist(
    (set) => ({
      dividends: [],
      loading: true,

      setDividends: (dividends) => set({ dividends, loading: false }),
      setLoading: (loading) => set({ loading }),
    }),
    {
      name: 'dividends-store',
      partialize: (state) => ({ dividends: state.dividends }),
      onRehydrateStorage: () => (state) => {
        if (state && state.dividends.length > 0) {
          state.loading = false
        }
      },
    },
  ),
)
