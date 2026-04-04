import { DrawdownEntry, DrawdownStats } from '@/types'
import { Box, Stack, Typography, useTheme } from '@mui/material'
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
  series: DrawdownEntry[]
  stats: DrawdownStats
  size?: number
}

function StatItem({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <Box sx={{ textAlign: 'center', px: 2 }}>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={700} color={color ?? 'text.primary'}>
        {value}
      </Typography>
    </Box>
  )
}

export default function DrawdownChart({ series, stats, size = 300 }: Props) {
  const theme = useTheme()
  const gridColor = theme.palette.chart.grid
  const labelColor = theme.palette.chart.label

  const chartData = useMemo(
    () => series.map((d) => ({ date: d.date, drawdown: d.drawdown * 100 })),
    [series],
  )

  const xTicks = useMemo(() => {
    const ticks: string[] = []
    chartData.forEach((d) => {
      const day = dayjs(d.date)
      if (day.date() === 1) ticks.push(d.date)
    })
    return ticks.length ? ticks : chartData.map((d) => d.date)
  }, [chartData])

  if (!chartData.length) return null

  const minVal = Math.min(...chartData.map((d) => d.drawdown))
  const pad = Math.abs(minVal) * 0.1

  return (
    <Box>
      <Typography variant="subtitle2" fontWeight={600} mb={1}>
        Drawdown
      </Typography>

      {/* Stats row */}
      <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" justifyContent="center">
        <StatItem
          label="Max Drawdown"
          value={`${(stats.max_drawdown * 100).toFixed(2)}%`}
          color="error.main"
        />
        <StatItem
          label="Data do Pico"
          value={dayjs(stats.peak_date_before_max_dd).format('DD/MM/YY')}
        />
        <StatItem
          label="Data do Max DD"
          value={dayjs(stats.max_drawdown_date).format('DD/MM/YY')}
        />
        {stats.recovery_date && (
          <StatItem
            label="Recuperação"
            value={dayjs(stats.recovery_date).format('DD/MM/YY')}
          />
        )}
        {stats.recovery_days != null && (
          <StatItem label="Dias p/ Recuperar" value={`${stats.recovery_days}d`} />
        )}
        {stats.max_drawdown_duration_days != null && (
          <StatItem label="Duração Max DD" value={`${stats.max_drawdown_duration_days}d`} />
        )}
      </Stack>

      <ResponsiveContainer width="100%" height={size}>
        <ComposedChart data={chartData} margin={{ left: 10 }}>
          <defs>
            <linearGradient id="ddGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={theme.palette.error.main} stopOpacity={0.05} />
              <stop offset="100%" stopColor={theme.palette.error.main} stopOpacity={0.35} />
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
            domain={[minVal - pad, 0]}
            tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
            stroke={labelColor}
          />
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Drawdown']}
            labelFormatter={(label) => dayjs(label).format('DD/MM/YYYY')}
          />
          <ReferenceLine y={0} stroke={labelColor} strokeWidth={1.5} />
          <Area
            type="monotone"
            dataKey="drawdown"
            stroke={theme.palette.error.main}
            strokeWidth={1.5}
            fill="url(#ddGradient)"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  )
}
