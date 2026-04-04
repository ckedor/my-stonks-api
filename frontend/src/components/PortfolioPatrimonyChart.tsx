import { useCurrency } from '@/hooks/useCurrency'
import { PatrimonyEntry } from '@/types'
import { Box, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import { useMemo } from 'react'
import {
    CartesianGrid,
    Line,
    LineChart,
    ReferenceDot,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

interface Props {
  patrimonyEvolution: PatrimonyEntry[]
  selected: string
  size: number
  hideContributions?: boolean
  projection?: {
    rate: number
    years: number
    monthlyContribution?: number
  }
}

export default function PortfolioPatrimonyChart({
  patrimonyEvolution,
  selected,
  size,
  hideContributions = false,
  projection,
}: Props) {
  const key = selected === 'Carteira' ? 'portfolio' : selected

  const theme = useTheme()
  const { symbol } = useCurrency()
  const gridColor = theme.palette.chart.grid
  const labelColor = theme.palette.chart.label
  const lineColor = theme.palette.primary.main
  const aportedColor = theme.palette.secondary.main
  const growthColor = theme.palette.success.main

  const showAported = key === 'portfolio' && !hideContributions

  const filtered = patrimonyEvolution.filter((entry) =>
    Number.isFinite(entry[key] as number),
  )

  const baseData = filtered.map((entry) => {
    const raw = dayjs(entry.date)

    const aportedValue =
      showAported &&
      typeof (entry as any).acc_aported === 'number' &&
      Number.isFinite((entry as any).acc_aported)
        ? ((entry as any).acc_aported as number)
        : null

    const value = entry[key] as number

    const growth =
      showAported && aportedValue !== null
        ? Math.max(0, value - aportedValue)
        : null

    return {
      ts: raw.valueOf(), 
      rawDate: raw, 
      dateLabel: raw.format('MM/YY'),
      value,
      acc_aported: aportedValue,
      growth,
    }
  })

  const projectedData = useMemo(() => {
    if (!projection || baseData.length === 0) return []

    const { rate, years, monthlyContribution = 0 } = projection
    const last = baseData[baseData.length - 1]

    let principal = last.value
    let futureContrib = 0

    const days = 365 * years
    const dailyRate = Math.pow(1 + rate, 1 / 365)

    const lastAportedBase =
      showAported && typeof last.acc_aported === 'number' && Number.isFinite(last.acc_aported)
        ? (last.acc_aported as number)
        : 0

    const points: {
      ts: number
      rawDate: dayjs.Dayjs
      dateLabel: string
      projection: number
      aportedProjection: number
      growthProjection: number
    }[] = []

    for (let i = 1; i <= days; i++) {
      principal *= dailyRate

      if (monthlyContribution > 0 && i % 30 === 0) {
        futureContrib += monthlyContribution
      }

      const futureDate = last.rawDate.add(i, 'day')
      const aportedProjection = lastAportedBase + futureContrib
      const projectionValue = principal + futureContrib
      const growthProjection = Math.max(0, projectionValue - aportedProjection)

      points.push({
        ts: futureDate.valueOf(),
        rawDate: futureDate,
        dateLabel: futureDate.format('MM/YY'),
        projection: projectionValue,
        aportedProjection,
        growthProjection,
      })
    }

    return points
  }, [projection, baseData, showAported])

  const mergedData = useMemo(() => {
    const baseMapped = baseData.map(
      ({ ts, rawDate, dateLabel, value, acc_aported, growth }) => ({
        ts,
        rawDate,
        dateLabel,
        value,
        acc_aported,
        growth,
        projection: null as number | null,
        aportedProjection: null as number | null,
        growthProjection: null as number | null,
      }),
    )
    const projectionMapped = projectedData.map(
      ({ ts, rawDate, dateLabel, projection, aportedProjection, growthProjection }) => ({
        ts,
        rawDate,
        dateLabel,
        value: null as number | null,
        acc_aported: null as number | null,
        growth: null as number | null,
        projection,
        aportedProjection,
        growthProjection,
      }),
    )
    return [...baseMapped, ...projectionMapped]
  }, [baseData, projectedData])

  const dynamicYMax = useMemo(() => {
    if (mergedData.length === 0) return 0
    let maxVal = 0
    for (const d of mergedData) {
      if (typeof d.value === 'number' && Number.isFinite(d.value)) {
        if (d.value > maxVal) maxVal = d.value
      }
      if (showAported) {
        if (typeof d.acc_aported === 'number' && Number.isFinite(d.acc_aported)) {
          if (d.acc_aported > maxVal) maxVal = d.acc_aported
        }
        if (typeof d.growth === 'number' && Number.isFinite(d.growth)) {
          if (d.growth > maxVal) maxVal = d.growth
        }
      }
      if (projection) {
        if (typeof d.projection === 'number' && Number.isFinite(d.projection)) {
          if (d.projection > maxVal) maxVal = d.projection
        }
        if (showAported) {
          if (typeof d.aportedProjection === 'number' && Number.isFinite(d.aportedProjection)) {
            if (d.aportedProjection > maxVal) maxVal = d.aportedProjection
          }
          if (typeof d.growthProjection === 'number' && Number.isFinite(d.growthProjection)) {
            if (d.growthProjection > maxVal) maxVal = d.growthProjection
          }
        }
      }
    }
    return maxVal * 1.1
  }, [mergedData, showAported, projection])

  const yTicks = useMemo(() => {
    if (dynamicYMax <= 0) return [0]
    const niceSteps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
    const targetSteps = 6
    const rawStep = dynamicYMax / targetSteps
    const step = niceSteps.find((s) => s >= rawStep) ?? Math.ceil(rawStep / 100000) * 100000
    const max = Math.ceil(dynamicYMax / step) * step
    return Array.from({ length: Math.floor(max / step) + 1 }, (_, i) => i * step)
  }, [dynamicYMax])

  const yDomain: [number, number] = [0, yTicks[yTicks.length - 1] || dynamicYMax]

  const lastHistorical = useMemo(() => {
    const historical = mergedData.filter((d) => d.value !== null)
    if (historical.length === 0) return null
    return historical[historical.length - 1]
  }, [mergedData])

  const januaryTicks = useMemo(() => {
    if (mergedData.length === 0) return []

    const minTs = mergedData[0].ts
    const maxTs = mergedData[mergedData.length - 1].ts

    let cursor = dayjs(minTs).startOf('year').month(0).date(1)
    if (cursor.valueOf() < minTs) cursor = cursor.add(1, 'year')

    const ticks: number[] = []
    while (cursor.valueOf() <= maxTs) {
      ticks.push(cursor.valueOf())
      cursor = cursor.add(1, 'year')
    }
    return ticks
  }, [mergedData])

  return (
    <Box>
      <ResponsiveContainer width="100%" height={size}>
        <LineChart data={mergedData} margin={{ left: 48, top: 15, right: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />

          <XAxis
            dataKey="ts"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            ticks={januaryTicks}
            tickFormatter={(v) => dayjs(v).format('MM/YY')}
            stroke={labelColor}
            tick={{ fill: labelColor, fontSize: 13 }}
          />

          <YAxis
            orientation="right"
            stroke={labelColor}
            tick={{ fill: labelColor, fontSize: 12 }}
            tickFormatter={(v: number) =>
              v >= 1000000
                ? `${(v / 1000000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}M`
                : v >= 1000
                  ? `${(v / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 0 })}K`
                  : v.toLocaleString('pt-BR')
            }
            ticks={yTicks}
            domain={yDomain}
          />

          <Tooltip
            labelFormatter={(v) => dayjs(v as number).format('DD/MM/YY')}
            formatter={(value: number) =>
              `${symbol} ${value.toLocaleString('pt-BR', {
                maximumFractionDigits: 0,
              })}`
            }
          />

          <Line
            type="monotone"
            dataKey="value"
            strokeWidth={2}
            dot={false}
            stroke={lineColor}
            name="Histórico"
          />

          {showAported && (
            <Line
              type="monotone"
              dataKey="acc_aported"
              strokeWidth={2}
              dot={false}
              stroke={aportedColor}
              name="Aportes"
            />
          )}

          {showAported && (
            <Line
              type="monotone"
              dataKey="growth"
              strokeWidth={2}
              dot={false}
              stroke={growthColor}
              name="Crescimento"
            />
          )}

          {projection && (
            <Line
              type="monotone"
              dataKey="projection"
              stroke={lineColor}
              strokeDasharray="5 5"
              strokeWidth={2}
              dot={false}
              name={`Projeção ${Math.round(projection.rate * 100)}% a.a.`}
            />
          )}

          {projection && showAported && (
            <Line
              type="monotone"
              dataKey="aportedProjection"
              strokeWidth={2}
              dot={false}
              stroke={aportedColor}
              strokeDasharray="5 5"
              name="Aportes projetados"
            />
          )}

          {projection && showAported && (
            <Line
              type="monotone"
              dataKey="growthProjection"
              strokeWidth={2}
              dot={false}
              stroke={growthColor}
              strokeDasharray="5 5"
              name="Crescimento projetado"
            />
          )}

          {lastHistorical && lastHistorical.value !== null && (
            <ReferenceDot
              x={lastHistorical.ts}
              y={lastHistorical.value}
              r={0}
              label={{
                value: `${(lastHistorical.value / 1000).toFixed(0)}K`,
                position: 'right',
                fill: lineColor,
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          )}
          {lastHistorical && showAported && lastHistorical.acc_aported !== null && (
            <ReferenceDot
              x={lastHistorical.ts}
              y={lastHistorical.acc_aported}
              r={0}
              label={{
                value: `${(lastHistorical.acc_aported / 1000).toFixed(0)}K`,
                position: 'right',
                fill: aportedColor,
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          )}
          {lastHistorical && showAported && lastHistorical.growth !== null && (
            <ReferenceDot
              x={lastHistorical.ts}
              y={lastHistorical.growth}
              r={0}
              label={{
                value: `${(lastHistorical.growth / 1000).toFixed(0)}K`,
                position: 'right',
                fill: growthColor,
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  )
}
