
import { useCurrency } from '@/hooks/useCurrency'
import { PortfolioPositionEntry } from '@/types'
import { Box, useTheme } from '@mui/material'
import { localPoint } from '@visx/event'
import { Treemap, hierarchy } from '@visx/hierarchy'
import { scaleLinear } from '@visx/scale'
import { TooltipWithBounds, useTooltip, useTooltipInPortal } from '@visx/tooltip'
import { treemapResquarify } from 'd3-hierarchy'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { DistributionMetric } from './PerformanceBarChart'

interface PortfolioHeatMapProps {
  positions: PortfolioPositionEntry[]
  metric?: DistributionMetric
  onAssetSelect?: (assetId: number) => void
}

function getMetricValue(pos: PortfolioPositionEntry, metric: DistributionMetric): number {
  switch (metric) {
    case 'profit':
      return (pos.value ?? 0) - (pos.total_invested ?? 0)
    case 'cagr':
      return (pos.cagr ?? 0)
    case 'twelve_months_return':
      return (pos.twelve_months_return ?? 0)
    case 'acc_return':
      return (pos.acc_return ?? 0)
  }
}

function formatMetricDisplay(value: number, metric: DistributionMetric, fmtCurrency?: (v: number) => string): string {
  if (metric === 'profit') {
    return fmtCurrency ? fmtCurrency(value) : `R$ ${(value / 1000).toFixed(1)}k`
  }
  const pct = value * 100
  return (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%'
}

export default function PortfolioHeatMap({ positions, metric = 'twelve_months_return', onAssetSelect }: PortfolioHeatMapProps) {
  const total = positions.reduce((sum, p) => sum + p.value, 0)

  const theme = useTheme()
  const { format: formatCurrency } = useCurrency()

  // Agrupar e ordenar categorias por valor total (desc)
  const grouped = useMemo(() => Object.entries(
    positions.reduce<Record<string, PortfolioPositionEntry[]>>((acc, pos) => {
      const key = pos.category || '(Sem categoria)'
      if (!acc[key]) acc[key] = []
      acc[key].push(pos)
      return acc
    }, {})
  ).sort(([, a], [, b]) => {
    const totalA = a.reduce((acc, p) => acc + p.value, 0)
    const totalB = b.reduce((acc, p) => acc + p.value, 0)
    return totalB - totalA
  }), [positions])

  const data = useMemo(() => ({
    name: 'Carteira',
    children: grouped.map(([category, items]) => ({
      name: category,
      children: items.map((pos) => ({
        name: pos.ticker,
        value: pos.value,
        metricValue: getMetricValue(pos, metric),
        asset_id: pos.asset_id,
        ticker: pos.ticker,
        currentValue: pos.value,
        invested: pos.total_invested ?? 0,
      })),
    })),
  }), [grouped, metric])

  const colorDomain = metric === 'profit'
    ? [-50000, 0, 100000]
    : [-0.2, 0, 0.3]

  const colorScale = scaleLinear<string>({
    domain: colorDomain,
    range: ['rgb(206, 43, 43)', 'rgb(117, 117, 117)', 'rgb(39, 174, 96)'],
    clamp: true,
  })

  const { tooltipData, tooltipLeft, tooltipTop, tooltipOpen, showTooltip, hideTooltip } =
    useTooltip<{ name: string; value: number; pct: number; metricValue: number; invested: number }>()

  const { containerRef } = useTooltipInPortal({ scroll: true })

  const wrapperRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

  useEffect(() => {
    if (!wrapperRef.current) return
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      setDimensions({ width, height })
    })
    observer.observe(wrapperRef.current)
    return () => observer.disconnect()
  }, [])

  return (
    <Box
      ref={wrapperRef}
      sx={{
        position: 'relative',
        width: '100%',
        height: 'calc(100vh - 200px)',
      }}
    >
      <Box
        ref={containerRef}
        sx={{
          position: 'relative',
          width: '100%',
          height: '100%',
          backgroundColor: theme.palette.background.default,
        }}
      >
        {dimensions.width > 0 && dimensions.height > 0 && (
          <Treemap
            root={hierarchy<any>(data).sum((d) => d.value)}
            size={[dimensions.width, dimensions.height]}
            tile={treemapResquarify}
            round
            paddingOuter={6}
            paddingInner={1}
            paddingTop={20}
          >
            {(treemap) => (
              <>
                {treemap.children?.map((group, idx) => {
                  const { x0, y0, x1, y1 } = group
                  return (
                    <div
                      key={`group-${idx}`}
                      style={{
                        position: 'absolute',
                        top: y0,
                        left: x0,
                        width: x1 - x0,
                        height: y1 - y0,
                        border: `1px solid ${theme.palette.background.default}`,
                        boxSizing: 'border-box',
                        pointerEvents: 'none',
                      }}
                    >
                      <div
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 6,
                          fontSize: 11,
                          fontWeight: 'bold',
                          color: theme.palette.text.primary,
                          padding: '1px 6px',
                          borderRadius: 4,
                          pointerEvents: 'none',
                        }}
                      >
                        {group.data.name}
                      </div>
                    </div>
                  )
                })}

                {treemap.leaves().map((node, i) => {
                  const { x0, y0, x1, y1 } = node
                  const width = x1 - x0
                  const height = y1 - y0
                  const pos = node.data
                  const pct = (pos.value / total) * 100
                  const colorInput = metric === 'profit' ? pos.metricValue : pos.metricValue

                  return (
                    <div
                      key={i}
                      style={{
                        position: 'absolute',
                        top: y0,
                        left: x0,
                        width,
                        height,
                        backgroundColor: colorScale(colorInput),
                        color: '#dededeff',
                        fontSize: 10,
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        padding: 2,
                        cursor: 'pointer',
                        transition: 'background-color 0.3s ease',
                      }}
                      onClick={() => onAssetSelect?.(pos.asset_id)}
                      onMouseMove={(e) => {
                        const coords = localPoint(e)
                        showTooltip({
                          tooltipLeft: coords?.x,
                          tooltipTop: coords?.y,
                          tooltipData: {
                            name: pos.ticker,
                            value: pos.value,
                            pct,
                            metricValue: pos.metricValue,
                            invested: pos.invested,
                          },
                        })
                      }}
                      onMouseLeave={hideTooltip}
                    >
                      <strong>{pos.ticker}</strong>
                      <span>{formatMetricDisplay(pos.metricValue, metric, formatCurrency)}</span>
                    </div>
                  )
                })}
              </>
            )}
          </Treemap>
        )}

        {tooltipOpen && tooltipData && (
          <TooltipWithBounds
            top={tooltipTop}
            left={tooltipLeft}
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.85)',
              color: 'white',
              padding: '6px 10px',
              borderRadius: 4,
              fontSize: 12,
              maxWidth: 220,
              lineHeight: 1.4,
              pointerEvents: 'none',
              position: 'absolute',
              zIndex: 9999,
              boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
            }}
          >
            <div>
              <strong>{tooltipData.name}</strong>
            </div>
            <div>Valor: {formatCurrency(tooltipData.value)}</div>
            <div>Participação: {tooltipData.pct.toFixed(2)}%</div>
            <div>{formatMetricDisplay(tooltipData.metricValue, metric, formatCurrency)}</div>
            {tooltipData.invested > 0 && (
              <div>Investido: {formatCurrency(tooltipData.invested)}</div>
            )}
          </TooltipWithBounds>
        )}
      </Box>
    </Box>
  )
}
