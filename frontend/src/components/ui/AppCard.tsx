import { Box, BoxProps } from '@mui/material'

interface AppCardProps extends BoxProps {
  children: React.ReactNode
  noPadding?: boolean
}

export default function AppCard({ children, sx, noPadding = false, ...props }: AppCardProps) {
  return (
    <Box
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2,
        p: noPadding ? 0 : 2,
        backgroundColor: 'background.paper',
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  )
}
