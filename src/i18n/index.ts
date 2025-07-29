import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import en from './locales/en'
import fr from './locales/fr'
import es from './locales/es'
import ar from './locales/ar'
import ary from './locales/ary'

const i18n = createI18n({
  legacy: false, // Set to false to use Composition API
  locale: localStorage.getItem('language') || 'en', // Default to 'en' if no value in localStorage
  fallbackLocale: 'en', // Fallback language
  messages: {
    'zh-CN': zhCN,
    'en': en,
    'fr': fr,
    'es': es,
    'ar': ar,
    'ary': ary
  }
})

export default i18n
