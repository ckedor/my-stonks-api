import type { ThemePaletteConfig } from '@/theme/themes'
import { Box, Grid, TextField, Typography } from '@mui/material'
import { useEffect, useRef, useState } from 'react'

interface Props {
  config: ThemePaletteConfig
  onChange: (config: ThemePaletteConfig) => void
}

function ColorField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (v: string) => void
}) {
  const isHex = /^#[0-9a-fA-F]{3,8}$/.test(value)
  const [localColor, setLocalColor] = useState(isHex ? value.slice(0, 7) : '#000000')
  const isPickerOpen = useRef(false)

  // Sync from parent when value changes externally (e.g. text field edit)
  useEffect(() => {
    if (!isPickerOpen.current) {
      setLocalColor(isHex ? value.slice(0, 7) : '#000000')
    }
  }, [value, isHex])

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box
        component="input"
        type="color"
        value={localColor}
        onFocus={() => { isPickerOpen.current = true }}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLocalColor(e.target.value)}
        onBlur={(e: React.FocusEvent<HTMLInputElement>) => {
          isPickerOpen.current = false
          onChange(e.target.value)
        }}
        sx={{
          width: 36,
          height: 36,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          cursor: 'pointer',
          p: 0,
          '&::-webkit-color-swatch-wrapper': { p: 0 },
          '&::-webkit-color-swatch': { border: 'none', borderRadius: 4 },
        }}
      />
      <TextField
        size="small"
        label={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        sx={{ flex: 1 }}
      />
    </Box>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Box>
      <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Grid container spacing={2}>
        {children}
      </Grid>
    </Box>
  )
}

export default function ThemePaletteForm({ config, onChange }: Props) {
  const set = <K extends keyof ThemePaletteConfig>(key: K, value: ThemePaletteConfig[K]) =>
    onChange({ ...config, [key]: value })

  const setNested = <
    K extends keyof ThemePaletteConfig,
    NK extends keyof Extract<ThemePaletteConfig[K], object>,
  >(
    key: K,
    nestedKey: NK,
    value: string,
  ) => {
    const parent = config[key] as Record<string, string>
    onChange({ ...config, [key]: { ...parent, [nestedKey]: value } })
  }

  const setChartColor = (index: number, value: string) => {
    const colors = [...config.chart.colors]
    colors[index] = value
    onChange({ ...config, chart: { ...config.chart, colors } })
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Background */}
      <Section title="Fundo">
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Background"
            value={config.background.default}
            onChange={(v) => setNested('background', 'default' as never, v)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Paper (Cards)"
            value={config.background.paper}
            onChange={(v) => setNested('background', 'paper' as never, v)}
          />
        </Grid>
      </Section>

      {/* Text */}
      <Section title="Texto">
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Primário"
            value={config.text.primary}
            onChange={(v) => setNested('text', 'primary' as never, v)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Secundário"
            value={config.text.secondary}
            onChange={(v) => setNested('text', 'secondary' as never, v)}
          />
        </Grid>
      </Section>

      {/* Main colors */}
      <Section title="Cores Principais">
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField label="Primary" value={config.primary} onChange={(v) => set('primary', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Secondary"
            value={config.secondary}
            onChange={(v) => set('secondary', v)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField label="Golden" value={config.golden} onChange={(v) => set('golden', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField label="Dark" value={config.dark} onChange={(v) => set('dark', v)} />
        </Grid>
      </Section>

      {/* Status */}
      <Section title="Status">
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ColorField label="Sucesso" value={config.success} onChange={(v) => set('success', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ColorField label="Erro" value={config.error} onChange={(v) => set('error', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ColorField label="Aviso" value={config.warning} onChange={(v) => set('warning', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ColorField label="Info" value={config.info} onChange={(v) => set('info', v)} />
        </Grid>
      </Section>

      {/* Layout */}
      <Section title="Layout (Sidebar / Topbar)">
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField label="Sidebar" value={config.sidebar} onChange={(v) => set('sidebar', v)} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Topbar Fundo"
            value={config.topbar.background}
            onChange={(v) => setNested('topbar', 'background' as never, v)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Topbar Texto"
            value={config.topbar.text}
            onChange={(v) => setNested('topbar', 'text' as never, v)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField label="Divider" value={config.divider} onChange={(v) => set('divider', v)} />
        </Grid>
      </Section>

      {/* Chart */}
      <Section title="Gráficos">
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Grid"
            value={config.chart.grid}
            onChange={(v) => onChange({ ...config, chart: { ...config.chart, grid: v } })}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <ColorField
            label="Label"
            value={config.chart.label}
            onChange={(v) => onChange({ ...config, chart: { ...config.chart, label: v } })}
          />
        </Grid>
        {config.chart.colors.map((color, i) => (
          <Grid key={i} size={{ xs: 6, sm: 4, md: 3 }}>
            <ColorField label={`Cor ${i + 1}`} value={color} onChange={(v) => setChartColor(i, v)} />
          </Grid>
        ))}
      </Section>
    </Box>
  )
}
