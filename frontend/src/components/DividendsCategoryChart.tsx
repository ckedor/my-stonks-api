import { useCurrency } from '@/hooks/useCurrency'
import { Dividend } from '@/types'
import { Box, Divider, Paper, Typography, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

interface Props {
  dividends: Dividend[]
  categoryColors: Record<string, string>
  year: number
  size?: number
}

export default function DividendsCategoryChart({ dividends, categoryColors, year, size = 370 }: Props) {
  const theme = useTheme()
  const { symbol, locale } = useCurrency()

  const currentYear = year

  const categories = Array.from(new Set(dividends.map((d) => d.category))).sort()

  const data = Array.from({ length: 12 }, (_, i) => {
    const entry: Record<string, any> = { month: dayjs().month(i).format('MMM') }
    categories.forEach((cat) => {
      entry[cat] = dividends
        .filter((d) => {
          const dt = dayjs(d.date)
          return dt.year() === currentYear && dt.month() === i && d.category === cat
        })
        .reduce((sum, d) => sum + d.amount, 0)
    })
    return entry
  })

  if (!dividends.length) {
    return (
      <Box
        position="relative"
        height={size}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Typography variant="subtitle1" color="text.secondary">
          Nenhum provento encontrado
        </Typography>
      </Box>
    )
  }

  const monthTotals = data.map((r) =>
    categories.reduce((sum, c) => sum + ((r[c] as number) || 0), 0)
  )
  const max = Math.max(...monthTotals)
  const upper = Math.ceil((max || 1) * 1.3)

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null
    const total = payload.reduce((sum: number, p: any) => sum + (p.value || 0), 0)
    return (
      <Paper sx={{ p: 1.5, boxShadow: 3 }}>
        <Typography variant="body2" fontWeight="bold" mb={0.5}>
          {label} / {currentYear}
        </Typography>
        {payload.map((p: any, i: number) => (
          <Typography key={i} variant="body2" sx={{ color: p.fill }}>
            {p.name}: {symbol} {p.value.toLocaleString(locale, { maximumFractionDigits: 2 })}
          </Typography>
        ))}
        {payload.length > 1 && (
          <>
            <Divider sx={{ my: 0.5 }} />
            <Typography variant="body2" fontWeight="bold">
              Total: {symbol} {total.toLocaleString(locale, { maximumFractionDigits: 2 })}
            </Typography>
          </>
        )}
      </Paper>
    )
  }

  return (
    <Box position="relative" height={size}>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ position: 'absolute', top: -2, left: 56 }}
      >
        {currentYear}
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: 48 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.chart.grid} />
          <XAxis dataKey="month" stroke={theme.palette.text.primary} />
          <YAxis
            orientation="right"
            domain={[0, upper]}
            tickFormatter={(v: number) => `${symbol} ${v.toLocaleString(locale)}`}
            tick={{ fontSize: 13 }}
            stroke={theme.palette.text.primary}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {categories.map((cat) => (
            <Bar
              key={cat}
              dataKey={cat}
              stackId="dividends"
              fill={categoryColors[cat] || theme.palette.primary.main}
              name={cat}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Box>
  )
}
