
import AppTable, { TableColumn, TableRowData } from '@/components/ui/app-table'
import { FixedIncomePositionEntry } from '@/types'
import { useMemo } from 'react'

type Props = {
  data: FixedIncomePositionEntry[]
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('pt-BR').format(date)
}

function getTipo(bond: FixedIncomePositionEntry): string {
  if (bond.treasury_bond_type) {
    return String(bond.treasury_bond_type)
  }

  const indexador = bond.fixed_income_index_name || ''
  const fee = bond.fixed_income_fee

  if (!indexador || fee === null || fee === undefined) return bond.fixed_income_type

  if (bond.fixed_income_type === 'Index+') {
    return `${indexador} + ${(fee * 100).toFixed(2).replace('.', ',')}%`
  }

  if (bond.fixed_income_type === '%Index') {
    return `${(fee * 100).toFixed(2).replace('.', ',')}% do ${indexador}`
  }

  return bond.fixed_income_type
}

export default function FixedIncomeTable({ data }: Props) {
  const columns: TableColumn[] = [
    { key: 'ativo', label: 'Ativo', type: 'text' },
    { key: 'tipo', label: 'Tipo', type: 'text' },
    { key: 'vencimento', label: 'Vencimento', type: 'text' },
    { key: 'quantidade', label: 'Qtd.', type: 'number' },
    { key: 'preco', label: 'Preço', type: 'currency', decimals: true },
    { key: 'posicao', label: 'Posição', type: 'currency' },
    { key: 'percentual', label: '% Total', type: 'percentage', decimals: true },
    { key: 'rent12m', label: 'Rent. 12m (Preço)', type: 'percentage', gainLossColors: true },
    { key: 'rent12mTotal', label: 'Rent. 12m (Total)', type: 'percentage', gainLossColors: true },
  ]

  const rows: TableRowData[] = useMemo(() => {
    const total = data.reduce((acc, bond) => acc + bond.value, 0)

    return data.map((bond) => ({
      id: bond.ticker,
      ativo: bond.ticker,
      tipo: getTipo(bond),
      vencimento: formatDate(bond.fixed_income_maturity_date || bond.treasury_bond_maturity_date),
      quantidade: bond.quantity,
      preco: bond.price,
      posicao: bond.value,
      percentual: total > 0 ? (bond.value / total) * 100 : 0,
      rent12m: (bond.twelve_months_return ?? 0) * 100,
      rent12mTotal: bond.profit_pct ?? 0,
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
      vencimento: '',
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
