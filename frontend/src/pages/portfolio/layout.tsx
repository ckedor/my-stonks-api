import { useAuthStore } from '@/stores/auth'

import { Box, useMediaQuery } from '@mui/material'
import { useTheme } from '@mui/material/styles'

import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar, { DRAWER_WIDTH } from './Sidebar'
import Topbar from './Topbar'

const COLLAPSE_MEDIA = '(max-width: 1366px)'

export default function PortfolioLayout() {
  const { isAuthenticated, isLoading } = useAuthStore()
  const theme = useTheme()
  const collapsedMode = useMediaQuery(COLLAPSE_MEDIA)
  const [drawerOpen, setDrawerOpen] = useState(false)

  if (isLoading) return null
  if (!isAuthenticated) {
    if (typeof window !== 'undefined') window.location.href = '/login'
    return null
  }

  const variant = collapsedMode ? 'persistent' : 'permanent'

  return (
    <Box sx={{ display: 'flex'}}>
      <Sidebar
        variant={variant}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
      {variant === 'permanent' && <Box sx={{ width: DRAWER_WIDTH, flexShrink: 0 }} />}

      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          overflow: 'hidden',
          ml:
            variant === 'persistent' && drawerOpen
              ? `${DRAWER_WIDTH}px`
              : 0,
          transition: theme.transitions.create('margin-left', {
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Topbar
          showMenuButton={variant === 'persistent'}
          onMenuClick={() => setDrawerOpen((v) => !v)}
        />
        <Box 
          px={4} pb={1} sx={{ flexGrow: 1, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}
