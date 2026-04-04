import { buildMuiTheme, type ThemePaletteConfig } from '@/theme/themes'
import { Box, Paper, ThemeProvider, Typography } from '@mui/material'
import { useMemo } from 'react'
import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ComposedChart,
    Legend,
    Line,
    Pie,
    PieChart,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'

const barData = [
  { month: 'Jan', '2025': 180, '2026': 220 },
  { month: 'Fev', '2025': 150, '2026': 190 },
  { month: 'Mar', '2025': 200, '2026': 260 },
  { month: 'Abr', '2025': 170, '2026': 210 },
  { month: 'Mai', '2025': 230, '2026': 280 },
  { month: 'Jun', '2025': 190, '2026': 250 },
]

const returnsData = [
  { date: 'Jan', Carteira: 1.2, CDI: 0.9 },
  { date: 'Fev', Carteira: 2.5, CDI: 1.8 },
  { date: 'Mar', Carteira: 1.8, CDI: 2.7 },
  { date: 'Abr', Carteira: 4.1, CDI: 3.6 },
  { date: 'Mai', Carteira: 3.2, CDI: 4.5 },
  { date: 'Jun', Carteira: 6.0, CDI: 5.4 },
]

const pieData = [
  { name: 'Ações BR', value: 35 },
  { name: 'FIIs', value: 25 },
  { name: 'Renda Fixa', value: 20 },
  { name: 'Cripto', value: 10 },
  { name: 'Ações US', value: 10 },
]

interface Props {
  config: ThemePaletteConfig
}

export default function ThemePreviewPanel({ config }: Props) {
  const theme = useMemo(() => buildMuiTheme(config), [config])
  const colors = config.chart.colors

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          bgcolor: config.background.default,
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          overflow: 'hidden',
        }}
      >
        {/* Mini topbar */}
        <Box
          sx={{
            bgcolor: config.topbar.background,
            color: config.topbar.text,
            px: 2,
            py: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: config.primary }} />
          <Typography variant="subtitle2" sx={{ color: config.topbar.text }}>
            Preview do Tema
          </Typography>
        </Box>

        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Status color chips */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {[
              { label: 'Primary', color: config.primary },
              { label: 'Secondary', color: config.secondary },
              { label: 'Sucesso', color: config.success },
              { label: 'Erro', color: config.error },
              { label: 'Aviso', color: config.warning },
              { label: 'Info', color: config.info },
              { label: 'Golden', color: config.golden },
            ].map((c) => (
              <Paper
                key={c.label}
                sx={{
                  px: 1.5,
                  py: 0.5,
                  bgcolor: c.color,
                  color: config.mode === 'dark' ? '#fff' : '#000',
                  borderRadius: 2,
                }}
              >
                <Typography variant="caption" fontWeight={600}>
                  {c.label}
                </Typography>
              </Paper>
            ))}
          </Box>

          {/* Bar chart — Dividendos */}
          <Paper sx={{ p: 2 }}>
            <Typography
              variant="subtitle2"
              sx={{ mb: 1, color: config.text.primary }}
              fontWeight={700}
            >
              Proventos por Mês
            </Typography>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" stroke={config.chart.grid} />
                <XAxis dataKey="month" stroke={config.text.primary} tick={{ fontSize: 12 }} />
                <YAxis
                  orientation="right"
                  stroke={config.text.primary}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip />
                <Legend />
                <Bar dataKey="2025" fill={config.primary} radius={[4, 4, 0, 0]} />
                <Bar dataKey="2026" fill={config.secondary} radius={[4, 4, 0, 0]} />
                <ReferenceLine
                  y={210}
                  stroke={config.text.primary}
                  strokeDasharray="5 5"
                  strokeWidth={1.5}
                />
              </BarChart>
            </ResponsiveContainer>
          </Paper>

          {/* Line chart + Pie side by side */}
          <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' } }}>
            <Paper sx={{ p: 2, flex: 1 }}>
              <Typography
                variant="subtitle2"
                sx={{ mb: 1, color: config.text.primary }}
                fontWeight={700}
              >
                Rentabilidade Acumulada
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <ComposedChart data={returnsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={config.chart.grid} />
                  <XAxis dataKey="date" stroke={config.text.primary} tick={{ fontSize: 12 }} />
                  <YAxis
                    orientation="right"
                    stroke={config.text.primary}
                    tick={{ fontSize: 12 }}
                    tickFormatter={(v) => `${v}%`}
                  />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="Carteira"
                    stroke={config.primary}
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="CDI"
                    stroke={config.secondary}
                    strokeWidth={2}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Paper>

            <Paper sx={{ p: 2, flex: 1 }}>
              <Typography
                variant="subtitle2"
                sx={{ mb: 1, color: config.text.primary }}
                fontWeight={700}
              >
                Alocação por Classe
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    dataKey="value"
                    label={(props) => {
                      const name = String(props.name ?? '')
                      const percent = Number(props.value ?? 0) / pieData.reduce((a, b) => a + b.value, 0)
                      return `${name} ${(percent * 100).toFixed(0)}%`
                    }}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={colors[i % colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Box>

          {/* Text preview */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ color: config.text.primary }}>
              Título de Exemplo
            </Typography>
            <Typography variant="body1" sx={{ color: config.text.primary }}>
              Texto primário para verificar legibilidade sobre o fundo.
            </Typography>
            <Typography variant="body2" sx={{ color: config.text.secondary }}>
              Texto secundário em tom mais suave para informações complementares.
            </Typography>
          </Paper>
        </Box>
      </Box>
    </ThemeProvider>
  )
}
