import { createTheme } from '@mui/material/styles'

declare module '@mui/material/styles' {
  interface Palette {
    dark: string
    chart: {
      grid: string
      label: string
      colors: string[]
    }
    golden: string
    sidebar: string
    topbar: {
      background: string
      text: string
      activeText: string
      activeBg: string
    }
  }

  interface PaletteOptions {
    dark?: string
    chart?: {
      grid?: string
      label?: string
      colors?: string[]
    }
    golden?: string
    sidebar?: string
    topbar?: {
      background?: string
      text?: string
      activeText?: string
      activeBg?: string
    }
  }
}

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#303030',
      paper:   '#3e3e3eff', 
    }, 
    text: {
      primary:   '#bebfc2ff',
      secondary: '#B0B4BA',
    },
    dark: '#3b2f2f',
    sidebar: '#3e3e3eff',
    // TOPBAR CONFIG - altere aqui para testar combinações
    topbar: {
      background: '#3e3e3eff',  // cor de fundo do topbar
      text: '#bebfc2ff',        // cor do texto/ícones do topbar
    },
    primary:   { main: '#e1cfcaff' },
    secondary: { main: '#d1705fff' },
    error:    { main: '#ec786bff' },
    success:  { main: '#61a964ff' },
    golden:  '#eeb227ff',
    divider: 'rgba(255,255,255,0.08)',
    chart: {
      grid: '#645959ff',
      label: '#bebfc2ff',
      colors: [
        '#C4956A',
        '#D4A574',
        '#8BAF88',
        '#7FA3BF',
        '#B8926A',
        '#A0A0A0',
        '#CBA882',
        '#B09080',
      ],
    },
  },
  components: {
      MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255,255,255,0.06)',
        },
      },
    },
  }
})
