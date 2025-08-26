import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './styles/theme.css'
import './index.css' // tailwind entry: @tailwind base; components; utilities

createApp(App).use(router).mount('#app')
