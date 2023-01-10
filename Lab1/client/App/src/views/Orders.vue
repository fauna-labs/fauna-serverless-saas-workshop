<template>
  <div class="flex flex-col h-screen overflow-auto pa-0 bg-white dark:bg-gray-800 dark:border-gray-700 text-gray-800 dark:text-white">
    <div class="max-w-4xl">

      <div class="px-4 py-2">
        <h2 class="text-3xl font-semibold">Order History</h2>
        <p class="my-4 max-w-2xl text-md text-gray-500">
            Check the status of recent orders, manage returns, and discover similar products.</p>

        <div class="flex flex-row text-sm">
          <div class="relative grow">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3">
              <svg class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none">
                <path
                  d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
              </svg>
            </span>

            <input type="text"
              class="w-full py-2 pl-10 pr-4 text-gray-700 bg-white border rounded-md dark:bg-gray-900 dark:text-gray-300 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-300 focus:ring-blue-300 focus:ring-opacity-40 focus:outline-none focus:ring"
              placeholder="Search" />
          </div>
          <div class="relative ml-2">
            <Button label="Create Order" :inactive="progress" @click="showAddOrder"/>
          </div>
        </div>
        <ProgressBar v-if="progress" class="pt-4"/>
      </div>
      <div class="">
        <div v-for="order in orders" :key="order.orderId" class="text-left p-4">
          <div class="px-6 py-4 border rounded-md">
            <div class="grid grid-cols-12 gap-4">
              <div class="col-span-4 mb-6 flex flex-col">
                <div class="flex flex-row items-center">
                  <h1 class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-400">Order</h1>
                  <p class="pl-2 text-sm justify-cente">{{order.orderId}}</p>
                </div>
                <p class="text-sm font-light">{{ order.orderName }}</p>
                <div class="flex flex-row text-md">
                  <p class="font-medium">Placed: </p>
                  <p class="ml-2">{{order.orderPlaced}}</p>
                </div>
                
              </div>
              <div class="col-span-2 flex flex-col">
                <p class="text-lg font-medium">Total</p>
                <p>${{ order.total }}</p>
              </div>
              <div class="col-span-2 flex flex-col">
                <p class="font-medium">Status</p>
                <p class="">{{ order.orderStatus }}</p>
              </div>
              <div class="col-span-2">
                <button @click="tbd"
                  class="px-4 py-2 border rounded-md text-sm font-medium shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  View Order</button>
              </div>
              <div class="col-span-2">
                <button @click="tbd"
                  class="px-4 py-2 border rounded-md text-sm font-medium shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  View Invoice</button>
              </div>
            </div>
            <div class="flow-root">
              <CartItem v-for="product in order.orderProducts" :key="product.product" :product="product" readOnly />
            </div>
          </div>
        </div>
      </div>
    </div>  
    <Order 
      v-if="addOrUpdateOrder" 
      @exit-order="orderAdded"
      :order="selectedOrder"/>    
  </div>
</template>

<script>
import CartItem from '../components/CartItem.vue';
import ProgressBar from '@/components/ProgressBar.vue';
import Button from '@/components/Button.vue';
import Order from '@/components/Order.vue';

export default {
  name: 'orders',
  components: {
    CartItem,
    ProgressBar,
    Button,
    Order
  },
  data() {
    return {
      orders: [],
      progress: false,
      selectedOrder: null,
      addOrUpdateOrder: false
    }
  },
  mounted() {
    this.loadMyOrders();
  },
  methods: {
    async loadMyOrders() {
      this.progress = true;

      fetch(
        `${import.meta.env.VITE_APP_APIGATEWAYURL}/orders`, {
        method: 'GET',
      })
        .then(res => {
          if (!res.ok) {
            this.progress = false;
          } else {
            return res.json();
          }
        })
        .then(data => {
          data = data.map(x => {
            const cart = x.orderProducts;
            let total = 0;
            for (const p of cart) {
              total += p.price * p.quantity;
            }
            x.total = total.toFixed(2);

            if (x.orderCreated) {
              x.orderPlaced = new Date(x.orderCreated).toLocaleDateString('en-us', { weekday:"long", year:"numeric", month:"short", day:"numeric"});
            }
            return x;
          });

          // sort descending
          data.sort((a, b)=>{ return (b.orderId > a.orderId) ? 1 : -1 });

          this.orders = data;

          this.progress = false;
        })
        .catch(e => {
          console.log('ERR: ', e);
          this.progress = false;
        })
    },
    tbd() {
      alert('nothing to see yet');
    },
    orderAdded() {
      this.addOrUpdateOrder = false;
      this.loadMyOrders();
    },
    showAddOrder() {
      if (this.progress) {
        return;
      }
      this.selectedOrder = null;
      this.addOrUpdateOrder = true;
    },
    viewOrder(order) {
      this.addOrUpdateOrder = true;
      this.selectedOrder = order;
    }

  }
}
</script>


