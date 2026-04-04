import { Box, Grid, Skeleton } from '@mui/material'

function ChartSkeleton({ height }: { height: number }) {
  return (
    <Skeleton
      variant="rounded"
      width="100%"
      height={height}
      sx={{ borderRadius: 2 }}
    />
  )
}

function CategoryRowSkeleton() {
  return (
    <Box display="flex" alignItems="center" py={1.8} px={1} gap={1.5}>
      <Skeleton variant="circular" width={40} height={40} />
      <Box flex={1}>
        <Skeleton variant="text" width="60%" height={20} />
      </Box>
      <Box textAlign="right">
        <Skeleton variant="text" width={80} height={18} />
        <Skeleton variant="text" width={50} height={14} />
      </Box>
    </Box>
  )
}

export default function OverviewSkeleton() {
  return (
    <Box>
      {/* Hero */}
      <Box sx={{ mb: 3 }}>
        <Skeleton variant="text" width={90} height={20} sx={{ mb: 0.5 }} />
        <Skeleton variant="text" width={220} height={42} />
        <Skeleton variant="text" width={160} height={20} sx={{ mt: 0.5 }} />
      </Box>

      {/* Row 1: Chart + Pie */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 8 }}>
          <ChartSkeleton height={360} />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <ChartSkeleton height={360} />
        </Grid>
      </Grid>

      {/* Row 2: Categories + Bottom chart */}
      <Grid container spacing={3} sx={{ mt: 2 }} alignItems="flex-start">
        <Grid size={{ xs: 12, lg: 5 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <CategoryRowSkeleton key={i} />
          ))}
        </Grid>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Box display="flex" gap={2} mb={1.5}>
            <Skeleton variant="rounded" width={70} height={24} />
            <Skeleton variant="rounded" width={80} height={24} />
          </Box>
          <ChartSkeleton height={320} />
        </Grid>
      </Grid>
    </Box>
  )
}
