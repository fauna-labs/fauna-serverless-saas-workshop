import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Products from '@/views/Products.vue'
import Orders from '@/views/Orders.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Home,
      name: 'home'
    },
    {
      path: '/products',
      component: Products,
      name: 'products'
    },
    {
      path: '/orders',
      component: Orders,
      name: 'orders'
    },
  ],
})
