import api from '@/lib/api'
import type { ReturnsEntry } from '@/types'

export type BenchmarksPayload = Record<string, ReturnsEntry[]>

export const fetchBenchmarks = (): Promise<BenchmarksPayload> =>
  api.get<BenchmarksPayload>('/market_data/indexes/time_series').then((r) => r.data)
