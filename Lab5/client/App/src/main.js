import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import store from './store';
import router from './router';
import auth from './auth';

createApp(App)
.use(router)
.use(store)
.use(auth, { foo: "bar" })
.mount('#app')