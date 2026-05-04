import { createI18n } from 'vue-i18n'
import en from './en'
import zh from './zh'

const saved = localStorage.getItem('locale')
const locale = saved && ['en', 'zh'].includes(saved) ? saved : 'zh'

export const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: 'en',
  messages: { en, zh },
})

export function setLocale(lang: 'en' | 'zh') {
  i18n.global.locale.value = lang
  localStorage.setItem('locale', lang)
}
