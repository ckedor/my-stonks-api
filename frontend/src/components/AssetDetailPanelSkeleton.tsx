import { Box, Divider, Skeleton } from '@mui/material'

function InfoRowSkeleton() {
  return (
    <Box display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
      <Skeleton variant="text" width={90} height={20} />
      <Skeleton variant="text" width={70} height={20} />
    </Box>
  )
}

function CardSkeleton() {
  return (
    <Box sx={{ p: 4 }}>
      {/* Ticker + name + chips */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
        <Box>
          <Skeleton variant="text" width={100} height={32} />
          <Skeleton variant="text" width={180} height={18} sx={{ mt: 0.5 }} />
        </Box>
        <Box display="flex" flexDirection="column" alignItems="flex-end" gap={0.5}>
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={50} height={22} />
        </Box>
      </Box>

      <Divider sx={{ my: 1.5 }} />

      {/* Valor total + donut */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1.5}>
        <Box>
          <Skeleton variant="text" width={60} height={14} />
          <Skeleton variant="text" width={140} height={32} />
        </Box>
        <Skeleton variant="circular" width={48} height={48} />
      </Box>

      <Divider sx={{ my: 1.5 }} />

      <InfoRowSkeleton />
      <InfoRowSkeleton />
      <InfoRowSkeleton />

      <Divider sx={{ my: 1.5 }} />

      <InfoRowSkeleton />
      <InfoRowSkeleton />

      <Divider sx={{ my: 1.5 }} />

      <InfoRowSkeleton />
      <InfoRowSkeleton />
      <InfoRowSkeleton />

      <Divider sx={{ my: 1.5 }} />

      <InfoRowSkeleton />
      <InfoRowSkeleton />
      <InfoRowSkeleton />
    </Box>
  )
}

function TabsSkeleton() {
  return (
    <Box
      sx={{
        display: 'flex',
        gap: 2,
        px: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        minHeight: 42,
        alignItems: 'center',
        justifyContent: 'flex-end',
      }}
    >
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} variant="text" width={80} height={24} />
      ))}
    </Box>
  )
}

function ChartSkeleton() {
  return (
    <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 4 }}>
      {/* Chips bar */}
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          px: 1,
          py: 1,
          bgcolor: 'action.hover',
          borderRadius: 1,
        }}
      >
        <Skeleton variant="rounded" width={100} height={24} />
        <Skeleton variant="rounded" width={120} height={24} />
        <Skeleton variant="rounded" width={90} height={24} />
      </Box>

      {/* Main chart area */}
      <Skeleton variant="rounded" width="100%" height={350} sx={{ borderRadius: 2 }} />

      {/* Second chart area */}
      <Skeleton variant="rounded" width="100%" height={250} sx={{ borderRadius: 2 }} />
    </Box>
  )
}

export default function AssetDetailPanelSkeleton() {
  return (
    <Box display="flex" sx={{ alignItems: 'stretch', height: '100%' }}>
      {/* Left sidebar */}
      <Box
        sx={{
          width: 400,
          minWidth: 320,
          flexShrink: 0,
          borderRight: '1px solid',
          borderColor: 'divider',
        }}
      >
        <CardSkeleton />
      </Box>

      {/* Right side */}
      <Box flex={1} minWidth={0} display="flex" flexDirection="column">
        <TabsSkeleton />
        <ChartSkeleton />
      </Box>
    </Box>
  )
}
