import { useCurrency } from '@/hooks/useCurrency'
import { usePortfolioStore } from '@/stores/portfolio'
import { useReturnsStore } from '@/stores/portfolio/returns'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { Box, CircularProgress, Collapse, Divider, IconButton, Typography, useTheme } from '@mui/material'
import { useMemo, useState } from 'react'

interface Position {
  asset_id: number
  ticker: string
  category: string
  value: number
  acc_return: number
  cagr?: number | null
}

interface PositionTableProps {
  positions: Position[]
  selectedCategory?: string
  onCategorySelect?: (category: string) => void
  onAssetSelect?: (assetId: number) => void
}

export default function PositionTable({
  positions,
  selectedCategory: controlledCategory,
  onCategorySelect,
  onAssetSelect,
}: PositionTableProps) {
  const [internalCategory, setInternalCategory] = useState<string>('portfolio')
  const selectedCategory = controlledCategory ?? internalCategory
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)
  const selectedPortfolio = usePortfolioStore((s) => s.selectedPortfolio)
  const userCategories = selectedPortfolio?.custom_categories ?? []
  const categoryCagr = useReturnsStore((s) => s.categoryCagr)

  const theme = useTheme()

  const categoryColorMap = useMemo(() => {
    const map: Record<string, string> = {}
    for (const cat of userCategories) {
      map[cat.name] = cat.color
    }
    return map
  }, [userCategories])

  const data = useMemo(() => {
    const grouped: Record<string, { value: number; count: number; assets: Position[] }> = {}
    for (const pos of positions) {
      const categoryName = pos.category ?? '(Sem Categoria)'
      if (!grouped[categoryName]) grouped[categoryName] = { value: 0, count: 0, assets: [] }
      grouped[categoryName].value += pos.value
      grouped[categoryName].count += 1
      grouped[categoryName].assets.push(pos)
    }
    const total = Object.values(grouped).reduce((sum, v) => sum + v.value, 0)
    const rows = Object.entries(grouped)
      .map(([name, { value, count, assets }]) => ({
        category: name,
        value,
        count,
        percentage: total ? (value / total) * 100 : 0,
        returnAcc: categoryCagr[name] != null ? (categoryCagr[name] as number) * 100 : null,
        assets: assets.sort((a, b) => b.value - a.value),
      }))
      .sort((a, b) => b.value - a.value)
    return { rows, total }
  }, [positions, categoryCagr])

  const handleClick = (category: string) => {
    const next = category === selectedCategory ? 'portfolio' : category
    setInternalCategory(next)
    onCategorySelect?.(next)
  }

  const { format: fmt } = useCurrency()

  return (
    <Box sx={{ width: '100%' }}>
      <Box>
        {data.rows.map((row, i) => {
          const color = categoryColorMap[row.category] ?? theme.palette.primary.main
          const isSelected = row.category === selectedCategory
          return (
            <Box key={row.category}>
              <Box
                onClick={() => handleClick(row.category)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1.8,
                  px: 1,
                  cursor: 'pointer',
                  borderRadius: 1,
                  bgcolor: isSelected ? 'action.selected' : 'transparent',
                  '&:hover': { bgcolor: 'action.hover' },
                  transition: 'background 0.15s',
                }}
              >
                {/* Mini donut */}
                <Box sx={{ position: 'relative', width: 40, height: 40, mr: 1.5, flexShrink: 0 }}>
                  <CircularProgress
                    variant="determinate"
                    value={100}
                    size={40}
                    thickness={3}
                    sx={{ color: 'action.hover', position: 'absolute' }}
                  />
                  <CircularProgress
                    variant="determinate"
                    value={row.percentage}
                    size={40}
                    thickness={3}
                    sx={{
                      color,
                      position: 'absolute',
                      '& .MuiCircularProgress-circle': { strokeLinecap: 'round' },
                    }}
                  />
                  <Box
                    sx={{
                      position: 'absolute',
                      inset: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography sx={{ fontSize: 10, fontWeight: 600, lineHeight: 1 }}>
                      {row.percentage.toFixed(0)}%
                    </Typography>
                  </Box>
                </Box>

                {/* Category name */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body1" sx={{ fontWeight: 500, lineHeight: 1.3 }}>
                    {row.category}
                  </Typography>
                </Box>

                {/* Right: value + return + expand */}
                <Box sx={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: 1.3 }}>
                      {fmt(row.value)}
                    </Typography>
                    {row.returnAcc != null && (
                      <Typography
                        variant="caption"
                        sx={{
                          color: row.returnAcc >= 0 ? 'success.main' : 'error.main',
                          fontWeight: 500,
                        }}
                      >
                        {row.returnAcc >= 0 ? '+' : ''}{row.returnAcc.toFixed(2)}%
                      </Typography>
                    )}
                  </Box>
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation()
                      setExpandedCategory(expandedCategory === row.category ? null : row.category)
                    }}
                    sx={{ ml: 0.5 }}
                  >
                    {expandedCategory === row.category ? (
                      <ExpandLessIcon fontSize="small" />
                    ) : (
                      <ExpandMoreIcon fontSize="small" />
                    )}
                  </IconButton>
                </Box>
              </Box>

              {/* Expanded asset list */}
              <Collapse in={expandedCategory === row.category} timeout="auto" unmountOnExit>
                <Box sx={{ pl: 1, pr: 1, pb: 1 }}>
                  {row.assets.map((asset) => {
                    const assetPct = data.total ? (asset.value / data.total) * 100 : 0
                    const assetCagr = asset.cagr != null ? asset.cagr * 100 : null
                    return (
                      <Box
                        key={asset.asset_id}
                        onClick={() => onAssetSelect?.(asset.asset_id)}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          py: 0.8,
                          px: 1,
                          cursor: 'pointer',
                          borderRadius: 1,
                          '&:hover': { bgcolor: 'action.hover' },
                          transition: 'background 0.15s',
                        }}
                      >
                        {/* Mini donut - relative to portfolio */}
                        <Box sx={{ position: 'relative', width: 32, height: 32, mr: 1.5, flexShrink: 0 }}>
                          <CircularProgress
                            variant="determinate"
                            value={100}
                            size={32}
                            thickness={3}
                            sx={{ color: 'action.hover', position: 'absolute' }}
                          />
                          <CircularProgress
                            variant="determinate"
                            value={assetPct}
                            size={32}
                            thickness={3}
                            sx={{
                              color,
                              position: 'absolute',
                              '& .MuiCircularProgress-circle': { strokeLinecap: 'round' },
                            }}
                          />
                          <Box
                            sx={{
                              position: 'absolute',
                              inset: 0,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography sx={{ fontSize: 8, fontWeight: 600, lineHeight: 1 }}>
                              {assetPct.toFixed(0)}%
                            </Typography>
                          </Box>
                        </Box>

                        <Typography variant="body2" sx={{ flex: 1, fontWeight: 500 }}>
                          {asset.ticker}
                        </Typography>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: 1.3 }}>
                            {fmt(asset.value)}
                          </Typography>
                          {assetCagr != null && (
                            <Typography
                              variant="caption"
                              sx={{
                                color: assetCagr >= 0 ? 'success.main' : 'error.main',
                                fontWeight: 500,
                              }}
                            >
                              {assetCagr >= 0 ? '+' : ''}{assetCagr.toFixed(2)}%
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    )
                  })}
                </Box>
              </Collapse>

              {i < data.rows.length - 1 && <Divider />}
            </Box>
          )
        })}
      </Box>
    </Box>
  )
}
