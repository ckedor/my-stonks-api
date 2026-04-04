import { staleWhileRevalidate } from '@/actions/sync';
import { useDataCacheStore } from '@/stores/data-cache';
import { useEffect, useRef } from 'react';

/**
 * React hook for page-level SWR data.
 *
 * Reads from IndexedDB cache on mount, hydrates a generic Zustand store,
 * then background-fetches and updates if hash differs.
 *
 * @param key   Cache key (e.g. "stocks-br:positions:42")
 * @param fetcher  Pure async function returning the data
 * @param options.enabled  If false, skip fetching (default: true)
 */
export function useCachedData<T>(
  key: string | null,
  fetcher: () => Promise<T>,
  options?: { enabled?: boolean },
): { data: T | null; loading: boolean } {
  const enabled = options?.enabled ?? true
  const prevKeyRef = useRef<string | null>(null)

  useEffect(() => {
    if (!enabled || !key) return
    if (prevKeyRef.current === key) return
    prevKeyRef.current = key

    const store = useDataCacheStore.getState()
    store.setLoading(key, true)

    staleWhileRevalidate<T>({
      cacheKey: key,
      fetcher,
      onLoadingChange: (loading) => useDataCacheStore.getState().setLoading(key, loading),
      onHydrate: (data) => useDataCacheStore.getState().setData(key, data),
    }).catch(console.error)
  }, [key, enabled, fetcher])

  const entry = useDataCacheStore((s) => s.entries[key ?? ''])

  return {
    data: (entry?.data as T) ?? null,
    loading: entry?.loading ?? true,
  }
}
