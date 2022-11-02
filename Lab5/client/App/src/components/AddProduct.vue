<template>
  <div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"/>

      <div class="fixed inset-0 z-10 overflow-y-auto flex min-h-full items-center justify-center px-6 sm:px-6 lg:px-8" 
        @click.self="exit">
        <div class="max-w-xl">
          <div class="grid grid-cols-4 col-span-3 gap-6 bg-gray-200 pl-4 pr-3 py-3 rounded-lg shadow-xl">
            <div class="col-span-3 md:col-span-1">
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Add Product</h2>
              <p class="text-gray-400">To add a new product, fill in the form and click Save</p>
            </div>

            <div class="mt-5 col-span-4 md:col-span-3">
              <form @submit.prevent="addProduct">
                <div class="shadow sm:overflow-hidden sm:rounded-md">
                  <div class="space-y-6 bg-white px-4 py-5 sm:p-6">
                    <div>
                      <label for="productName" class="block text-md font-medium text-gray-700">Name</label>
                      <div class="mt-2">
                        <input id="productName" name="productName" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="name" v-model="productName">
                      </div>
                    </div>
                    <div>
                      <label for="price" class="block text-md font-medium text-gray-700">Price</label>
                      <div class="mt-2">
                        <input id="price" name="price" type="number" min="0.01" step="0.01" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="price" v-model="price">
                      </div>
                    </div>
                    <div>
                      <label for="sku" class="block text-md font-medium text-gray-700">SKU</label>
                      <div class="mt-2">
                        <input id="sku" name="sku" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="sku" v-model="sku">
                      </div>
                    </div>
                    <div>
                      <label for="category" class="block text-md font-medium text-gray-700">Category</label>
                      <div class="mt-2">
                        <input id="category" name="category" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="category" v-model="category">
                      </div>
                    </div>

                  </div>
                  <ProgressBar v-if="progress"/>
                  <div class="bg-gray-50 px-4 py-3 text-right sm:px-6">
                    <Button label="Save" :inactive="progress" class="text-sm"/>
                  </div>
                </div>
              </form>
            </div>
          </div>   
        </div>     
      </div>
    </div>
</template>

<script>
import ProgressBar from '@/components/ProgressBar.vue';
import Button from '@/components/Button.vue';

export default {
  name: 'add-product',
  components: {
    ProgressBar,
    Button
  },
  data() {
    return {
      progress: false,
      productName: null,
      price: null,
      sku: null,
      category: null
    }
  },
  methods: {
    exit() {
      this.progress = false;
      this.$emit('exit-add-product');
    },
    async addProduct() {
      if (this.progress) {
        return;
      }
      const accessToken = this.$auth.getAccessToken();
      if (!accessToken) {
        return;
      }

      this.progress = true;
      const res = await fetch(
        `${import.meta.env.VITE_API_GATEWAY_URL}/product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name: this.productName,
          price: this.price,
          sku: this.sku,
          category: this.category
        })        
      });
      this.exit();
    }
  }
}
</script>