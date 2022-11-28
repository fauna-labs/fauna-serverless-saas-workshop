<template>
  <div class="">

    <div class="grid grid-cols-1 gap-0 py-6" v-if="message">
      <div
        class="flex h-20 items-center justify-end bg-green-600 px-4 text-sm font-medium text-white sm:px-6 lg:px-8">
        <p class="grow w-full">{{ message }}
          <!-- <button class="pl-1 underline">View orders</button> -->
        </p>
        <div class="flex-none w-9">
          <button @click="hideBanner"
            type="button" class="rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white">
            <span class="sr-only">Close message</span>
            <!-- Heroicon name: outline/x-mark -->
            <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div> 
    <div v-else>
      <h2 class="text-2xl font-bold text-pink-500 underline">Home</h2>
    </div>

  </div>
</template>


<script>
export default {
  name: 'Home',
  data() {
    return {
      message: false
    }    
  },
  computed: {
    isAdminApp() {
      return this.$store.state.isAdminApp
    }
  },
  methods: {
    hideBanner() {
      this.message = false;
      this.$store.commit('setAlert', null);
    }
  },
  mounted() {
    this.message = this.$store.state.alertMessage;
  }
}
</script>