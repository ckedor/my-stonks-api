import DrawdownChart from '@/components/DrawdownChart'
import RiskMetricsPanel from '@/components/RiskMetricsPanel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAnalysisStore } from '@/stores/portfolio/analysis'
import { Box, Typography } from '@mui/material'

export default function PortfolioRiskPage() {
  const { analysis, loading: analysisLoading } = useAnalysisStore()

  const loading = analysisLoading && !analysis

  if (loading) {
    return <LoadingSpinner />
  }

  if (!analysis) {
    return (
      <Box p={4}>
        <Typography color="text.secondary">
          Dados de análise não disponíveis para esta carteira.
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 1, pt: 2 }}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>Risco</Typography>
      <Box display="flex" flexDirection="column" gap={3}>
        <RiskMetricsPanel analysis={analysis} />
        <DrawdownChart
          series={analysis.risk_metrics.drawdown.series}
          stats={analysis.risk_metrics.drawdown.stats}
          size={350}
        />
      </Box>
    </Box>
  )
}
