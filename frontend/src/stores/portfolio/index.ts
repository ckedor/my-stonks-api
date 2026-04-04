import type { Portfolio } from '@/types'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface PortfolioState {
  portfolios: Portfolio[]
  selectedPortfolio: Portfolio | null
  loading: boolean

  setPortfolios: (portfolios: Portfolio[]) => void
  setSelectedPortfolio: (p: Portfolio) => void
  setLoading: (loading: boolean) => void
}

export const usePortfolioStore = create<PortfolioState>()(
  persist(
    (set) => ({
      portfolios: [],
      selectedPortfolio: null,
      loading: true,

      setPortfolios: (portfolios) => set({ portfolios }),

      setSelectedPortfolio: (p) => {
        localStorage.setItem('selectedPortfolioId', String(p.id))
        set({ selectedPortfolio: p })
      },

      setLoading: (loading) => set({ loading }),
    }),
    {
      name: 'portfolio-store',
      partialize: (state) => ({
        portfolios: state.portfolios,
        selectedPortfolio: state.selectedPortfolio,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && state.portfolios.length > 0) {
          state.loading = false
        }
      },
    },
  ),
)
