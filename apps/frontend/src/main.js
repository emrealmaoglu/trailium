import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

import './index.css'
import './styles/theme.css'
import { initThemeOnce } from './lib/theme'

const app = createApp(App)
initThemeOnce()
app.use(createPinia())
app.use(router)
app.mount('#app')
