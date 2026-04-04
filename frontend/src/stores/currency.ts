import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Currency = 'BRL' | 'USD'

interface CurrencyState {
  currency: Currency
  setCurrency: (currency: Currency) => void
  toggleCurrency: () => void
}

export const useCurrencyStore = create<CurrencyState>()(
  persist(
    (set) => ({
      currency: 'BRL',
      setCurrency: (currency) => set({ currency }),
      toggleCurrency: () =>
        set((s) => ({ currency: s.currency === 'BRL' ? 'USD' : 'BRL' })),
    }),
    { name: 'currency-store' },
  ),
)
