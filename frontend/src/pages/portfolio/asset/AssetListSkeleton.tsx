import { Box, Skeleton, Stack } from '@mui/material'

const GRID_COLS = '40px 1.8fr 0.8fr 0.8fr 1fr 1fr 1fr 1fr 160px'

function RowSkeleton() {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: GRID_COLS,
        gap: 1,
        px: 1,
        py: 1,
        alignItems: 'center',
      }}
    >
      <Skeleton variant="circular" width={32} height={32} />
      <Box>
        <Skeleton variant="text" width="70%" height={18} />
        <Skeleton variant="text" width="50%" height={14} />
      </Box>
      <Skeleton variant="text" width="60%" height={18} sx={{ ml: 'auto' }} />
      <Skeleton variant="text" width="70%" height={18} sx={{ ml: 'auto' }} />
      <Skeleton variant="text" width="75%" height={18} sx={{ ml: 'auto' }} />
      <Skeleton variant="text" width="70%" height={18} sx={{ ml: 'auto' }} />
      <Skeleton variant="text" width="50%" height={18} sx={{ ml: 'auto' }} />
      <Box>
        <Skeleton variant="text" width="75%" height={18} sx={{ ml: 'auto' }} />
        <Skeleton variant="text" width="40%" height={14} sx={{ ml: 'auto' }} />
      </Box>
      <Skeleton variant="rounded" width="100%" height={32} />
    </Box>
  )
}

function GroupSkeleton({ rows }: { rows: number }) {
  return (
    <Box>
      {/* Group header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1, pb: 0.75, borderBottom: '2px solid', borderColor: 'divider' }}>
        <Skeleton variant="rounded" width={6} height={20} />
        <Skeleton variant="text" width={120} height={22} />
        <Box sx={{ flex: 1 }} />
        <Skeleton variant="text" width={100} height={22} />
      </Box>

      {/* Column headers */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: GRID_COLS,
          gap: 1,
          px: 1,
          py: 0.5,
        }}
      >
        <Box />
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} variant="text" width="60%" height={14} sx={i >= 1 && i <= 6 ? { ml: 'auto' } : undefined} />
        ))}
      </Box>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <RowSkeleton key={i} />
      ))}
    </Box>
  )
}

export default function AssetListSkeleton() {
  return (
    <Box>
      {/* Toolbar skeleton */}
      <Stack direction="row" spacing={2} mb={2} alignItems="center">
        <Skeleton variant="rounded" width={400} height={40} />
        <Skeleton variant="rounded" width={200} height={40} />
        <Box sx={{ flex: 1 }} />
        <Skeleton variant="rounded" width={160} height={40} />
      </Stack>

      {/* Groups */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <GroupSkeleton rows={5} />
        <GroupSkeleton rows={4} />
        <GroupSkeleton rows={3} />
      </Box>
    </Box>
  )
}
