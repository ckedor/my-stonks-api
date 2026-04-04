
import { Dividend } from '@/types'
import { Box, Typography, useTheme } from '@mui/material'
import dayjs from 'dayjs'
import { useMemo } from 'react'
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

type Props = {
  data: Dividend[]
}

export default function FixedIncomeDividendsChart({ data }: Props) {
  const theme = useTheme()
  const colors = theme.palette.chart?.colors ?? ['#8884d8', '#82ca9d']

  const mostRecent = useMemo(() => {
    return data.reduce((a, b) => (dayjs(a.date).isAfter(b.date) ? a : b))
  }, data)

  const currentYear = dayjs(mostRecent?.date).year()
  const previousYear = currentYear - 1

  const groupedData = useMemo(() => {
    const monthlyMap: Record<string, { month: string; [year: number]: number }> = {}

    for (let i = 0; i < 12; i++) {
      const month = dayjs().month(i).format('MMM')
      monthlyMap[month] = { month }
    }

    data.forEach((d) => {
      const date = dayjs(d.date)
      const year = date.year()
      if (year !== previousYear && year !== currentYear) return

      const month = date.format('MMM')
      const amount = d.amount

      monthlyMap[month][year] = (monthlyMap[month][year] || 0) + amount
    })

    return Object.values(monthlyMap)
  }, [data, currentYear, previousYear])

  return (
    <Box mt={4}>
      <Typography variant="body2" mb={2}>
        Rendimentos Mensais
      </Typography>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={groupedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip formatter={(value: number) => value.toFixed(2)} />
          <Legend />
          <Bar dataKey={previousYear} fill={colors[0]} name={`${previousYear}`} />
          <Bar dataKey={currentYear} fill={colors[1]} name={`${currentYear}`} />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  )
}
