import type { PortfolioPositionEntry } from '@/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface PositionsState {
  positions: PortfolioPositionEntry[]
  loading: boolean

  setPositions: (positions: PortfolioPositionEntry[]) => void
  setLoading: (loading: boolean) => void
}

export const usePositionsStore = create<PositionsState>()(
  persist(
    (set) => ({
      positions: [],
      loading: true,

      setPositions: (positions) => set({ positions, loading: false }),
      setLoading: (loading) => set({ loading }),
    }),
    {
      name: 'positions-store',
      partialize: (state) => ({ positions: state.positions }),
      onRehydrateStorage: () => (state) => {
        if (state && state.positions.length > 0) {
          state.loading = false
        }
      },
    },
  ),
)
