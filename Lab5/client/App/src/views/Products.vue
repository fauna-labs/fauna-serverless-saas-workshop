<template>
  <div class="flex flex-col h-screen overflow-auto pa-0 bg-white dark:bg-gray-800 dark:border-gray-700 text-gray-800 dark:text-white">
    
    <div class="px-4 py-2">
      <h2 class="text-3xl font-semibold">Products</h2>
      <div class="flex flex-row text-sm pt-4">
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
          <Button label="Add Product" :inactive="progress" @click="showAddProduct"/>
        </div>
      </div>
    </div>

    <div class="flex flex-col mt-1">
      
      <div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="py-2 inline-block min-w-full sm:px-6 lg:px-8">
          <div class="overflow-hidden">
            <table class="min-w-full">
              <thead class="border-b dark:border-gray-300">
                <tr>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Name</th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Price</th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">SKU</th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Quantity stock</th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">Backordered Limit</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colspan="5">
                    <ProgressBar v-if="progress" />
                  </td>
                </tr>
                <tr class="border-b dark:border-gray-600" v-for="p in products" :key="p.productId">                  
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
                    <div class="flex flex-col">
                      <div>{{ p.quantity }}</div>
                      <div class="text-xs text-red-500 font-light mt-1" v-if="p.backordered">(Backordered)</div>
                    </div>
                  </td>
                  <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.backorderedLimit }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <Product 
      v-if="addOrUpdateProduct" 
      @exit-add-product="productAdded"
      :product="selectedProduct"/>
  </div>
</template>

<script>
import ProgressBar from '@/components/ProgressBar.vue';
import Product from '@/components/Product.vue';
import Button from '@/components/Button.vue';

export default {
  name: 'products',
  components: {
    ProgressBar,
    Product,
    Button
  },
  data() {
    return {
      addOrUpdateProduct: false,
      products: [],
      progress: false,
      selectedProduct: null
    }
  },
  computed: {
    accessToken() {
      return this.$auth.getAccessToken();
    }
  },
  methods: {
    async listProducts() {
      if (!this.accessToken) {
        return;
      }

      this.progress = true;

      fetch(
        `${this.$store.state.apiGatewayUrl}/products`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
        }
      })
        .then(res => {
          if (!res.ok) {
            console.log('ERR: ', e);
            this.progress = false;
          } else {
            return res.json();
          }
        })
        .then(data => {
          this.products = data;
          this.progress = false;
        })
        .catch(e => {
          console.log('ERR: ', e);
          this.progress = false;
        })

    },
    productAdded() {
      this.addOrUpdateProduct = false;
      this.listProducts();
    },
    showAddProduct() {
      if (this.progress) {
        return;
      }
      this.selectedProduct = null;
      this.addOrUpdateProduct = true;
    },
    viewProduct(product) {
      this.addOrUpdateProduct = true;
      this.selectedProduct = product;
    }
  },
  mounted() {
    this.listProducts();
  },
  watch: {
    accessToken: "listProducts"
  }
}
</script>