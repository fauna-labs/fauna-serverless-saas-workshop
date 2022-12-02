<template>
  <div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"/>

      <div class="fixed inset-0 z-10 overflow-y-auto flex min-h-full items-center justify-center px-6 sm:px-6 lg:px-8" 
        @click.self="exit">
        <div class="max-w-xl">
          <div class="grid grid-cols-4 col-span-3 gap-6 bg-gray-200 pl-4 pr-3 py-3 rounded-lg shadow-xl">
            <div v-if="registrationMode">
              <div class="col-span-3 md:col-span-1">
                <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Register Tenant</h2>
                <p class="text-gray-400">To apply for a new Tenant, fill in the form and click Save</p>
              </div>
            </div>
            <div v-else>
              <div class="col-span-3 md:col-span-1" v-if="updateMode">
                <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Update Tenant</h2>
                <p class="text-gray-400">Update the values and click Save</p>
              </div>
              <div class="col-span-3 md:col-span-1" v-else>
                <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Add Tenant</h2>
                <p class="text-gray-400">To provision a new Tenant, fill in the form and click Save</p>
              </div>
            </div>

            <div class="mt-5 col-span-4 md:col-span-3 dark:text-gray-500">
              <form @submit.prevent="addOrUpdateTenant">
                <div class="shadow sm:rounded-md">
                  <div class="space-y-6 bg-white px-4 py-5 sm:p-6">
                    <div>
                      <label for="tenantName" class="block text-md font-medium text-gray-700">Name</label>
                      <div class="mt-2">
                        <input id="tenantName" name="tenantName" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="name" v-model="tenantName">
                      </div>
                    </div>
                    <div>
                      <label for="tenantEmail" class="block text-md font-medium text-gray-700">Email</label>
                      <div v-if="updateMode" class="mt-2 text-md font-light">
                        {{ tenantEmail }}
                      </div>
                      <div v-else class="mt-2">
                        <input id="tenantEmail" name="tenantEmail" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="Email" v-model="tenantEmail">
                      </div>
                    </div>
                    <div>
                      <label for="tenantAddress" class="block text-md font-medium text-gray-700">Address</label>
                      <div class="mt-2">
                        <input id="tenantAddress" name="tenantAddress" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="Company address" v-model="address">
                      </div>
                    </div>
                    <div>
                      <label for="tenantPhone" class="block text-md font-medium text-gray-700">Phone number</label>
                      <div class="mt-2">
                        <input id="tenantPhone" name="tenantPhone" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="Company phone number" v-model="phoneNumber">
                      </div>
                    </div>

                    <div>
                      <label for="tier" class="block text-md font-medium text-gray-700">Service plan</label>
                      <div v-if="updateMode" class="mt-2 text-md font-light">
                        {{tier}}
                      </div>
                      <div v-else class="mt-2 pb-6">
                        <select v-model="tier" id="tier-select"
                              class="
                                bg-white
                                text-sm font-medium text-gray-700 
                                float-left
                                p-2
                                list-none
                                text-left
                                rounded-md
                                border border-gray-300
                                shadow-sm
                                hover:bg-gray-50
                                focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-100
                              "                     
                          >
                          <option disabled value="">Please select a plan tier</option>
                          <option v-for="t in tiers" v-bind:key="t.value">
                              {{t.value}}
                          </option>
                        </select>
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
  name: 'tenant',
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
      tenantName: null,
      tenantEmail: null,
      address: null,
      phoneNumber: null,
      tier: null,
      tiers: [
        {
          "id": "basic",
          "value": "Basic"
        },
        {
          "id": "standard",
          "value": "Standard"
        },
        {
          "id": "premium",
          "value": "Premium"
        },
        {
          "id": "platinum",
          "value": "Platinum"
        }
      ]      
    }
  },
  props: {
    tenant: Object,
    registrationMode: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    if (this.tenant) {
      this.updateMode = true;
      this.tenantName = this.tenant.tenantName;
      this.tenantEmail = this.tenant.tenantEmail;
      this.address = this.tenant.tenantAddress;
      this.phoneNumber = this.tenant.tenantPhone;
      this.tier = this.tenant.tenantTier;

    } else {
      this.updateMode = false;
    }
  },
  methods: {
    exit() {
      this.progress = false;
      this.$emit('exit-add-tenant');
    },
    async addOrUpdateTenant() {
      if (this.progress) {
        return;
      }
      this.progress = true;

      let headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
      }      
      if (this.updateMode) {
        this.url = `${import.meta.env.VITE_ADMIN_API_GATEWAY_URL}/tenant/${this.tenant.tenantId}`;
        this.apimethod = 'PUT';
        const accessToken = this.$auth.getAccessToken();
        if (!accessToken) {
          return;
        }
        headers['Authorization'] = `Bearer ${accessToken}`
      } else {
        this.url = `${import.meta.env.VITE_ADMIN_API_GATEWAY_URL}/registration`;
        this.apimethod = 'POST';
      }
      const res = await fetch(
        this.url, {
        method: this.apimethod,
        headers: headers,
        body: JSON.stringify({
          tenantName: this.tenantName,
          tenantEmail: this.tenantEmail,
          tenantAddress: this.address,
          tenantPhone: this.phoneNumber,
          tenantTier: this.tier
        })        
      });
      this.progress = false;
      this.$emit('tenant-added');
    }
  }
}
</script>