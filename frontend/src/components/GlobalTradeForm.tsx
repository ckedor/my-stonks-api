import { forceRefreshAll } from '@/actions/portfolio'
import { usePortfolioStore } from '@/stores/portfolio'
import { useTradeFormStore } from '@/stores/trade-form'
import TradeForm from './TradeForm'

export default function GlobalTradeForm() {
  const { isOpen, preSelectedAsset, closeTradeForm } = useTradeFormStore()
  const selectedPortfolio = usePortfolioStore((s) => s.selectedPortfolio)

  const handleSave = () => {
    if (selectedPortfolio) forceRefreshAll(selectedPortfolio.id)
  }

  return (
    <TradeForm
      open={isOpen}
      onClose={closeTradeForm}
      onSave={handleSave}
      initialAsset={preSelectedAsset}
    />
  )
}
