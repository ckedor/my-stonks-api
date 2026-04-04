import { db, type CacheEntry } from '@/db'
import { computeHash } from '@/db/hash'

// ---------------------------------------------------------------------------
// Generic Stale-While-Revalidate engine
//
// 1. Read from IndexedDB cache (instant)
// 2. Hydrate store (UI updates immediately)
// 3. Fetch fresh data in the background
// 4. Compare hash of fresh vs cached
// 5. If different (or forced), update IndexedDB + store
// ---------------------------------------------------------------------------

export interface SWROptions<T> {
  /** Cache key in IndexedDB (e.g. "positions:42") */
  cacheKey: string
  /** Pure API call that returns the data */
  fetcher: () => Promise<T>
  /** Called with the data to hydrate the Zustand store */
  onHydrate: (data: T) => void
  /** Called to toggle the loading flag on the store */
  onLoadingChange: (loading: boolean) => void
  /** Bypass hash comparison and force overwrite */
  force?: boolean
}

export async function staleWhileRevalidate<T>(opts: SWROptions<T>): Promise<void> {
  const { cacheKey, fetcher, onHydrate, onLoadingChange, force = false } = opts

  // ---- Step 1: Read from IndexedDB ----
  let cached: CacheEntry | undefined
  try {
    cached = await db.cache.get(cacheKey)
  } catch {
    // IndexedDB may fail in private browsing – treat as cache miss
  }

  if (cached) {
    // ---- Step 2: Hydrate store from cache (instant) ----
    onHydrate(cached.data as T)
  } else {
    onLoadingChange(true)
  }

  // ---- Step 3: Background fetch ----
  try {
    const freshData = await fetcher()
    const freshHash = await computeHash(freshData)

    // ---- Step 4: Compare ----
    if (force || !cached || cached.hash !== freshHash) {
      // ---- Step 5: Persist + hydrate ----
      try {
        await db.cache.put({
          key: cacheKey,
          data: freshData,
          hash: freshHash,
          updatedAt: Date.now(),
        })
      } catch {
        // IndexedDB write failure is non-fatal
      }
      onHydrate(freshData)
    }
  } catch (error) {
    if (!cached) {
      // No cache fallback – propagate to caller
      onLoadingChange(false)
      throw error
    }
    // Silently use stale data when background fetch fails
    console.warn(`[SWR] Background revalidation failed for "${cacheKey}":`, error)
  }
}

// ---------------------------------------------------------------------------
// Helper: clear all cached data for a given portfolio
// ---------------------------------------------------------------------------
export async function clearPortfolioCache(portfolioId: number): Promise<void> {
  const keys = [
    `positions:${portfolioId}`,
    `returns:${portfolioId}`,
    `analysis:${portfolioId}`,
    `dividends:${portfolioId}`,
    `patrimony:${portfolioId}`,
    `trades:${portfolioId}`,
  ]
  await db.cache.bulkDelete(keys)
}
