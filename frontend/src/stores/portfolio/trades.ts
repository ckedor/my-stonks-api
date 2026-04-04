import type { Trade } from '@/types'
import { create } from 'zustand'

export interface TradesState {
  trades: Trade[]
  loading: boolean

  setTrades: (trades: Trade[]) => void
  setLoading: (loading: boolean) => void
}

export const useTradesStore = create<TradesState>()((set) => ({
  trades: [],
  loading: true,

  setTrades: (trades) => set({ trades, loading: false }),
  setLoading: (loading) => set({ loading }),
}))
