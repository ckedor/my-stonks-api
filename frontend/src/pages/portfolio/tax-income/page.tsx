
import { usePortfolioStore } from '@/stores/portfolio'
import { Box, FormControl, InputLabel, MenuItem, Select, Tab, Tabs, Typography } from '@mui/material'
import dayjs from 'dayjs'
import { useState } from 'react'
import AssetsAndRights from './AssetsAndRights'
import CommonOperationsTaxIncome from './CommonOperationsTaxIncome'
import DarfSummaryTable from './DarfSummaryTable'
import FIITaxIncome from './FIITaxIncome'

export default function TaxIncomePage() {
  const selectedPortfolio = usePortfolioStore(s => s.selectedPortfolio)
  const [fiscalYear, setFiscalYear] = useState(dayjs().year() - 1)
  const [tabIndex, setTabIndex] = useState(0)

  const years = Array.from({ length: 5 }, (_, i) => dayjs().year() - i)

  if (!selectedPortfolio?.id) return null

  return (
    <Box pt={2}>
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>Declaração de Imposto de Renda</Typography>
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <FormControl variant="standard" sx={{ minWidth: 100 }}>
          <InputLabel>Ano</InputLabel>
          <Select
            value={fiscalYear}
            onChange={(e) => setFiscalYear(Number(e.target.value))}
            disableUnderline
          >
            {years.map((year) => (
              <MenuItem key={year} value={year}>
                {year}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Tabs value={tabIndex} onChange={(_, idx) => setTabIndex(idx)}>
          <Tab label="DARF" />
          <Tab label="Bens e Direitos" />
          <Tab label="Apuração FIIs" />
          <Tab label="Apuração Operações Comuns" />
        </Tabs>
      </Box>

      {tabIndex === 0 && (
        <DarfSummaryTable fiscalYear={fiscalYear} portfolioId={selectedPortfolio.id} />
      )}
      {tabIndex === 1 && (
        <AssetsAndRights fiscalYear={fiscalYear} portfolioId={selectedPortfolio.id} />
      )}
      {tabIndex === 2 && (
        <FIITaxIncome fiscalYear={fiscalYear} portfolioId={selectedPortfolio.id} />
      )}
      {tabIndex === 3 && (
        <CommonOperationsTaxIncome fiscalYear={fiscalYear} portfolioId={selectedPortfolio.id} />
      )}
    </Box>
  )
}
