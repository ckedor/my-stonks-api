export type NumberFormatKind = 'number' | 'currency' | 'percent'

export interface NumberFormatOptions {
  kind?: NumberFormatKind
  locale?: string
  currency?: string
  maximumFractionDigits?: number
  compact?: boolean
}

export function createNumberFormatter({
  kind = 'number',
  locale = 'pt-BR',
  currency = 'BRL',
  compact = false,
}: NumberFormatOptions = {}) {
  if (kind === 'currency' && compact) {
    return (value: number) => `${Math.round(value / 1000)}K`
  }

  if (kind === 'currency') {
    return (value: number) =>
      value.toLocaleString(locale, {
        style: 'currency',
        currency,
        maximumFractionDigits: 0,
      })
  }

  if (kind === 'percent') {
    return (value: number) => `${value.toFixed(2)}%`
  }

  const nf = new Intl.NumberFormat(locale, { maximumFractionDigits: 2 })
  return (value: number) => nf.format(value)
}