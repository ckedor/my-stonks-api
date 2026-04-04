
import AppPieChart from '@/components/ui/app-pie-chart'
import { PortfolioPositionEntry } from '@/types'
import { Box } from '@mui/material'
import { useMemo } from 'react'

type Props = {
  data: PortfolioPositionEntry[]
}

export default function PensionPieChart({ data }: Props) {
  const chartData = useMemo(() => {
    return data.map((item) => ({
      label: item.ticker,
      value: item.value,
    }))
  }, [data])

  return (
    <Box>
      <AppPieChart data={chartData} isCurrency height={300} />
    </Box>
  )
}
