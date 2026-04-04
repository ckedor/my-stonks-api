import AssetDetailPanel from '@/components/AssetDetailPanel'
import { usePortfolioStore } from '@/stores/portfolio'
import { Drawer } from '@mui/material'

interface AssetDrawerProps {
  assetId: number | null
  open: boolean
  onClose: () => void
}

export default function AssetDrawer({ assetId, open, onClose }: AssetDrawerProps) {
  const portfolioId = usePortfolioStore(s => s.selectedPortfolio?.id)

  return (
    <Drawer
      anchor="right"
      open={open && !!assetId}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100%', md: '100%', lg: '75vw' },
          overflow: 'hidden',
        },
      }}
    >
      {assetId && portfolioId && (
        <AssetDetailPanel assetId={assetId} portfolioId={portfolioId} />
      )}
    </Drawer>
  )
}
