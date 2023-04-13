<template>
  <div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"/>

      <div class="fixed inset-0 z-10 overflow-y-auto flex min-h-full items-center justify-center px-6 sm:px-6 lg:px-8" 
        @click.self="exit">
        <div class="max-w-xl">
          <div class="grid grid-cols-4 col-span-3 gap-6 bg-gray-200 pl-4 pr-3 py-3 rounded-lg shadow-xl">
            <div class="col-span-3 md:col-span-1" v-if="updateMode">
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Update Product</h2>
              <p class="text-gray-400">Update the values and click Save</p>
            </div>
            <div class="col-span-3 md:col-span-1" v-else>
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Add Product</h2>
              <p class="text-gray-400">To add a new product, fill in the form and click Save</p>
            </div>

            <div class="mt-5 col-span-4 md:col-span-3 dark:text-gray-500">
              <form @submit.prevent="addOrUpdateProduct">
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
                      <label for="productDesc" class="block text-md font-medium text-gray-700">Description</label>
                      <div class="mt-2">
                        <input id="productDesc" name="productDesc" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="description" v-model="description">
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
                    <div class="flex flex-row gap-2">
                      <div>
                        <label for="quantity" class="block text-md font-medium text-gray-700">Quantity</label>
                        <div class="mt-2">
                          <input id="quantity" name="quantity" type="number" required
                            class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                            placeholder="quantity" v-model="quantity">
                        </div>
                      </div>
                      <div>
                        <label for="backorderedLimit" class="block text-md font-medium text-gray-700">Backordered limit</label>
                        <div class="mt-2">
                          <input id="backorderedLimit" name="backorderedLimit" type="number" required
                            class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                            placeholder="backordered limit" v-model="backorderedLimit">
                        </div>
                      </div>   
                    </div>
                  </div>
                  <ProgressBar v-if="progress"/>
                  <div class="bg-gray-50 px-4 py-3 text-right sm:px-6">
                    <div class="flex flex-row justify-end gap-2">
                      <Button label="Cancel" :inactive="progress" class="text-sm" @click="exit"/>
                      <Button label="Save" :inactive="progress" class="text-sm"/>
                    </div>
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
  name: 'product',
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
      productName: null,
      price: null,
      sku: null,
      description: null,
      quantity: null,
      backorderedLimit: null
    }
  },
  props: {
    product: Object
  },
  mounted() {
    if (this.product) {
      this.updateMode = true;
      this.productName = this.product.name;
      this.price = this.product.price;
      this.sku = this.product.sku;
      this.description = this.product.description;
      this.quantity = this.product.quantity;
      this.backorderedLimit = this.product.backorderedLimit;
    } else {
      this.updateMode = false;
    }
  },
  methods: {
    exit() {
      this.progress = false;
      this.$emit('exit-add-product');
    },
    async addOrUpdateProduct() {
      if (this.progress) {
        return;
      }
      this.progress = true;

      this.url = `${import.meta.env.VITE_APP_APIGATEWAYURL}/product`;
      this.apimethod = 'POST';
      if (this.updateMode) {
        this.url += `/${this.product.id}`;
        this.apimethod = 'PUT';
      }
      const res = await fetch(
        this.url, {
        method: this.apimethod,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          name: this.productName,
          price: this.price,
          sku: this.sku,
          description: this.description,
          quantity: this.quantity,
          backorderedLimit: this.backorderedLimit
        })        
      });
      this.exit();
    }
  }
}
</script>