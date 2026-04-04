
import { useCurrency } from '@/hooks/useCurrency'
import {
    Box,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TableSortLabel,
} from '@mui/material'
import { useTheme } from '@mui/material/styles'
import { useState } from 'react'

export type ColumnType = 'text' | 'number' | 'percentage' | 'currency'

export interface TableColumn {
  key: string
  label: string
  type: ColumnType
  gainLossColors?: boolean
  decimals?: boolean
}

export interface TableRowData {
  id: string | number
  [key: string]: any
}

export interface AppTableProps {
  columns: TableColumn[]
  rows: TableRowData[]
  totalRow?: TableRowData
  onRowClick?: (id: string | number) => void
  size?: 'small' | 'medium' | 'large'
}

export default function AppTable({
  columns,
  rows,
  totalRow,
  onRowClick,
  size = 'medium',
}: AppTableProps) {
  const theme = useTheme()
  const { symbol: currencySymbol, locale: currencyLocale } = useCurrency()
  const [orderBy, setOrderBy] = useState<string>('')
  const [orderDirection, setOrderDirection] = useState<'asc' | 'desc'>('asc')

  const getSizeStyle = () => {
    switch (size) {
      case 'small':
        return { py: 1, px: 1.5, fontSize: 13 }
      case 'large':
        return { py: 2, px: 2.5, fontSize: 17 }
      default:
        return { py: 1.3, px: 1.8, fontSize: 15 }
    }
  }

  const formatValue = (value: any, column: TableColumn): string => {
    if (value == null || value === '') return '—'

    const useDecimals = column.decimals ?? false
    const min = useDecimals ? 2 : 0
    const max = useDecimals ? 2 : 0

    if (column.type === 'currency') {
      return `${currencySymbol} ${value.toLocaleString(currencyLocale, {
        minimumFractionDigits: min,
        maximumFractionDigits: max,
      })}`
    }

    if (column.type === 'number') {
      return value.toLocaleString('pt-BR', {
        minimumFractionDigits: min,
        maximumFractionDigits: max,
      })
    }

    if (column.type === 'percentage') {
      return `${Number(value)
        .toFixed(useDecimals ? 2 : 0)
        .replace('.', ',')}%`
    }

    return String(value)
  }

  const getColor = (value: number): string | undefined => {
    if (value > 0) return theme.palette.success.main
    if (value < 0) return theme.palette.error.main
    return undefined
  }

  const cellSx = getSizeStyle()

  const handleSort = (key: string) => {
    if (orderBy === key) {
      setOrderDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setOrderBy(key)
      setOrderDirection('asc')
    }
  }

  const sortedRows = [...rows].sort((a, b) => {
    if (!orderBy) return 0
    const column = columns.find((col) => col.key === orderBy)
    if (!column) return 0

    const aVal = a[orderBy]
    const bVal = b[orderBy]

    if (column.type === 'text') {
      return orderDirection === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal))
    } else {
      return orderDirection === 'asc' ? aVal - bVal : bVal - aVal
    }
  })

  return (
    <Box>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell
                  key={col.key}
                  sx={cellSx}
                  align={col.type === 'text' ? 'left' : 'right'}
                  sortDirection={orderBy === col.key ? orderDirection : false}
                >
                  <TableSortLabel
                    active={orderBy === col.key}
                    direction={orderBy === col.key ? orderDirection : 'asc'}
                    onClick={() => handleSort(col.key)}
                  >
                    <strong>{col.label}</strong>
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRows.map((row) => (
              <TableRow
                key={row.id}
                hover
                onClick={() => onRowClick?.(row.id)}
                sx={{ cursor: 'pointer' }}
              >
                {columns.map((col) => (
                  <TableCell
                    key={col.key}
                    sx={{
                      ...cellSx,
                      color:
                        col.gainLossColors && typeof row[col.key] === 'number'
                          ? getColor(row[col.key])
                          : undefined,
                    }}
                    align={col.type === 'text' ? 'left' : 'right'}
                  >
                    {formatValue(row[col.key], col)}
                  </TableCell>
                ))}
              </TableRow>
            ))}

            {totalRow && (
              <TableRow
                selected
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => onRowClick?.(totalRow.id)}
              >
                {columns.map((col) => (
                  <TableCell
                    key={col.key}
                    sx={{
                      ...cellSx,
                      fontWeight: 'bold',
                      color:
                        col.gainLossColors && typeof totalRow[col.key] === 'number'
                          ? getColor(totalRow[col.key])
                          : undefined,
                    }}
                    align={col.type === 'text' ? 'left' : 'right'}
                  >
                    {formatValue(totalRow[col.key], col)}
                  </TableCell>
                ))}
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}
