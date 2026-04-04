import AppCard from '@/components/ui/AppCard'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import InfoIcon from '@mui/icons-material/Info'
import {
    Alert,
    Box,
    Button,
    Chip,
    Divider,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Skeleton,
    Stack,
    Switch,
    TextField,
    ToggleButton,
    ToggleButtonGroup,
    Tooltip,
    Typography,
    useTheme,
} from '@mui/material'
import { useState } from 'react'

function ColorSwatch({ color, label }: { color: string; label: string }) {
  return (
    <Box sx={{ textAlign: 'center' }}>
      <Box
        sx={{
          width: 56,
          height: 56,
          borderRadius: 2,
          bgcolor: color,
          border: '1px solid',
          borderColor: 'divider',
          mb: 0.5,
        }}
      />
      <Typography variant="caption" color="text.secondary" sx={{ fontSize: 10 }}>
        {label}
      </Typography>
    </Box>
  )
}

export default function GeneralTab() {
  const theme = useTheme()
  const [toggle, setToggle] = useState('one')

  return (
    <Stack spacing={4}>
      {/* ── Palette ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Palette</Typography>
        <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
          <ColorSwatch color={theme.palette.primary.main} label="Primary" />
          <ColorSwatch color={theme.palette.secondary.main} label="Secondary" />
          <ColorSwatch color={theme.palette.error.main} label="Error" />
          <ColorSwatch color={theme.palette.warning.main} label="Warning" />
          <ColorSwatch color={theme.palette.success.main} label="Success" />
          <ColorSwatch color={theme.palette.info.main} label="Info" />
          <ColorSwatch color={theme.palette.golden} label="Golden" />
          <ColorSwatch color={theme.palette.background.default} label="Bg Default" />
          <ColorSwatch color={theme.palette.background.paper} label="Bg Paper" />
          <ColorSwatch color={theme.palette.text.primary} label="Text Primary" />
          <ColorSwatch color={theme.palette.text.secondary} label="Text Sec." />
          <ColorSwatch color={theme.palette.divider} label="Divider" />
        </Stack>

        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Chart Colors</Typography>
        <Stack direction="row" spacing={1}>
          {theme.palette.chart.colors.map((c, i) => (
            <ColorSwatch key={i} color={c} label={`${i + 1}`} />
          ))}
        </Stack>
      </AppCard>

      {/* ── Typography ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Typography</Typography>
        <Stack spacing={1}>
          {(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] as const).map((v) => (
            <Typography key={v} variant={v}>{v} — The quick brown fox</Typography>
          ))}
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle1">subtitle1 — The quick brown fox</Typography>
          <Typography variant="subtitle2">subtitle2 — The quick brown fox</Typography>
          <Typography variant="body1">body1 — The quick brown fox jumps over the lazy dog</Typography>
          <Typography variant="body2">body2 — The quick brown fox jumps over the lazy dog</Typography>
          <Typography variant="caption">caption — The quick brown fox</Typography>
          <Typography variant="overline">overline — The quick brown fox</Typography>
        </Stack>
      </AppCard>

      {/* ── Buttons ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Buttons</Typography>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" gutterBottom>Contained</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Button variant="contained" color="primary">Primary</Button>
              <Button variant="contained" color="secondary">Secondary</Button>
              <Button variant="contained" color="error">Error</Button>
              <Button variant="contained" color="success">Success</Button>
              <Button variant="contained" color="warning">Warning</Button>
              <Button variant="contained" color="info">Info</Button>
              <Button variant="contained" disabled>Disabled</Button>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" gutterBottom>Outlined</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Button variant="outlined" color="primary">Primary</Button>
              <Button variant="outlined" color="secondary">Secondary</Button>
              <Button variant="outlined" color="error">Error</Button>
              <Button variant="outlined" disabled>Disabled</Button>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" gutterBottom>Text</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Button variant="text" color="primary">Primary</Button>
              <Button variant="text" color="secondary">Secondary</Button>
              <Button variant="text" color="error">Error</Button>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" gutterBottom>Icon Buttons</Typography>
            <Stack direction="row" spacing={1}>
              <IconButton color="primary"><AddIcon /></IconButton>
              <IconButton color="secondary"><EditIcon /></IconButton>
              <IconButton color="error"><DeleteIcon /></IconButton>
              <IconButton disabled><InfoIcon /></IconButton>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" gutterBottom>Sizes</Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Button variant="contained" size="small">Small</Button>
              <Button variant="contained" size="medium">Medium</Button>
              <Button variant="contained" size="large">Large</Button>
            </Stack>
          </Grid>
        </Grid>
      </AppCard>

      {/* ── Form Controls ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Form Controls</Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField label="Default" fullWidth size="small" />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField label="With value" fullWidth size="small" defaultValue="R$ 1.250,00" />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField label="Error" fullWidth size="small" error helperText="Campo obrigatório" />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField label="Disabled" fullWidth size="small" disabled defaultValue="Read-only" />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body2">Switch</Typography>
              <Switch defaultChecked />
              <Switch />
              <Switch disabled />
            </Stack>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <ToggleButtonGroup
              value={toggle}
              exclusive
              onChange={(_, v) => v && setToggle(v)}
              size="small"
            >
              <ToggleButton value="one">One</ToggleButton>
              <ToggleButton value="two">Two</ToggleButton>
              <ToggleButton value="three">Three</ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>
      </AppCard>

      {/* ── Feedback ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Feedback</Typography>
        <Stack spacing={2}>
          <Alert severity="success">Success — operation completed.</Alert>
          <Alert severity="info">Info — here's something you should know.</Alert>
          <Alert severity="warning">Warning — proceed with caution.</Alert>
          <Alert severity="error">Error — something went wrong.</Alert>
          <LinearProgress />
          <LinearProgress variant="determinate" value={65} />
        </Stack>
      </AppCard>

      {/* ── Chips & Tooltips ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Chips & Tooltips</Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip label="Default" />
          <Chip label="Primary" color="primary" />
          <Chip label="Secondary" color="secondary" />
          <Chip label="Success" color="success" />
          <Chip label="Error" color="error" />
          <Chip label="Deletable" onDelete={() => {}} />
          <Tooltip title="I'm a tooltip!" arrow>
            <Chip label="Hover me" variant="outlined" />
          </Tooltip>
        </Stack>
      </AppCard>

      {/* ── Cards & Paper ── */}
      <AppCard>
        <Typography variant="h6" gutterBottom>Cards & Paper</Typography>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2">Paper (default)</Typography>
              <Typography variant="body2" color="text.secondary">
                Standard paper elevation with theme borders.
              </Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2">Paper (outlined)</Typography>
              <Typography variant="body2" color="text.secondary">
                No elevation, border only.
              </Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <AppCard>
              <Typography variant="subtitle2">AppCard</Typography>
              <Typography variant="body2" color="text.secondary">
                Project's card wrapper component.
              </Typography>
            </AppCard>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" sx={{ mt: 1, mb: 1 }}>Skeleton Loading</Typography>
            <Stack spacing={1}>
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="rectangular" height={40} />
              <Skeleton variant="rounded" height={40} />
            </Stack>
          </Grid>
        </Grid>
      </AppCard>
    </Stack>
  )
}
