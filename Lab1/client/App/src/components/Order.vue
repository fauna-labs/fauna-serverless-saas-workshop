<!--
Copyright Fauna, Inc.
SPDX-License-Identifier: MIT-0
-->
<template>
  <div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">

    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity">      
    </div>

    <div class="fixed inset-0 z-10 flex items-center justify-center px-6 sm:px-6 lg:px-8" 
      @click.self="exit">
      <div class="flex flex-col max-h-full">
        <div class="py-3"></div>
        <div class="max-w-5xl px-2 pb-2 overflow-auto">
          <div class="grid grid-cols-9 gap-6 bg-gray-200 pl-4 pr-3 py-3 rounded-lg shadow-xl">
            <div v-if="updateMode" class="col-span-6 md:col-span-2">
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Update Order</h2>
              <p class="text-gray-400">Update the order details and click Save</p>
            </div>
            <div v-else class="col-span-6 md:col-span-2">
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Create Order</h2>
              <p class="text-gray-400">To create an Order, provide an Order Name, select the products and quantity, and click Save</p>
            </div>

            
            
            <div class="mt-5 col-span-9 md:col-span-7 dark:text-gray-500">   
              
              <form @submit.prevent="addOrUpdateOrder">
                <div class="shadow sm:overflow-hidden sm:rounded-md">

                  <div class="space-y-6 px-4 py-5 sm:p-6 bg-white">
                    <label for="orderName" class="block text-md font-medium text-gray-700">Order Name</label>
                    <div class="mt-2">
                      <input id="orderName" name="orderName" type="text" required
                        class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                        placeholder="name" v-model="orderName">
                    </div>
                  </div>
                  <div class="bg-gray-100">
                    <table class="min-w-full">
                      <thead class="border-b border-gray-400">
                        <tr>
                          <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Product</th>
                          <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Price</th>
                          <th scope="col" class="text-sm font-medium px-6 py-4 text-left">SKU</th>
                          <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Qty</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr><td colspan="4"><ProgressBar v-if="loadingProducts" /></td></tr>
                        <tr class="border-b border-gray-300" v-for="p in products" :key="p.id">                  
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <a href="#" @click="viewProduct(p)">
                              <div class="flex flex-col">
                                <div>{{ p.name }}</div>
                                <div class="text-xs font-light mt-1">{{ p.description }}</div>
                              </div>
                            </a>
                          </td>
                          <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.price }}</td>
                          <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.sku }}</td>
                          <td class="text-sm font-light px-6 py-4 whitespace-nowrap">
                            <div flex="flex flex-col">
                              <a href="#" @click="addOne(p)"><span class="pr-3 pl-5 text-lg">+</span></a>
                              <input class="py-1 w-14 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-center"
                                type="number"
                                v-model="p.requestedQuantity">
                              <a href="#" @click="subtractOne(p)"><span class="pl-3 pr-5 text-lg">-</span></a>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <ProgressBar v-if="progress"/>
                  <div class="bg-gray-50 px-4 py-3 text-right sm:px-6">
                    <div class="flex flex-row justify-end gap-2">
                      <Button label="Cancel" :inactive="progress" class="text-sm" @click="exit"/>                    
                      <Button 
                        label="Save" 
                        :inactive="progress" 
                        class="text-sm"
                        type="submit" 
                        value="submit"
                      />
                    </div>
                  </div>
                </div>
              </form>

            </div>
            
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
input[type=number]{
    -moz-appearance: textfield;
}
</style>

<script>
import ProgressBar from '@/components/ProgressBar.vue';
import Button from '@/components/Button.vue';

export default {
  name: 'order',
  components: {
    ProgressBar,
    Button
  },
  data() {
    return {
      updateMode: false,
      url: null,
      apimethod: null,
      progress: false,
      loadingProducts: false,
      orderName: null,
      products: []
    }
  },
  props: {
    order: Object
  },
  async mounted() {
    if (this.order) {
      this.updateMode = true;      
    } else {
      this.updateMode = false;
    }
    this.loadProducts();
  },
  methods: {
    exit() {
      this.progress = false;
      this.$emit('exit-order');
    },
    addOne(product) {
      if (!product.requestedQuantity) product.requestedQuantity = 0;
      product.requestedQuantity += 1;
    },
    subtractOne(product) {
      if (!product.requestedQuantity) return;

      product.requestedQuantity = product.requestedQuantity > 0 ? product.requestedQuantity - 1 : 0;
    },
    async loadProducts() {
      this.loadingProducts = true;
      try {
        const res = await fetch(
          `${import.meta.env.VITE_APP_APIGATEWAYURL}/products`, {
            method: 'GET'
        });
        this.products = await res.json();
      } catch(e) {
        alert(e);
        this.loadingProducts = false;
      }
      this.loadingProducts = false;
    },
    async addOrUpdateOrder() {
      if (this.progress) {
        return;
      }      
      let orderProducts = [];
      this.products.forEach(p=>{
        if (p.requestedQuantity && p.requestedQuantity > 0) {
          orderProducts.push({
            productId: p.id,
            quantity: p.requestedQuantity,
            price: p.price
          })
        }
      })
      if (orderProducts.length <= 0) {
        alert('Please add some products');
        return;
      }

      this.progress = true;

      let newOrder = {
        orderName: this.orderName,
        orderProducts: orderProducts
      }

      this.url = `${import.meta.env.VITE_APP_APIGATEWAYURL}/order`;
      this.apimethod = 'POST';
      if (this.updateMode) {
        this.url += `/${this.product.id}`;
        this.apimethod = 'PUT';
      }
      try {
        const res = await fetch(
          this.url, {
          method: this.apimethod,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(newOrder)        
        });
        if (!res.ok) {
          alert(await res.text());
          this.progress = false;
          return;
        }
      } catch(e) {
        console.log(e)
      }
      this.exit();
    }
  }
}
</script>