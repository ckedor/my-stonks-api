
import { logout } from '@/actions/auth'
import { syncPortfolios } from '@/actions/portfolio'
import PortfolioForm from '@/components/PortfolioForm'
import { useAuthStore } from '@/stores/auth'
import { usePortfolioStore } from '@/stores/portfolio'

import AccountCircle from '@mui/icons-material/AccountCircle'
import AddIcon from '@mui/icons-material/Add'
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings'
import EditIcon from '@mui/icons-material/Edit'
import ExpandMore from '@mui/icons-material/ExpandMore'
import MenuIcon from '@mui/icons-material/Menu'

import {
    AppBar,
    Box,
    CircularProgress,
    Divider,
    IconButton,
    ListSubheader,
    Menu,
    MenuItem,
    Select,
    Toolbar,
    Typography
} from '@mui/material'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import RecalculatePortfolioButton from '@/components/RecalculatePortfolioButton'
import { ThemeToggleButton } from '@/components/ui/ThemeToggleButton'

export default function Topbar({
  showMenuButton = false,
  onMenuClick,
}: {
  showMenuButton?: boolean
  onMenuClick?: () => void
}) {
  const user = useAuthStore(s => s.user)
  const { portfolios, loading, selectedPortfolio, setSelectedPortfolio } =
    usePortfolioStore()
  const navigate = useNavigate()

  const [selected, setSelected] = useState<number | null>(selectedPortfolio?.id ?? null)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const open = Boolean(anchorEl)
  const [openForm, setOpenForm] = useState(false)
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    if (selectedPortfolio && selected !== selectedPortfolio.id) {
      setSelected(selectedPortfolio.id)
    }
  }, [selectedPortfolio])

  const handleOpenCreate = () => { setEditMode(false); setOpenForm(true) }
  const handleOpenEdit = () => { setEditMode(true); setOpenForm(true) }

  return (
    <>
      <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Toolbar sx={{ justifyContent: 'space-between', minHeight: 48 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1}}>
            {showMenuButton && (
              <IconButton edge="start" aria-label="menu" onClick={onMenuClick}>
                <MenuIcon />
              </IconButton>
            )}

          </Box>

          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <ThemeToggleButton />
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <>
              
              <Select
                value={selected ?? ''}
                onChange={(e) => {
                  const value = Number(e.target.value)
                  if (value === -1) { handleOpenEdit(); return }
                  if (value === -2) { handleOpenCreate(); return }
                  setSelected(value)
                  const portfolio = portfolios.find((p) => p.id === value)
                  if (portfolio) setSelectedPortfolio(portfolio)
                }}
                size="small"
                IconComponent={ExpandMore}
                sx={{ minWidth: 150, bgcolor: 'background.default' }}
                renderValue={(value) => portfolios.find((p) => p.id === value)?.name || ''}
              >
                {portfolios.map((p) => (
                  <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                ))}
                <ListSubheader>──────────</ListSubheader>
                <MenuItem value={-1}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <EditIcon sx={{ color: 'primary.main' }} fontSize="small" />
                    <Typography sx={{ fontStyle: 'italic', color: 'primary.main' }}>Editar Carteira</Typography>
                  </Box>
                </MenuItem>
                <MenuItem value={-2}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <AddIcon sx={{ color: 'primary.main' }} fontSize="small" />
                    <Typography sx={{ fontStyle: 'italic', color: 'primary.main' }}>Nova Carteira</Typography>
                  </Box>
                </MenuItem>
              </Select>
              <RecalculatePortfolioButton />
              </>
            )}

            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
              <AccountCircle />
            </IconButton>
            <Menu anchorEl={anchorEl} open={open} onClose={() => setAnchorEl(null)}>
              <MenuItem disabled>{user?.email}</MenuItem>
              <Divider />
              {user?.is_admin && (
                <MenuItem onClick={() => { setAnchorEl(null); navigate('/admin/assets'); }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <AdminPanelSettingsIcon fontSize="small" />
                    Painel Administrativo
                  </Box>
                </MenuItem>
              )}
              <MenuItem onClick={logout}>Sair</MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <PortfolioForm
        open={openForm}
        onClose={() => setOpenForm(false)}
        onSave={(newId) => { syncPortfolios(true); setSelected(newId ?? null); setOpenForm(false) }}
        portfolio={editMode ? (selectedPortfolio ?? undefined) : undefined}
      />
    </>
  )
}
