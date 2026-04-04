import { create } from 'zustand'

interface TradeFormAsset {
  id: number
  ticker: string
  name: string
  asset_type_id: number
}

export interface TradeFormState {
  isOpen: boolean
  preSelectedAsset: TradeFormAsset | null

  openTradeForm: (asset?: TradeFormAsset | null) => void
  closeTradeForm: () => void
}

export const useTradeFormStore = create<TradeFormState>()((set) => ({
  isOpen: false,
  preSelectedAsset: null,

  openTradeForm: (asset) => set({ isOpen: true, preSelectedAsset: asset ?? null }),
  closeTradeForm: () => set({ isOpen: false, preSelectedAsset: null }),
}))
