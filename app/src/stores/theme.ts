import { defineStore } from 'pinia'
import { useLocalStorage } from '@vueuse/core'
import type { Ref } from 'vue'

type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  const theme: Ref<Theme> = useLocalStorage<Theme>('theme', 'dark')

  const sync_theme = (): void => {
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  const set_theme = (value: Theme): void => {
    theme.value = value
    sync_theme()
  }

  return { theme, set_theme, sync_theme }
})
