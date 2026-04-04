import { usePositionsStore } from '@/stores/portfolio/positions'
import {
    Box,
    CircularProgress,
    Divider,
    List,
    ListItemButton,
    ListItemText,
    Typography,
    useTheme,
} from '@mui/material'
import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'

interface Props {
  selectedAssetId: number
}

export default function AssetSidebar({ selectedAssetId }: Props) {
  const { positions, loading } = usePositionsStore()
  const navigate = useNavigate()
  const theme = useTheme()

  const totalValue = useMemo(
    () => positions.reduce((s, p) => s + p.value, 0),
    [positions],
  )

  const grouped = useMemo(() => {
    const map: Record<string, typeof positions> = {}
    for (const pos of positions) {
      const cat = pos.category || 'Sem categoria'
      if (!map[cat]) map[cat] = []
      map[cat].push(pos)
    }
    // Sort each group by value desc
    for (const cat of Object.keys(map)) {
      map[cat].sort((a, b) => b.value - a.value)
    }
    // Sort categories by total value desc
    return Object.entries(map).sort(
      ([, a], [, b]) =>
        b.reduce((s, p) => s + p.value, 0) - a.reduce((s, p) => s + p.value, 0),
    )
  }, [positions])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={3}>
        <CircularProgress size={24} />
      </Box>
    )
  }

  return (
    <Box>
      {grouped.map(([category, assets], idx) => (
        <Box key={category} mb={0.5}>
          {idx > 0 && <Divider sx={{ mx: 1, mb: 0.5 }} />}
          <Typography
            variant="overline"
            sx={{
              px: 1.5,
              pt: idx > 0 ? 0.8 : 0.3,
              pb: 0.3,
              display: 'block',
              color: 'primary.main',
              fontSize: '0.68rem',
              fontWeight: 700,
              letterSpacing: 1.2,
              lineHeight: 1.5,
            }}
          >
            {category}
          </Typography>
          <List dense disablePadding>
            {assets.map((pos) => {
              const isSelected = pos.asset_id === selectedAssetId
              const pct = totalValue > 0 ? ((pos.value / totalValue) * 100).toFixed(1) : '0.0'
              return (
                <ListItemButton
                  key={pos.asset_id}
                  selected={isSelected}
                  onClick={() => navigate(`/portfolio/asset/${pos.asset_id}`)}
                  sx={{
                    py: 0.3,
                    px: 1.5,
                    minHeight: 32,
                    borderRadius: 1,
                    mx: 0.5,
                    mb: 0.2,
                    ...(isSelected && {
                      backgroundColor: theme.palette.primary.main + '18',
                      borderLeft: `3px solid ${theme.palette.primary.main}`,
                      pl: 1.2,
                    }),
                  }}
                >
                  <ListItemText
                    primary={pos.ticker}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: isSelected ? 700 : 400,
                      fontSize: '0.8rem',
                      noWrap: true,
                    }}
                  />
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ fontSize: '0.7rem', ml: 1, whiteSpace: 'nowrap' }}
                  >
                    {pct}%
                  </Typography>
                </ListItemButton>
              )
            })}
          </List>
        </Box>
      ))}
    </Box>
  )
}
