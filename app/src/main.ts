import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import App from './App.vue'
import router from './router'
import VueApexCharts from "vue3-apexcharts"
import Notifications from '@kyvg/vue3-notification'

// axios.defaults.baseURL = 

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Notifications)
app.component('Icon', FontAwesomeIcon)
app.component('Chart', VueApexCharts)

app.mount('#app')
