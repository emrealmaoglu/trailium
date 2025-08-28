import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { i18n } from './i18n'
import { useSessionStore } from '@/stores/session'

import './index.css'
import './styles/theme.css'
import { initThemeOnce } from './lib/theme'

const app = createApp(App)
initThemeOnce()
app.use(createPinia())
app.use(i18n)
// Initialize session from storage before mounting
const session = useSessionStore()
await session.initFromStorage()
app.use(router)
app.mount('#app')
