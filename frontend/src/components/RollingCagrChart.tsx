import { RollingCagrEntry } from '@/types'
import { Box, Typography, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import { useMemo } from 'react'
import {
    Area,
    CartesianGrid,
    ComposedChart,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

interface Props {
  data: RollingCagrEntry[]
  size?: number
}

export default function RollingCagrChart({ data, size = 300 }: Props) {
  const theme = useTheme()
  const gridColor = theme.palette.chart.grid
  const labelColor = theme.palette.chart.label

  const chartData = useMemo(() => {
    if (!data.length) return []
    const cutoff = dayjs(data[0].date).add(12, 'month')
    return data.map((d) => ({
      date: d.date,
      cagr: dayjs(d.date).isBefore(cutoff) ? null : d.value,
    }))
  }, [data])

  const xTicks = useMemo(() => {
    const ticks: string[] = []
    chartData.forEach((d) => {
      const day = dayjs(d.date)
      if (day.date() === 1) ticks.push(d.date)
    })
    return ticks.length ? ticks : chartData.map((d) => d.date)
  }, [chartData])

  if (!chartData.length) return null

  const values = chartData.filter((d) => d.cagr != null).map((d) => d.cagr as number)
  if (!values.length) return null
  const min = Math.min(...values)
  const max = Math.max(...values)
  const pad = (max - min) * 0.1

  return (
    <Box>
      <Typography variant="subtitle2" fontWeight={600} mb={1} ml={1}>
        Retorno Anualizado Móvel (12 meses)
      </Typography>
      <ResponsiveContainer width="100%" height={size}>
        <ComposedChart data={chartData} margin={{ left: 10 }}>
          <defs>
            <linearGradient id="cagrGradientPos" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
              <stop offset="100%" stopColor={theme.palette.success.main} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="date"
            ticks={xTicks}
            interval={0}
            minTickGap={0}
            tickFormatter={(v) => {
              const d = dayjs(v)
              return d.month() === 0 ? d.format('MM/YY') : d.format('MM')
            }}
            stroke={labelColor}
          />
          <YAxis
            orientation="right"
            domain={[Math.min(0, min - pad), max + pad]}
            tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
            stroke={labelColor}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'CAGR 12m']}
            labelFormatter={(label) => dayjs(label).format('DD/MM/YYYY')}
          />
          <ReferenceLine y={0} stroke={labelColor} strokeDasharray="3 3" />
          <Area
            type="monotone"
            dataKey="cagr"
            stroke={theme.palette.primary.main}
            strokeWidth={2}
            fill="url(#cagrGradientPos)"
            dot={false}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  )
}
