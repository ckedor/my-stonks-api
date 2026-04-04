import { create } from 'zustand'

/**
 * Generic key-value data cache store for page-level SWR data.
 *
 * Used by pages that fetch specialised/filtered data (asset-class positions,
 * filtered patrimony, etc.) via the useCachedData hook.
 */

interface CacheSlice {
  data: unknown
  loading: boolean
}

export interface DataCacheState {
  entries: Record<string, CacheSlice>

  setData: (key: string, data: unknown) => void
  setLoading: (key: string, loading: boolean) => void
  clear: () => void
}

const DEFAULT_SLICE: CacheSlice = { data: null, loading: true }

export const useDataCacheStore = create<DataCacheState>()((set) => ({
  entries: {},

  setData: (key, data) =>
    set((s) => ({
      entries: { ...s.entries, [key]: { data, loading: false } },
    })),

  setLoading: (key, loading) =>
    set((s) => ({
      entries: {
        ...s.entries,
        [key]: { ...((s.entries[key] as CacheSlice | undefined) ?? DEFAULT_SLICE), loading },
      },
    })),

  clear: () => set({ entries: {} }),
}))
