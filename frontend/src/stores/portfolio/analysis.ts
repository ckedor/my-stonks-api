import type { AssetAnalysis } from '@/types'
import { create } from 'zustand'

export interface AnalysisState {
  analysis: AssetAnalysis | null
  loading: boolean

  setAnalysis: (analysis: AssetAnalysis | null) => void
  setLoading: (loading: boolean) => void
}

export const useAnalysisStore = create<AnalysisState>()((set) => ({
  analysis: null,
  loading: true,

  setAnalysis: (analysis) => set({ analysis, loading: false }),
  setLoading: (loading) => set({ loading }),
}))
