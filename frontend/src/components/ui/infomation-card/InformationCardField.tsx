
import { useCurrency } from '@/hooks/useCurrency'
import { Grid, Typography } from '@mui/material'

export type InformationCardFieldProps = {
  label: string
  value: string | number | null | undefined
  isPercentage?: boolean
  isCurrency?: boolean
  gainLossColors?: boolean
}

export default function InformationCardField({
  label,
  value,
  isPercentage = false,
  isCurrency = false,
  gainLossColors = false,
}: InformationCardFieldProps) {
  const isNullish = value === null || value === undefined
  const isNumeric =
    typeof value === 'number' || (typeof value === 'string' && !isNaN(Number(value)))
  const num = isNumeric ? Number(value) : null

  const { format: formatCurrency } = useCurrency()

  let displayValue: string | number = '—'

  if (isNullish) {
    displayValue = '—'
  } else if (!isNumeric) {
    displayValue = value as string
  } else if (isPercentage) {
    displayValue = `${(num! * 100).toFixed(2)}%`
  } else if (isCurrency) {
    displayValue = formatCurrency(num!)
  } else {
    displayValue = num!
  }

  let color: string = 'text.primary'
  if (gainLossColors && isNumeric) {
    if (num! > 0) color = 'success.main'
    else if (num! < 0) color = 'error.main'
  }

  return (
    <Grid size={{ xs: 4, md: 2 }}>
      <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
        {label}
      </Typography>
      <Typography fontWeight="bold" sx={{ color }}>
        {displayValue}
      </Typography>
    </Grid>
  )
}
