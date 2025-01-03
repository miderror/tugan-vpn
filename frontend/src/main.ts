import './assets/global.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import WebApp from '@twa-dev/sdk';
import 'virtual:svg-icons-register'

WebApp.ready();

const app = createApp(App);
app.use(router);
app.mount('#app');