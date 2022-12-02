import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Tenants from '@/views/Tenants.vue'
import Users from '@/views/Users.vue'
import Registration from '@/views/Registration.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Home,
      name: 'home'
    },
    {
      path: '/register',
      component: Registration,
      name: 'registration'
    },
    {
      path: '/users',
      component: Users,
      name: 'users'
    },
    {
      path: '/tenants',
      component: Tenants,
      name: 'tenants'
    }      
  ],
})
