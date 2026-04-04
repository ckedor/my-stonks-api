import AssetDetailPanel from '@/components/AssetDetailPanel'
import AssetSidebar from '@/components/AssetSidebar'
import AppBreadcrumbs from '@/components/ui/AppBreadcrumbs'
import { usePortfolioStore } from '@/stores/portfolio'
import { usePositionsStore } from '@/stores/portfolio/positions'
import { Box, Paper } from '@mui/material'
import { useParams } from "react-router-dom"

export default function PortfolioAssetPage() {
  const { id } = useParams<{ id: string }>()
  const selectedPortfolio = usePortfolioStore(s => s.selectedPortfolio)
  const portfolioId = selectedPortfolio?.id
  const positions = usePositionsStore(s => s.positions)
  const assetId = id ? parseInt(id, 10) : null
  const asset = positions.find(p => p.asset_id === assetId)

  if (!portfolioId || !assetId) return null

  return (
    <Box display="flex" sx={{ ml: -4, mr: -4, mb: -1 }}>
      {/* Sidebar de ativos */}
      <Box
        sx={{
          width: 180,
          minWidth: 180,
          flexShrink: 0,
          display: { xs: 'none', md: 'block' },
          borderRight: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Box
          sx={{
            position: 'sticky',
            top: 0,
            maxHeight: 'calc(100vh - 112px)',
            overflowY: 'auto',
            pt: 1.5,
            pl: 2,
            pr: 0.5,
            '&::-webkit-scrollbar': { width: 4 },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'divider',
              borderRadius: 2,
            },
          }}
        >
          <AssetSidebar selectedAssetId={assetId} />
        </Box>
      </Box>

      {/* Conteúdo principal */}
      <Box flex={1} minWidth={0} sx={{ pt: 2, px: 3 }}>
        <AppBreadcrumbs items={[
          { label: 'Ativos', href: '/portfolio/asset' },
          { label: asset?.ticker ?? '...' },
        ]} />

        <Box sx={{ mt: 1 }}>
          <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <AssetDetailPanel assetId={assetId} portfolioId={portfolioId} />
          </Paper>
        </Box>
      </Box>
    </Box>
  )
}
