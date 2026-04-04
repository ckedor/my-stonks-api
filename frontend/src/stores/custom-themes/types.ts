import type { ThemePaletteConfig } from '@/theme/themes'

export interface CustomThemeEntry {
  id: string
  name: string
  description: string
  config: ThemePaletteConfig
  createdAt: number
  updatedAt: number
}
