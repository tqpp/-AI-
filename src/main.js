import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog, Loading } from 'quasar'
import router from './router'
import App from './App.vue'
import VueKonva from 'vue-konva'
import i18n from './i18n'

// Import Quasar css
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/mdi-v6/mdi-v6.css'
import 'quasar/src/css/index.sass'

// Import global styles
import './styles/global.scss'

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(Quasar, {
  plugins: {
    Notify,
    Dialog,
    Loading
  },
  config: {
    dark: true, // Enable dark mode by default for industrial environment
    brand: {
      primary: '#2A5CAA',   // Industrial blue
      secondary: '#4A4E54', // Equipment gray
      accent: '#FF6B35',    // Safety orange
      
      dark: '#1D1D1D',
      'dark-page': '#121212',
      
      positive: '#21BA45',
      negative: '#C10015',
      info: '#31CCEC',
      warning: '#F2C037'
    },
    notify: {
      position: 'top-right',
      timeout: 2500,
      textColor: 'white'
    }
  }
})
app.use(VueKonva)
app.use(i18n)

// Mount app
app.mount('#app')