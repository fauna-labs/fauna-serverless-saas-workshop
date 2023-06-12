// Copyright Fauna, Inc.
// SPDX-License-Identifier: MIT-0

import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Products from '@/views/Products.vue'
import Orders from '@/views/Orders.vue'
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
      path: '/products',
      component: Products,
      name: 'products'
    },
    {
      path: '/orders',
      component: Orders,
      name: 'orders'
    },
    {
      path: '/tenants',
      component: Tenants,
      name: 'tenants'
    }      
  ],
})
