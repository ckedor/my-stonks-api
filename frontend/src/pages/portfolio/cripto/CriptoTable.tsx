
import AppTable, { TableColumn, TableRowData } from '@/components/ui/app-table'
import { PortfolioPositionEntry } from '@/types'
import { useMemo } from 'react'

type Props = {
  data: PortfolioPositionEntry[]
}

export default function CriptoTable({ data }: Props) {
  const columns: TableColumn[] = [
    { key: 'ativo', label: 'Ativo', type: 'text' },
    { key: 'nome', label: 'Nome', type: 'text' },
    { key: 'quantidade', label: 'Qtd.', type: 'number' },
    { key: 'preco', label: 'Preço', type: 'currency', decimals: true },
    { key: 'posicao', label: 'Posição', type: 'currency' },
    { key: 'percentual', label: '% Total', type: 'percentage', decimals: true },
    { key: 'rent12m', label: 'Rent. 12m (Preço)', type: 'percentage', gainLossColors: true },
    { key: 'rent12mTotal', label: 'Rent. 12m (Total)', type: 'percentage', gainLossColors: true },
  ]

  const rows: TableRowData[] = useMemo(() => {
    const total = data.reduce((acc, item) => acc + item.value, 0)

    return data.map((obj) => ({
      id: obj.ticker,
      ativo: obj.ticker,
      nome: obj.name,
      quantidade: obj.quantity,
      preco: obj.price,
      posicao: obj.value,
      percentual: total > 0 ? (obj.value / total) * 100 : 0,
      rent12m: obj.twelve_months_return * 100,
      rent12mTotal: obj.profit_pct,
    }))
  }, [data])

  const totalRow: TableRowData = useMemo(() => {
    const posicao = rows.reduce((sum, r) => sum + (r.posicao || 0), 0)
    const rent12m = rows.reduce((sum, r) => sum + (r.rent12m || 0), 0) / rows.length
    const rent12mTotal = rows.reduce((sum, r) => sum + (r.rent12mTotal || 0), 0) / rows.length

    return {
      id: 'total',
      ativo: 'Total',
      nome: '',
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
