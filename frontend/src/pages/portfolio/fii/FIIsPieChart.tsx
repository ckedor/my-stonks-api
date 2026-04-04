
import AppPieChart from '@/components/ui/app-pie-chart'
import { FIIPortfolioPositionEntry } from '@/types'
import { Box } from '@mui/material'
import { useMemo } from 'react'

type Props = {
  data: FIIPortfolioPositionEntry[]
  groupBy: 'ticker' | 'fii_type' | 'fii_segment'
}

export default function FIIsPieChart({ data, groupBy }: Props) {
  const chartData = useMemo(() => {
    const grouped: Record<string, number> = {}

    for (const item of data) {
      const key = groupBy === 'ticker' ? item.ticker : item[groupBy]
      grouped[key] = (grouped[key] || 0) + item.value
    }

    return Object.entries(grouped).map(([label, value]) => ({ label, value }))
  }, [data, groupBy])

  return (
    <Box>
      <AppPieChart data={chartData} isCurrency height={300} />
    </Box>
  )
}
