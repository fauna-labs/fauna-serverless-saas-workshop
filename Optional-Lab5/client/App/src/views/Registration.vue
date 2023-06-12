<template>
  <div class="flex flex-col h-screen overflow-auto pa-0 bg-white dark:bg-gray-800 dark:border-gray-700 text-gray-800 dark:text-white">
    
    <div class="px-4 py-2">
      <h2 class="text-3xl font-semibold">New Tenant Registration</h2>
      <div class="flex flex-row text-sm pt-4">
        <div class="relative grow">

        </div>
      </div>
    </div>

    <Tenant 
      @tenant-added="tenantAdded"
      @exit-add-tenant="canceled"
      registrationMode
      />
  </div>
</template>

<script>
import ProgressBar from '@/components/ProgressBar.vue';
import Tenant from '@/components/Tenant.vue';
import Button from '@/components/Button.vue';

export default {
  name: 'registration',
  components: {
    ProgressBar,
    Tenant,
    Button
  },
  data() {
    return {
      progress: false
    }
  },
  computed: {},
  methods: {
    tenantAdded() {
      this.$store.commit('setAlert', 'Successfully registered tenant. Please check your email for login instructions.');
      this.$router.push("/");
    },
    canceled() {
      this.$router.push("/");
    }
  },
  mounted() {}
}
</script>