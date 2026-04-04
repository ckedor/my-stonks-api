// src/pages/PortfolioReturnsPage.tsx
import PortfolioReturnsChart from '@/components/PortfolioReturnsChart'
import AppCard from '@/components/ui/AppCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useAnalysisStore } from '@/stores/portfolio/analysis'
import { useReturnsStore } from '@/stores/portfolio/returns'
import { Box, Chip, Grid, Typography } from '@mui/material'
import { useEffect, useMemo, useState } from 'react'
import PortfolioMonthlyHeatmap from './PortfolioMonthlyHeatmap'
import PortfolioMonthlyReturnsChart from './PortfolioMonthlyReturnsChart'
import PortfolioRolling12mChart from './PortfolioRolling12mChart'

interface SeriesPoint {
  date: string
  value: number
}

export default function PortfolioReturnsPage() {
  const { categoryReturns, loading: returnsLoading } = useReturnsStore()
  const { analysis } = useAnalysisStore()

  const loading = returnsLoading && Object.keys(categoryReturns).length === 0

  const [range, setRange] = useState<string>('max')

  useEffect(() => {
    if (!useReturnsStore.persist.hasHydrated()) {
      const id = setTimeout(() => useReturnsStore.persist.rehydrate(), 0)
      return () => clearTimeout(id)
    }
  }, [])

  // Busca os dados do portfolio
  const portfolioData: SeriesPoint[] = useMemo(() => {
    return (categoryReturns['portfolio'] || []).slice()
  }, [categoryReturns])

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <Box sx={{ p: 1, pt: 2 }}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>Rentabilidade Carteira</Typography>
      <Grid container spacing={2}>
        {/* Performance metrics row */}
        {analysis && (
          <Grid size={12}>
            <AppCard>
              <Box
                display="flex"
                flexWrap="wrap"
                gap={1}
                alignItems="center"
              >
              <Chip
                label={`CAGR ${analysis.performance_metrics.cagr.toFixed(2)}%`}
                size="small"
                sx={{
                  fontWeight: 700,
                  color: analysis.performance_metrics.cagr >= 0 ? 'success.main' : 'error.main',
                  bgcolor: 'transparent',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              />
              {Object.entries(analysis.performance_metrics.benchmarks_metrics).map(([name, bm]) => (
                <Box key={name} display="flex" alignItems="center" gap={0.5}>
                  <Chip
                    label={`α ${name} ${bm.alpha >= 0 ? '+' : ''}${bm.alpha.toFixed(2)}%`}
                    size="small"
                    sx={{
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      color: bm.alpha >= 0 ? 'success.main' : 'error.main',
                      bgcolor: 'transparent',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    β {bm.beta.toFixed(2)} · ρ {bm.correlation.toFixed(2)}
                  </Typography>
                </Box>
              ))}
            </Box>
            </AppCard>
          </Grid>
        )}

        {/* Linha 1 - Gráfico principal full width */}
        <Grid size={12}>
          <AppCard>
            <PortfolioReturnsChart
              size={520}
              selectedCategory="portfolio"
              selectedBenchmark="CDI"
              defaultRange={range}
              onRangeChange={setRange}
            />
          </AppCard>
        </Grid>

        {/* Linha 2 - Heatmap full width */}
        <Grid size={12}>
          <AppCard>
            <PortfolioMonthlyHeatmap 
              data={portfolioData} 
            />
          </AppCard>
        </Grid>

        {/* Linha 3 - 2 gráficos lado a lado */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AppCard>
            <PortfolioMonthlyReturnsChart
              height={300}
              defaultRange={range}
              data={portfolioData}
            />
          </AppCard>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <AppCard>
            <PortfolioRolling12mChart
              height={300}
              data={portfolioData}
            />
          </AppCard>
        </Grid>
      </Grid>
    </Box>
  )
}
