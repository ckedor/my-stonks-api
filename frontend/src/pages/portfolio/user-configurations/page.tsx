
import BrushIcon from '@mui/icons-material/Brush'
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions'
import { Box, Tab, Tabs, Typography } from '@mui/material'
import { useState } from 'react'
import IntegrationsTab from './IntegrationsTab'
import ThemeTab from './ThemeTab'

export default function UserConfigurationPage() {
  const [tab, setTab] = useState(0)

  return (
    <Box mt={3} pt={1}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>Configurações</Typography>
      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
      >
        <Tab icon={<BrushIcon />} iconPosition="start" label="Aparência" />
        <Tab icon={<IntegrationInstructionsIcon />} iconPosition="start" label="Integrações" />
      </Tabs>

      {tab === 0 && <ThemeTab />}
      {tab === 1 && <IntegrationsTab />}
    </Box>
  )
}
