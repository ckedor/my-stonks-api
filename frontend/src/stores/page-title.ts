import { create } from 'zustand'

export interface PageTitleState {
  title: string
  setTitle: (title: string) => void
}

export const usePageTitleStore = create<PageTitleState>()((set) => ({
  title: '',
  setTitle: (title) => set({ title }),
}))
