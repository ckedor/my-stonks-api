
import AppPieChart from '@/components/ui/app-pie-chart'
import { FixedIncomePositionEntry } from '@/types'
import { Box } from '@mui/material'
import { useMemo } from 'react'

type Props = {
  data: FixedIncomePositionEntry[]
}

export default function FixedIncomePieChart({ data }: Props) {
  const chartData = useMemo(() => {
    const grouped: Record<string, number> = {}

    for (const item of data) {
      const label = item.ticker
      grouped[label] = (grouped[label] || 0) + item.value
    }

    return Object.entries(grouped)
      .sort((a, b) => b[1] - a[1]) // Ordena do maior para o menor valor
      .map(([label, value]) => ({ label, value }))
  }, [data])

  return (
    <Box>
      <AppPieChart data={chartData} isCurrency height={300} />
    </Box>
  )
}
