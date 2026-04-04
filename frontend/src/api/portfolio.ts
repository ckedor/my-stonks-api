import api from '@/lib/api'
import type { AssetAnalysis, CategoryReturnEntry, Dividend, PatrimonyEntry, Portfolio, PortfolioPositionEntry, PortfolioReturnEntry, ReturnsEntry, Trade } from '@/types'

// ---------------------------------------------------------------------------
// Pure API functions – no state management, no side-effects beyond the fetch.
// ---------------------------------------------------------------------------

export const fetchPortfolios = (): Promise<Portfolio[]> =>
  api.get<Portfolio[]>('/portfolio/list').then((r) => r.data)

export const fetchPositions = (portfolioId: number, currency: string = 'BRL'): Promise<PortfolioPositionEntry[]> =>
  api.get<PortfolioPositionEntry[]>(`/portfolio/${portfolioId}/position`, { params: { currency } }).then((r) => r.data)

export const fetchDividends = (portfolioId: number, currency: string = 'BRL'): Promise<Dividend[]> =>
  api.get<Dividend[]>(`/portfolio/dividends/${portfolioId}`, { params: { currency } }).then((r) => r.data)

export const fetchPatrimony = (portfolioId: number, currency: string = 'BRL'): Promise<PatrimonyEntry[]> =>
  api.get<PatrimonyEntry[]>(`/portfolio/${portfolioId}/patrimony_evolution`, { params: { currency } }).then((r) => r.data).catch((err) => {
    if (err?.response?.status === 404) return []
    throw err
  })

export const fetchTrades = (portfolioId: number): Promise<Trade[]> =>
  api.get<Trade[]>(`/portfolio/transaction/${portfolioId}`).then((r) => r.data)

export const fetchReturns = (portfolioId: number, currency: string = 'BRL'): Promise<PortfolioReturnEntry[]> =>
  api.get<PortfolioReturnEntry[]>(`/portfolio/${portfolioId}/returns`, { params: { currency } }).then((r) => r.data ?? [])

export const fetchCategoryReturns = (
  portfolioId: number,
  categoryId?: number,
  mostRecent?: boolean,
  currency: string = 'BRL',
): Promise<CategoryReturnEntry[]> => {
  const params = new URLSearchParams()
  if (categoryId != null) params.set('category_id', String(categoryId))
  if (mostRecent) params.set('most_recent', 'true')
  params.set('currency', currency)
  const qs = params.toString()
  return api.get<CategoryReturnEntry[]>(`/portfolio/${portfolioId}/category/returns${qs ? `?${qs}` : ''}`).then((r) => r.data ?? [])
}

export const fetchCategoryAnalysis = (portfolioId: number, categoryId: number, currency: string = 'BRL'): Promise<AssetAnalysis> =>
  api.get<AssetAnalysis>(`/portfolio/${portfolioId}/category/${categoryId}/analysis`, { params: { currency } }).then((r) => r.data)

export const fetchAssetReturns = (portfolioId: number, assetId: number, currency: string = 'BRL'): Promise<Record<string, ReturnsEntry[]>> =>
  api.get(`/portfolio/${portfolioId}/asset/${assetId}/returns`, { params: { currency } }).then((r) => {
    const rows: Record<string, any>[] = r.data?.data ?? r.data ?? []
    // df_response returns [{date, TICKER: value, ...}, ...] — pivot to {TICKER: [{date, value}]}
    const result: Record<string, ReturnsEntry[]> = {}
    for (const row of rows) {
      const { date, ...rest } = row
      for (const [ticker, val] of Object.entries(rest)) {
        if (val == null) continue
        if (!result[ticker]) result[ticker] = []
        result[ticker].push({ date, value: val as number })
      }
    }
    return result
  })

export const fetchAssetDetails = (portfolioId: number, assetId: number, currency: string = 'BRL') =>
  api.get(`/portfolio/${portfolioId}/asset/${assetId}/details`, { params: { currency } }).then((r) => r.data)

export const fetchAssetAnalysis = (portfolioId: number, assetId: number, currency: string = 'BRL'): Promise<AssetAnalysis | null> =>
  api.get<AssetAnalysis>(`/portfolio/${portfolioId}/asset/${assetId}/analysis`, { params: { currency } }).then((r) => r.data).catch(() => null)

export const fetchAnalysis = (portfolioId: number, currency: string = 'BRL'): Promise<AssetAnalysis> =>
  api.get<AssetAnalysis>(`/portfolio/${portfolioId}/analysis`, { params: { currency } }).then((r) => r.data)

export const consolidatePortfolio = (portfolioId: number): Promise<void> =>
  api.post(`/portfolio/${portfolioId}/consolidate`).then(() => undefined)

export const recalculateAssetPosition = (portfolioId: number, assetId: number): Promise<void> =>
  api.post(`/portfolio/${portfolioId}/recalculate_asset_position`, null, { params: { asset_id: assetId } }).then(() => undefined)
