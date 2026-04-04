import AppTable from '@/components/ui/app-table/AppTable'
import AppCard from '@/components/ui/AppCard'
import { Box, Tab, Tabs, Typography } from '@mui/material'
import { useState } from 'react'
import ChartsTab from './ChartsTab'
import GeneralTab from './GeneralTab'
import {
    MOCK_TABLE_COLUMNS,
    MOCK_TABLE_ROWS,
    MOCK_TABLE_TOTAL,
} from './mockData'

function TabPanel({ children, value, index }: { children: React.ReactNode; value: number; index: number }) {
  if (value !== index) return null
  return <Box sx={{ pt: 3 }}>{children}</Box>
}

export default function DesignSystemPage() {
  const [tab, setTab] = useState(0)

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 2 }}>Design System</Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)}>
        <Tab label="General" />
        <Tab label="Charts" />
        <Tab label="Data Table" />
      </Tabs>

      <TabPanel value={tab} index={0}>
        <GeneralTab />
      </TabPanel>

      <TabPanel value={tab} index={1}>
        <ChartsTab />
      </TabPanel>

      <TabPanel value={tab} index={2}>
        <AppCard>
          <Typography variant="h6" gutterBottom>AppTable</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Sortable table with currency formatting and gain/loss colors
          </Typography>
          <AppTable
            columns={MOCK_TABLE_COLUMNS}
            rows={MOCK_TABLE_ROWS}
            totalRow={MOCK_TABLE_TOTAL}
            size="small"
          />
        </AppCard>
      </TabPanel>
    </Box>
  )
}
