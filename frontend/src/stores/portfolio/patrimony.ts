import type { PatrimonyEntry } from '@/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface PatrimonyState {
  patrimony: PatrimonyEntry[]
  loading: boolean

  setPatrimony: (patrimony: PatrimonyEntry[]) => void
  setLoading: (loading: boolean) => void
}

export const usePatrimonyStore = create<PatrimonyState>()(
  persist(
    (set) => ({
      patrimony: [],
      loading: true,

      setPatrimony: (patrimony) => set({ patrimony, loading: false }),
      setLoading: (loading) => set({ loading }),
    }),
    {
      name: 'patrimony-store',
      partialize: (state) => ({ patrimony: state.patrimony }),
      onRehydrateStorage: () => (state) => {
        if (state && state.patrimony.length > 0) {
          state.loading = false
        }
      },
    },
  ),
)
