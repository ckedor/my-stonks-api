import { DateRangeKey, getDateFromRange } from '@/lib/utils/date'
import { alpha, Box, MenuItem, Select, Stack, Switch, Typography, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
import {
    CandlestickData,
    CandlestickSeries,
    ColorType,
    createChart,
    HistogramSeries,
    IChartApi,
    ISeriesApi,
    Time,
} from 'lightweight-charts'
import { useEffect, useMemo, useRef, useState } from 'react'
import { defaultRangeOptionsFromOldest } from '../charts/app-bar-chart/helpers'
import DateRangeMenu, { RangeOption } from '../charts/shared/DateRangeMenu'

dayjs.extend(isSameOrAfter)

export type CandleTimeframe = 'day' | 'week' | 'month'

export interface CandleDataPoint {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

function aggregateCandles(data: CandleDataPoint[], timeframe: CandleTimeframe): CandleDataPoint[] {
  if (timeframe === 'day') return data
  if (!data.length) return []

  const buckets: Record<string, CandleDataPoint[]> = {}

  for (const d of data) {
    const dt = dayjs(d.time)
    const key = timeframe === 'week'
      ? dt.startOf('week').format('YYYY-MM-DD')
      : dt.format('YYYY-MM-01')

    if (!buckets[key]) buckets[key] = []
    buckets[key].push(d)
  }

  return Object.entries(buckets)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, candles]) => ({
      time: key,
      open: candles[0].open,
      high: Math.max(...candles.map((c) => c.high)),
      low: Math.min(...candles.map((c) => c.low)),
      close: candles[candles.length - 1].close,
      volume: candles.some((c) => c.volume != null)
        ? candles.reduce((sum, c) => sum + (c.volume ?? 0), 0)
        : undefined,
    }))
}

interface CandleChartProps {
  data: CandleDataPoint[]
  height?: number
  showVolume?: boolean
  showVolumeToggle?: boolean
  showRangePicker?: boolean
  defaultRange?: DateRangeKey
  rangeOptions?: RangeOption[]
  showTimeframeSelector?: boolean
  defaultTimeframe?: CandleTimeframe
}

export default function CandleChart({
  data,
  height = 400,
  showVolume = false,
  showVolumeToggle = false,
  showRangePicker = false,
  defaultRange = '1y',
  rangeOptions,
  showTimeframeSelector = false,
  defaultTimeframe = 'day',
}: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const theme = useTheme()
  const [range, setRange] = useState<DateRangeKey>(defaultRange)
  const [timeframe, setTimeframe] = useState<CandleTimeframe>(defaultTimeframe)
  const [volumeEnabled, setVolumeEnabled] = useState(showVolume)

  const oldestDateISO = useMemo(() => {
    if (!data.length) return null
    return data.reduce((oldest, d) =>
      d.time < oldest ? d.time : oldest, data[0].time)
  }, [data])

  const effectiveRangeOptions = useMemo(() => {
    if (rangeOptions?.length) return rangeOptions
    return defaultRangeOptionsFromOldest(oldestDateISO)
  }, [rangeOptions, oldestDateISO])

  const didInitRange = useRef(false)
  useEffect(() => {
    if (!showRangePicker) { setRange('max'); return }
    if (!effectiveRangeOptions.length || didInitRange.current) return
    const next = effectiveRangeOptions.some((o) => o.value === defaultRange)
      ? defaultRange
      : effectiveRangeOptions[0]?.value ?? 'max'
    setRange(next)
    didInitRange.current = true
  }, [showRangePicker, effectiveRangeOptions, defaultRange])

  const filtered = useMemo(() => {
    if (!data.length) return []
    let result = data
    if (showRangePicker && range !== 'max') {
      const from = getDateFromRange(range)
      result = result.filter((d) => dayjs(d.time).isSameOrAfter(from))
    }
    return aggregateCandles(result, timeframe)
  }, [data, showRangePicker, range, timeframe])

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      height,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: theme.palette.text.secondary,
        fontFamily: theme.typography.fontFamily as string,
      },
      grid: {
        vertLines: { color: theme.palette.chart.grid },
        horzLines: { color: theme.palette.chart.grid },
      },
      crosshair: {
        vertLine: { labelBackgroundColor: theme.palette.primary.main },
        horzLine: { labelBackgroundColor: theme.palette.primary.main },
      },
      rightPriceScale: {
        borderColor: theme.palette.divider,
      },
      timeScale: {
        borderColor: theme.palette.divider,
        timeVisible: false,
      },
    })

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: theme.palette.success.main,
      downColor: theme.palette.error.main,
      borderUpColor: theme.palette.success.main,
      borderDownColor: theme.palette.error.main,
      wickUpColor: theme.palette.success.main,
      wickDownColor: theme.palette.error.main,
    })

    candleSeries.setData(filtered as CandlestickData<Time>[])
    candleSeriesRef.current = candleSeries

    if (volumeEnabled && filtered.some((d) => d.volume != null)) {
      const volumeSeries = chart.addSeries(HistogramSeries, {
        priceFormat: { type: 'volume' },
        priceScaleId: 'volume',
      })

      chart.priceScale('volume').applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 },
      })

      volumeSeries.setData(
        filtered
          .filter((d) => d.volume != null)
          .map((d) => ({
            time: d.time as Time,
            value: d.volume!,
            color: d.close >= d.open
              ? alpha(theme.palette.success.main, 0.3)
              : alpha(theme.palette.error.main, 0.3),
          })),
      )

      volumeSeriesRef.current = volumeSeries
    }

    chart.timeScale().fitContent()
    chartRef.current = chart

    const resizeObserver = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    })
    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.remove()
      chartRef.current = null
      candleSeriesRef.current = null
      volumeSeriesRef.current = null
    }
  }, [filtered, height, volumeEnabled, theme])

  return (
    <Box>
      <Stack direction="row" justifyContent="flex-end" spacing={2} alignItems="center" sx={{ mb: 1 }}>
        {showVolumeToggle && (
          <Stack direction="row" spacing={0.5} alignItems="center">
            <Typography variant="body2" color="text.secondary">Vol</Typography>
            <Switch
              size="small"
              checked={volumeEnabled}
              onChange={(_, checked) => setVolumeEnabled(checked)}
            />
          </Stack>
        )}
        {showTimeframeSelector && (
          <Select
            size="small"
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as CandleTimeframe)}
            renderValue={(v) => (v === 'day' ? 'D' : v === 'week' ? 'S' : 'M')}
            sx={{ minWidth: 0, '.MuiSelect-select': { py: 0.5, px: 1, fontSize: 13 } }}
          >
            <MenuItem value="day">Diário</MenuItem>
            <MenuItem value="week">Semanal</MenuItem>
            <MenuItem value="month">Mensal</MenuItem>
          </Select>
        )}
        <DateRangeMenu
          show={showRangePicker}
          range={range}
          options={effectiveRangeOptions}
          onChange={setRange}
        />
      </Stack>
      <div ref={containerRef} style={{ width: '100%' }} />
    </Box>
  )
}
