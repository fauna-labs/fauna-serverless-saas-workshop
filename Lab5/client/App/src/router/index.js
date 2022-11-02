import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Home,
      name: 'home'
    },
    {
      path: '/about',
      component: () => import('@/views/About.vue'),
      name: 'about'
    },
    {
      path: '/products',
      component: () => import('@/views/Products.vue'),
      name: 'products'
    }
  ],
})
