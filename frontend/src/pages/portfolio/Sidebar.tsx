
import {
    Box,
    Divider,
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Typography,
} from '@mui/material'

import AddIcon from '@mui/icons-material/Add'
import DashboardIcon from '@mui/icons-material/Dashboard'
import EditIcon from '@mui/icons-material/Edit'
import ListAltIcon from '@mui/icons-material/ListAlt'
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn'
import PaidIcon from '@mui/icons-material/Paid'
import SavingsIcon from '@mui/icons-material/Savings'
import SettingsIcon from '@mui/icons-material/Settings'
import TokenIcon from '@mui/icons-material/Token'

import CategoryForm from '@/components/CategoryForm'
import DividendForm from '@/components/DividendForm'
import { useTradeFormStore } from '@/stores/trade-form'

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export const DRAWER_WIDTH = 240
const FONT_SIZE_LABEL = 16
const FONT_SIZE_HEADER = '1.4rem'

const menuItems = [
  { text: 'Resumo', icon: <DashboardIcon fontSize="small" />, path: '/portfolio/overview' },
  { text: 'Ativos', icon: <TokenIcon fontSize="small" />, path: '/portfolio/asset' },
  { text: 'Distribuição', icon: <TokenIcon fontSize="small" />, path: '/portfolio/distribution' },
  { text: 'Rentabilidade', icon: <PaidIcon fontSize="small" />, path: '/portfolio/returns' },
  { text: 'Patrimônio', icon: <SavingsIcon fontSize="small" />, path: '/portfolio/wealth' },
  { text: 'Trades', icon: <ListAltIcon fontSize="small" />, path: '/portfolio/trades' },
  { text: 'Proventos', icon: <MonetizationOnIcon fontSize="small" />, path: '/portfolio/dividends' },
  { text: 'Declaração IR', icon: <ListAltIcon fontSize="small" />, path: '/portfolio/tax-income' },
]

export default function Sidebar({
  variant,
  open,
  onClose,
}: {
  variant: 'permanent' | 'persistent'
  open: boolean                 // usado quando 'persistent'
  onClose: () => void           // fechar quando clicar em link / botão
}) {
  const navigate = useNavigate()
  const pathname = window.location.pathname
  const { openTradeForm } = useTradeFormStore()

  const [categoryFormOpen, setCategoryFormOpen] = useState(false)
  const [dividendFormOpen, setDividendFormOpen] = useState(false)

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Typography
        variant="subtitle1"
        align="center"
        sx={{ fontWeight: 'bold', fontSize: FONT_SIZE_HEADER, my: 1.05 }}
      >
        My Stonks
      </Typography>

      <Divider />

      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        <List dense>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.text}
              onClick={() => {
                navigate(item.path)
              }}
              selected={pathname === item.path}
            >
              <ListItemIcon sx={{ minWidth: 30 }}>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{ fontSize: FONT_SIZE_LABEL }}
              />
            </ListItemButton>
          ))}
        </List>

        <Divider sx={{ my: 1 }} />

        <List dense>
          <ListItemButton onClick={() => openTradeForm()}>
            <ListItemIcon sx={{ minWidth: 30 }}>
              <AddIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Cadastrar Compra"
              primaryTypographyProps={{ fontSize: FONT_SIZE_LABEL }}
            />
          </ListItemButton>

          <ListItemButton onClick={() => setDividendFormOpen(true)}>
            <ListItemIcon sx={{ minWidth: 30 }}>
              <AddIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Cadastrar Provento"
              primaryTypographyProps={{ fontSize: FONT_SIZE_LABEL }}
            />
          </ListItemButton>

          <ListItemButton onClick={() => setCategoryFormOpen(true)}>
            <ListItemIcon sx={{ minWidth: 30 }}>
              <EditIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Editar Categorias"
              primaryTypographyProps={{ fontSize: FONT_SIZE_LABEL }}
            />
          </ListItemButton>
        </List>
      </Box>

      <Divider sx={{ mt: 1 }} />
      <List dense>
        <ListItemButton onClick={() => navigate('/portfolio/user-configurations')}>
          <ListItemIcon sx={{ minWidth: 30 }}>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Configurações"
            primaryTypographyProps={{ fontSize: FONT_SIZE_LABEL }}
          />
        </ListItemButton>
      </List>
    </Box>
  )

  return (
    <>
      <Drawer
        variant={variant}                                  // 'permanent' | 'persistent'
        open={variant === 'permanent' ? true : open}       // controla quando persistent
        onClose={onClose}
        PaperProps={{
          sx: {
            width: DRAWER_WIDTH,
            pt: 1,
            pb: 1,
            height: '100vh',
            overflow: 'hidden',
            bgcolor: 'background.default',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      <CategoryForm open={categoryFormOpen} onClose={() => setCategoryFormOpen(false)} />
      <DividendForm open={dividendFormOpen} onClose={() => setDividendFormOpen(false)} />
    </>
  )
}
