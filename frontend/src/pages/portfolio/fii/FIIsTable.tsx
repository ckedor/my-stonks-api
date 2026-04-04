
import AppTable, { TableColumn, TableRowData } from '@/components/ui/app-table'
import { FIIPortfolioPositionEntry } from '@/types'
import { useMemo } from 'react'

type Props = {
  data: FIIPortfolioPositionEntry[]
}

export default function FIIsTable({ data }: Props) {
  const columns: TableColumn[] = [
    { key: 'ativo', label: 'Ativo', type: 'text' },
    { key: 'tipo', label: 'Tipo', type: 'text' },
    { key: 'segmento', label: 'Segmento', type: 'text' },
    { key: 'quantidade', label: 'Qtd.', type: 'number' },
    { key: 'preco', label: 'Preço', type: 'currency', decimals: true },
    { key: 'posicao', label: 'Posição', type: 'currency' },
    { key: 'percentual', label: '% Total', type: 'percentage', decimals: true },
    { key: 'rent12m', label: 'Rent. 12m (Preço)', type: 'percentage', gainLossColors: true },
    { key: 'rent12mTotal', label: 'Rent. 12m (Total)', type: 'percentage', gainLossColors: true },
  ]

  const rows: TableRowData[] = useMemo(() => {
    const total = data.reduce((acc, fii) => acc + fii.value, 0)

    return data.map((fii) => ({
      id: fii.ticker,
      ativo: fii.ticker,
      tipo: fii.fii_type,
      segmento: fii.fii_segment,
      quantidade: fii.quantity,
      preco: fii.price,
      posicao: fii.value,
      percentual: total > 0 ? (fii.value / total) * 100 : 0,
      rent12m: fii.twelve_months_return * 100,
      rent12mTotal: fii.profit_pct,
    }))
  }, [data])

  const totalRow: TableRowData = useMemo(() => {
    const posicao = rows.reduce((sum, r) => sum + (r.posicao || 0), 0)
    const rent12m = rows.reduce((sum, r) => sum + (r.rent12m || 0), 0) / rows.length
    const rent12mTotal = rows.reduce((sum, r) => sum + (r.rent12mTotal || 0), 0) / rows.length

    return {
      id: 'total',
      ativo: 'Total',
      tipo: '',
      segmento: '',
      quantidade: '',
      preco: '',
      posicao,
      percentual: 100,
      rent12m,
      rent12mTotal,
    }
  }, [rows])

  return <AppTable columns={columns} rows={rows} totalRow={totalRow} size="small" />
}
