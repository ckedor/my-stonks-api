import { usePageTitleStore } from '@/stores/page-title'
import { Typography } from '@mui/material'

export default function PageHeader() {
  const { title } = usePageTitleStore()

  if (!title) return null

  return (
    <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
      {title}
    </Typography>
  )
}
