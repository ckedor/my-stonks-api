import { useCurrency } from '@/hooks/useCurrency'
import { PortfolioPositionEntry } from '@/types'
import { Box, Typography, useTheme } from '@mui/material'
import { Portal } from '@visx/tooltip'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

export type DistributionMetric = 'twelve_months_return' | 'acc_return' | 'cagr' | 'profit'

interface PerformanceBarChartProps {
  positions: PortfolioPositionEntry[]
  metric: DistributionMetric
  onAssetSelect?: (assetId: number) => void
}

const METRIC_LABELS: Record<DistributionMetric, string> = {
  twelve_months_return: 'Rent. 12M',
  acc_return: 'Rent. Acumulada',
  cagr: 'CAGR',
  profit: 'Lucro Absoluto',
}

function getMetricValue(pos: PortfolioPositionEntry, metric: DistributionMetric): number {
  switch (metric) {
    case 'profit':
      return (pos.value ?? 0) - (pos.total_invested ?? 0)
    case 'cagr':
      return (pos.cagr ?? 0) * 100
    case 'twelve_months_return':
      return (pos.twelve_months_return ?? 0) * 100
    case 'acc_return':
      return (pos.acc_return ?? 0) * 100
  }
}

function formatMetricValue(value: number, metric: DistributionMetric, fmtCurrency?: (v: number) => string): string {
  if (metric === 'profit') {
    return fmtCurrency ? fmtCurrency(value) : `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
  }
  return `${value >= 0 ? '+' : ''}${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`
}

const BAR_HEIGHT = 28
const BAR_GAP = 4
const LABEL_WIDTH = 140
const PADDING_RIGHT = 12

export default function PerformanceBarChart({ positions, metric, onAssetSelect }: PerformanceBarChartProps) {
  const theme = useTheme()
  const { format: formatCurrency } = useCurrency()
  const containerRef = useRef<HTMLDivElement>(null)
  const [chartWidth, setChartWidth] = useState(0)

  type TooltipData = { ticker: string; name: string; value: number; currentValue: number; invested: number }
  const [tooltip, setTooltip] = useState<{ data: TooltipData; x: number; y: number } | null>(null)
  const hideTooltip = useCallback(() => setTooltip(null), [])

  useEffect(() => {
    if (!containerRef.current) return
    const observer = new ResizeObserver(([entry]) => setChartWidth(entry.contentRect.width))
    observer.observe(containerRef.current)
    return () => observer.disconnect()
  }, [])

  const sorted = useMemo(() => {
    return [...positions]
      .map((pos) => ({
        ...pos,
        metricValue: getMetricValue(pos, metric),
      }))
      .sort((a, b) => b.metricValue - a.metricValue)
  }, [positions, metric])

  const { minVal, maxVal } = useMemo(() => {
    if (sorted.length === 0) return { minVal: 0, maxVal: 1 }
    const vals = sorted.map((d) => d.metricValue)
    return {
      minVal: Math.min(...vals, 0),
      maxVal: Math.max(...vals, 0),
    }
  }, [sorted])

  const barAreaWidth = Math.max(chartWidth - LABEL_WIDTH - PADDING_RIGHT, 0)
  const range = maxVal - minVal || 1
  // Position of 0 within the bar area, proportional to data range
  const zeroX = LABEL_WIDTH + (barAreaWidth * (-minVal)) / range
  const pxPerUnit = barAreaWidth / range

  const totalHeight = sorted.length * (BAR_HEIGHT + BAR_GAP)

  // Clamp a bar so it never extends into the label area
  const clampBar = (x: number, w: number) => {
    const clampedX = Math.max(x, LABEL_WIDTH)
    const clampedW = Math.max(w - (clampedX - x), 0)
    return { x: clampedX, w: clampedW }
  }

  return (
    <Box ref={containerRef} sx={{ position: 'relative', width: '100%', height: '100%', overflow: 'auto' }}>
      {chartWidth > 0 && (
        <svg width={chartWidth} height={Math.max(totalHeight, 100)}>
          {/* Zero line */}
          <line
            x1={zeroX}
            y1={0}
            x2={zeroX}
            y2={totalHeight}
            stroke={theme.palette.divider}
            strokeWidth={1}
          />

          {sorted.map((item, i) => {
            const y = i * (BAR_HEIGHT + BAR_GAP)
            const barWidth = Math.abs(item.metricValue * pxPerUnit)
            const isPositive = item.metricValue >= 0
            const rawBarX = isPositive ? zeroX : zeroX - barWidth
            const { x: barX, w: clampedBarWidth } = clampBar(rawBarX, barWidth)
            const barColor = isPositive ? theme.palette.success.main : theme.palette.error.main

            return (
              <g
                key={item.asset_id}
                style={{ cursor: 'pointer' }}
                onClick={() => onAssetSelect?.(item.asset_id)}
                onMouseMove={(e) => {
                  setTooltip({
                    x: e.clientX + 12,
                    y: e.clientY - 40,
                    data: {
                      ticker: item.ticker,
                      name: item.name,
                      value: item.metricValue,
                      currentValue: item.value,
                      invested: item.total_invested ?? 0,
                    },
                  })
                }}
                onMouseLeave={hideTooltip}
              >
                {/* Ticker label */}
                <foreignObject x={0} y={y} width={LABEL_WIDTH - 4} height={BAR_HEIGHT}>
                  <div
                    title={item.ticker}
                    style={{
                      width: '100%',
                      height: BAR_HEIGHT,
                      lineHeight: `${BAR_HEIGHT}px`,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      textAlign: 'right',
                      fontSize: 11,
                      fontWeight: 600,
                      color: theme.palette.text.primary,
                      paddingRight: 4,
                    }}
                  >
                    {item.ticker}
                  </div>
                </foreignObject>

                {/* Bar */}
                <rect
                  x={barX}
                  y={y + 2}
                  width={Math.max(clampedBarWidth, 1)}
                  height={BAR_HEIGHT - 4}
                  rx={3}
                  fill={barColor}
                  opacity={0.85}
                />

                {/* Value label on the bar */}
                {clampedBarWidth > 50 && (
                  <text
                    x={isPositive ? barX + clampedBarWidth - 4 : barX + 4}
                    y={y + BAR_HEIGHT / 2}
                    textAnchor={isPositive ? 'end' : 'start'}
                    dominantBaseline="central"
                    fontSize={10}
                    fontWeight={600}
                    fill="#fff"
                  >
                    {formatMetricValue(item.metricValue, metric, formatCurrency)}
                  </text>
                )}
              </g>
            )
          })}
        </svg>
      )}

      {tooltip && (
        <Portal>
          <div
            style={{
              position: 'fixed',
              top: tooltip.y,
              left: tooltip.x,
              backgroundColor: 'rgba(0, 0, 0, 0.88)',
              color: 'white',
              padding: '8px 12px',
              borderRadius: 6,
              fontSize: 12,
              lineHeight: 1.5,
              pointerEvents: 'none',
              zIndex: 9999,
              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
              maxWidth: 240,
            }}
          >
            <Typography variant="caption" sx={{ fontWeight: 700, display: 'block', color: 'white' }}>
              {tooltip.data.name || tooltip.data.ticker}
            </Typography>
            <div>{METRIC_LABELS[metric]}: {formatMetricValue(tooltip.data.value, metric, formatCurrency)}</div>
            <div>Valor Atual: {formatCurrency(tooltip.data.currentValue)}</div>
            <div>Investido: {formatCurrency(tooltip.data.invested)}</div>
          </div>
        </Portal>
      )}
    </Box>
  )
}
