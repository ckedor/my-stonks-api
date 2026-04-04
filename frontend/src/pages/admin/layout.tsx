import { useAuthStore } from '@/stores/auth'

import { Box, Typography, useMediaQuery } from '@mui/material'
import { useTheme } from '@mui/material/styles'

import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import AdminSidebar, { DRAWER_WIDTH } from './Sidebar'
import AdminTopbar from './Topbar'

const COLLAPSE_MEDIA = '(max-width: 1366px)'

export default function AdminLayout() {
  const { isAuthenticated, isLoading, user } = useAuthStore()
  const theme = useTheme()
  const collapsedMode = useMediaQuery(COLLAPSE_MEDIA)
  const [drawerOpen, setDrawerOpen] = useState(false)

  if (isLoading) return null

  if (!isAuthenticated) {
    if (typeof window !== 'undefined') window.location.href = '/login'
    return null
  }

  // Verifica se o usuário é admin
  if (!user?.is_admin) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
        }}
      >
        <Typography variant="h4" color="error">
          Acesso Negado
        </Typography>
        <Typography variant="body1">
          Você não tem permissão para acessar esta área administrativa.
        </Typography>
      </Box>
    )
  }

  const variant = collapsedMode ? 'persistent' : 'permanent'

  return (
    <Box sx={{ display: 'flex' }}>
        <AdminSidebar
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
              variant === 'persistent' && drawerOpen ? `${DRAWER_WIDTH}px` : 0,
            transition: theme.transitions.create('margin-left', {
              duration: theme.transitions.duration.enteringScreen,
            }),
          }}
        >
          <AdminTopbar
            showMenuButton={variant === 'persistent'}
            onMenuClick={() => setDrawerOpen((v) => !v)}
          />
          <Box px={4} pt={2} pb={1} sx={{ flexGrow: 1, overflow: 'auto' }}>
            <Outlet />
          </Box>
        </Box>
      </Box>
  )
}
