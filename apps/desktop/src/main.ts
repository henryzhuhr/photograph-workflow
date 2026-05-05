import { createApp } from 'vue'
import DesktopApp from './DesktopApp.vue'
import { i18n } from '@/i18n'

createApp(DesktopApp).use(i18n).mount('#app')
