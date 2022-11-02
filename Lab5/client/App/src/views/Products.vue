<template>
  <div class="pa-0 bg-white dark:bg-gray-800 dark:border-gray-700 text-gray-800 dark:text-white">
    <h2 class="pl-4 pb-2 text-3xl font-semibold dark:bg-gray-900">Products</h2>
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
        <Button label="Add Product" :inactive="progress" @click="showAddProduct"/>
      </div>
    </div>
    <div class="flex flex-col mt-1">
      
      <div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="py-2 inline-block min-w-full sm:px-6 lg:px-8">
          <div class="overflow-hidden">
            <table class="min-w-full">
              <thead class="border-b dark:border-gray-300">
                <tr>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">
                    Name
                  </th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">
                    Price
                  </th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">
                    SKU
                  </th>
                  <th scope="col" class="text-sm font-medium px-6 py-4 text-left">
                    Category
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colspan="4">
                    <ProgressBar v-if="progress" />
                  </td>
                </tr>
                <tr class="border-b dark:border-gray-600" v-for="p in products" :key="p.productId">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">{{ p.name }}</td>
                  <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.price }}</td>
                  <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.sku }}</td>
                  <td class="text-sm font-light px-6 py-4 whitespace-nowrap">{{ p.category }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <AddProduct v-if="addProduct" @exit-add-product="productAdded"/>
  </div>
</template>

<script>
import ProgressBar from '@/components/ProgressBar.vue';
import AddProduct from '@/components/AddProduct.vue';
import Button from '@/components/Button.vue';

export default {
  name: 'products',
  components: {
    ProgressBar,
    AddProduct,
    Button
  },
  data() {
    return {
      addProduct: false,
      products: [],
      progress: false
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
        `${import.meta.env.VITE_API_GATEWAY_URL}/products`, {
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
      this.addProduct = false;
      this.listProducts();
    },
    showAddProduct() {
      if (this.progress) {
        return;
      }
      this.addProduct = true;
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