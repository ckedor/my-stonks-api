import { Box, CircularProgress } from '@mui/material'

export default function LoadingSpinner() {
  return (
    <Box minHeight="80vh" display="flex" justifyContent="center" alignItems="center">
      <CircularProgress size={48} thickness={4} />
    </Box>
  )
}
