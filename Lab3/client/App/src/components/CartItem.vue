<!--
Copyright Fauna, Inc.
SPDX-License-Identifier: MIT-0
-->
<template>
  <li class="flex py-2">
    <div class="flex justify-center">
      <div class="flex relative w-12 h-12 bg-blue-400 justify-center items-center m-1 mr-2 text-xl rounded-lg text-white">
        {{avatarName(product.productName)}}
      </div>
    </div>
    <div class="ml-4 flex flex-1 flex-col">
      <div>
        <div class="flex justify-between text-base font-medium text-gray-900 dark:text-gray-400">
          <div class="flex flex-row gap-4">
            <div class="flex-none w-40">
              <h3>
                <a href="#">{{product.productName}}</a>
              </h3>
            </div>
            <p class="flex mt-1 text-xs text-gray-500">{{product.productDescription}}</p>
          </div>
          <p class="ml-4">${{product.price}}</p>
        </div>
      </div>
      <div class="flex flex-1 items-end justify-between text-sm">
        <p class="text-gray-500">Qty {{product.quantity}}</p>

        <div v-if="!readOnly"
          class="flex">
          <button 
            @click="remove"
            type="button" 
            class="font-medium text-indigo-600 hover:text-indigo-500"
            >Remove</button>
        </div>
      </div>
    </div>
  </li>
</template>

<script>

export default {
  name: 'CartItem',
  components: {},
  props: {
    product: Object,
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    remove() {
      this.$emit("remove-item", this.product.product.id);
    },
    avatarName(name) {
      return name.substring(0,2);
    }
  }
}


</script>