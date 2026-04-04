// src/components/PortfolioReturnsChart.tsx
import { usePortfolioStore } from '@/stores/portfolio'
import { useReturnsStore } from '@/stores/portfolio/returns'
import { Box, Checkbox, CircularProgress, MenuItem, Select, Stack, Typography, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
import { useEffect, useMemo, useState } from 'react'
import {
    CartesianGrid,
    ComposedChart,
    Legend,
    Line,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

dayjs.extend(isSameOrAfter)

interface Props {
  size: number
  selectedCategory?: string
  selectedBenchmark?: string
  selectedAssets?: string[]
  defaultRange?: string
  onRangeChange?: (range: string) => void
  onCurveChange?: (curve: { kind: 'category' | 'benchmark' | 'asset'; key: string }) => void
}

const mapDisplayName = (key: string) => (key === 'portfolio' ? 'Carteira' : key)
const mapOriginalKey = (label: string) => (label === 'Carteira' ? 'portfolio' : label)

export default function PortfolioReturnsChart({
  size,
  selectedCategory,
  selectedBenchmark,
  selectedAssets = [],
  defaultRange,
  onRangeChange,
  onCurveChange,
}: Props) {
  const { categoryReturns, assetReturns, benchmarks, loading } = useReturnsStore()
  const selectedPortfolio = usePortfolioStore(s => s.selectedPortfolio)
  const userCategories = selectedPortfolio?.custom_categories ?? []

  const theme = useTheme()
  const gridColor = theme.palette.chart.grid
  const labelColor = theme.palette.chart.label

  const COLORS: Record<string, string> = {
    Carteira: theme.palette.primary.main,
    CDI: theme.palette.secondary.main,
    IFIX: '#00bc8c',
    'S&P500': '#e74c3c',
    IBOVESPA: '#A9A92A',
    IPCA: '#8e44ad',
    'USD/BRL': '#2980b9',
  }

  const [selectedCategories, setSelectedCategories] = useState<string[]>(
    selectedCategory ? [mapOriginalKey(selectedCategory)] : []
  )
  const [selectedBenchmarks, setSelectedBenchmarks] = useState<string[]>(
    selectedBenchmark ? [selectedBenchmark] : []
  )
  const [selectedAssetKeys, setSelectedAssetKeys] = useState<string[]>(selectedAssets)
  const [range, setRange] = useState(defaultRange)

  useEffect(() => {
    setSelectedCategories(selectedCategory ? [mapOriginalKey(selectedCategory)] : [])
  }, [selectedCategory])

  useEffect(() => {
    setSelectedBenchmarks(selectedBenchmark ? [selectedBenchmark] : [])
  }, [selectedBenchmark])

  useEffect(() => {
    setSelectedAssetKeys(selectedAssets)
  }, [selectedAssets.join(',')])

  const categoryColorMap = useMemo(() => {
    const map: Record<string, string> = {}
    userCategories.forEach((cat) => {
      map[cat.name] = cat.color
    })
    return map
  }, [userCategories])

  const allDates = useMemo(() => {
    const dateSet = new Set<string>()
    // Include dates from all data sources
    for (const cat of selectedCategories) {
      (categoryReturns[cat] || []).forEach((d) => dateSet.add(d.date))
    }
    for (const asset of selectedAssetKeys) {
      (assetReturns[asset] || []).forEach((d) => dateSet.add(d.date))
    }
    for (const bm of selectedBenchmarks) {
      (benchmarks[bm] || []).forEach((d) => dateSet.add(d.date))
    }
    return Array.from(dateSet).sort()
  }, [categoryReturns, assetReturns, benchmarks, selectedCategories, selectedAssetKeys, selectedBenchmarks])

  // Find the latest "first date" among all selected series so all curves start at 0
  const latestSeriesStart = useMemo(() => {
    const firstDates: string[] = []
    for (const cat of selectedCategories) {
      const series = categoryReturns[cat]
      if (series?.length) firstDates.push([...series].sort((a, b) => a.date.localeCompare(b.date))[0].date)
    }
    for (const asset of selectedAssetKeys) {
      const series = assetReturns[asset]
      if (series?.length) firstDates.push([...series].sort((a, b) => a.date.localeCompare(b.date))[0].date)
    }
    for (const bm of selectedBenchmarks) {
      const series = benchmarks[bm]
      if (series?.length) firstDates.push([...series].sort((a, b) => a.date.localeCompare(b.date))[0].date)
    }
    // Latest first date = all curves will have data from this point
    return firstDates.length ? firstDates.sort().at(-1)! : null
  }, [categoryReturns, assetReturns, benchmarks, selectedCategories, selectedAssetKeys, selectedBenchmarks])

  const filteredDates = useMemo(() => {
    const today = dayjs()
    let from: dayjs.Dayjs
    switch (range) {
      case 'ytd':
        from = today.startOf('year')
        break
      case '1y':
        from = today.subtract(1, 'year')
        break
      case '2y':
        from = today.subtract(2, 'year')
        break
      case '3y':
        from = today.subtract(3, 'year')
        break
      case '4y':
        from = today.subtract(4, 'year')
        break
      case '5y':
        from = today.subtract(5, 'year')
        break
      case 'max':
      default:
        from = latestSeriesStart ? dayjs(latestSeriesStart) : dayjs('1900-01-01')
    }
    return allDates.filter((date) => dayjs(date).isSameOrAfter(from))
  }, [allDates, range, latestSeriesStart])

  const normalizeReturns = (series: { date: string; value: number }[], dates: string[]) => {
    if (!dates.length) return []

    // ordene a série uma vez
    const sorted = [...series].sort((a, b) => dayjs(a.date).unix() - dayjs(b.date).unix())
    const valuesMap = new Map(sorted.map((p) => [p.date, p.value]))

    const startDate = dates[0]

    // baseValue: último valor conhecido em <= startDate (se não existir, 0)
    let baseValue = 0
    for (let i = sorted.length - 1; i >= 0; i--) {
      if (!dayjs(sorted[i].date).isAfter(startDate)) {
        baseValue = sorted[i].value
        break
      }
    }

    // “last known” para forward-fill ao longo do range
    let lastKnown = baseValue

    return dates.map((date) => {
      if (valuesMap.has(date)) lastKnown = valuesMap.get(date) as number

      // rebasing correto (evita b <= -1)
      const denom = 1 + baseValue
      const numer = 1 + lastKnown
      const rebased = denom > 0 ? (numer / denom) - 1 : 0

      return { date, value: rebased }
    })
  }


  const data = useMemo(() => {
    const map: Record<string, any> = {}
    filteredDates.forEach((date) => {
      map[date] = { date }
    })
    for (const cat of selectedCategories) {
      const series = normalizeReturns(categoryReturns[cat] || [], filteredDates)
      for (const { date, value } of series) {
        if (map[date]) map[date][cat] = value * 100
      }
    }
    for (const asset of selectedAssetKeys) {
      const series = normalizeReturns(assetReturns[asset] || [], filteredDates)
      for (const { date, value } of series) {
        if (map[date]) map[date][asset] = value * 100
      }
    }
    for (const bm of selectedBenchmarks) {
      const series = benchmarks[bm] || []
      const normalized = normalizeReturns(series, filteredDates)
      for (const { date, value } of normalized) {
        if (map[date]) map[date][bm] = value * 100
      }
    }
    return Object.values(map).sort((a, b) => dayjs(a.date).unix() - dayjs(b.date).unix())
  }, [
    categoryReturns,
    assetReturns,
    benchmarks,
    selectedCategories,
    selectedAssetKeys,
    selectedBenchmarks,
    filteredDates,
  ])

  const allKeys = [...selectedCategories, ...selectedBenchmarks, ...selectedAssetKeys]
  const values = data.flatMap((d) => allKeys.map((k) => (typeof d[k] === 'number' ? d[k] : 0)))
  const min = values.length ? Math.min(...values) : 0
  const max = values.length ? Math.max(...values) : 0
  const padding = (max - min) * 0.1
  const upper = Math.ceil((max + padding) / 10) * 10
  const yTicks: number[] = []
  for (let i = 0; i <= upper; i += 10) yTicks.push(i)

  const currentYear = dayjs().year()
  const totalMonths = allDates.length
    ? dayjs(allDates.at(-1) as string).diff(dayjs(allDates[0] as string), 'month')
    : 0
  const totalYears = Math.floor(totalMonths / 12)
  const ranges = useMemo(() => {
    const base = [
      { label: 'Max', value: 'max' },
      { label: `${currentYear}`, value: 'ytd' },
    ]
    for (let y = 1; y <= 5; y++) {
      if (y <= totalYears) base.push({ label: `${y}Y`, value: `${y}y` })
    }
    return base
  }, [totalYears, currentYear])

  const xTicks = useMemo(() => {
    const ticks: string[] = []

    filteredDates.forEach((date) => {
      const d = dayjs(date)
      if (d.date() === 1) {
        ticks.push(date)
      }
    })

    return ticks.length ? ticks : filteredDates
  }, [filteredDates])

  return (
    <Box sx={{ p: 2 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1} mr={5}>
        <Box>
          {/* Categorias */}
          <Select
            multiple
            value={selectedCategories}
            onChange={(e) => {
              const value = e.target.value
              const arr = typeof value === 'string' ? value.split(',') : (value as string[])
              setSelectedCategories(arr)
              if (arr.length && onCurveChange) {
                const lastKey = arr[arr.length - 1]
                onCurveChange({ kind: 'category', key: lastKey })
              }
            }}
            variant="standard"
            size="small"
            sx={{ minWidth: 50, ml: 1, fontSize: 14 }}
            renderValue={(selected) => selected.map(mapDisplayName).join(', ')}
          >
            {Object.keys(categoryReturns).map((cat) => (
              <MenuItem key={cat} value={cat}>
                <Checkbox checked={selectedCategories.includes(cat)} size="small" />
                <Typography variant="body2">{mapDisplayName(cat)}</Typography>
              </MenuItem>
            ))}
          </Select>

          {/* Benchmarks */}
          <Select
            multiple
            value={selectedBenchmarks}
            onChange={(e) => {
              const value = e.target.value
              const arr = typeof value === 'string' ? value.split(',') : (value as string[])
              setSelectedBenchmarks(arr)
              if (arr.length && onCurveChange) {
                const lastKey = arr[arr.length - 1]
                onCurveChange({ kind: 'benchmark', key: lastKey })
              }
            }}
            variant="standard"
            size="small"
            sx={{ minWidth: 50, ml: 2, fontSize: 14 }}
            renderValue={(selected) => selected.join(', ')}
          >
            {Object.keys(benchmarks).map((key) => (
              <MenuItem key={key} value={key}>
                <Checkbox checked={selectedBenchmarks.includes(key)} size="small" />
                <Typography variant="body2">{key}</Typography>
              </MenuItem>
            ))}
          </Select>

          {/* Ativos */}
          <Select
            multiple
            value={selectedAssetKeys}
            onChange={(e) => {
              const value = e.target.value
              const arr = typeof value === 'string' ? value.split(',') : (value as string[])
              setSelectedAssetKeys(arr)
              if (arr.length && onCurveChange) {
                const lastKey = arr[arr.length - 1]
                onCurveChange({ kind: 'asset', key: lastKey })
              }
            }}
            variant="standard"
            size="small"
            sx={{ minWidth: 50, ml: 2, fontSize: 14 }}
            renderValue={(selected) => selected.join(', ')}
          >
            {Object.keys(assetReturns).map((key) => (
              <MenuItem key={key} value={key}>
                <Checkbox checked={selectedAssetKeys.includes(key)} size="small" />
                <Typography variant="body2">{key}</Typography>
              </MenuItem>
            ))}
          </Select>
        </Box>

        {/* Timeframes */}
        <Stack direction="row" spacing={1}>
          {ranges.map((r) => (
            <Typography
              key={r.value}
              onClick={() => {
                setRange(r.value)
                onRangeChange?.(r.value)
              }}
              sx={{ cursor: 'pointer', fontWeight: range === r.value ? 700 : 400, fontSize: 13 }}
            >
              {r.label}
            </Typography>
          ))}
        </Stack>
      </Stack>

      {loading ? (
        <Box height={size} display="flex" justifyContent="center" alignItems="center">
          <CircularProgress size={48} thickness={4} />
        </Box>
      ) : (
        <ResponsiveContainer width="100%" height={size}>
          <ComposedChart data={data} margin={{ left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis
              dataKey="date"
              ticks={xTicks}
              interval={0}
              minTickGap={0}
              tickFormatter={(v) => {
                const d = dayjs(v)
                return d.month() === 0 ? d.format("MM/YY") : d.format("MM")
              }}
              stroke={labelColor}
            />
            <YAxis
              orientation="right"
              domain={[min - padding, max + padding]}
              tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
              ticks={yTicks}
              stroke={labelColor}
            />
            <Tooltip
              formatter={(value, name) => [`${Number(value).toFixed(2)}%`, mapDisplayName(String(name))]}
            />
            <Legend />
            {allKeys.map((key) => {
              const display = mapDisplayName(key)
              const stroke = categoryColorMap[display] || COLORS[display] || theme.palette.primary.main
              return (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  strokeWidth={2}
                  dot={false}
                  stroke={stroke}
                  name={display}
                />
              )
            })}
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </Box>
  )
}
