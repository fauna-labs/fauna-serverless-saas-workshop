<!--
Copyright Fauna, Inc.
SPDX-License-Identifier: MIT-0
-->
<template>
  <div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"/>

      <div class="fixed inset-0 z-10 overflow-y-auto flex min-h-full items-center justify-center px-6 sm:px-6 lg:px-8" 
        @click.self="exit">
        <div class="max-w-xl">
          <div class="grid grid-cols-4 col-span-3 gap-6 bg-gray-200 pl-4 pr-3 py-3 rounded-lg shadow-xl">
            
            <div class="col-span-3 md:col-span-1" v-if="updateMode">
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Update User</h2>
              <p class="text-gray-400 py-2">Update the values and click Save</p>
            </div>
            <div class="col-span-3 md:col-span-1" v-else>
              <h2 class="mt-6 text-xl font-bold tracking-tight text-gray-800">Add User</h2>
              <p class="text-gray-400 py-2">To add a new user, fill in the form and click Save</p>
            </div>

            <div class="mt-5 col-span-4 md:col-span-3 dark:text-gray-500">
              <form @submit.prevent="addOrUpdateUser">
                <div class="shadow sm:overflow-hidden sm:rounded-md">
                  <div class="space-y-6 bg-white px-4 py-5 sm:p-6">
                    <div>
                      <label for="userName" class="block text-md font-medium text-gray-700">User Name</label>
                      <div v-if="updateMode" class="mt-2 font-light">
                        {{ username }}
                      </div>
                      <div v-else class="mt-2">
                        <input id="userName" name="userName" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="User name" v-model="username">
                      </div>
                    </div>
                    <div>
                      <label for="userEmail" class="block text-md font-medium text-gray-700">Email</label>
                      <div class="mt-2">
                        <input id="userEmail" name="userEmail" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="Email" v-model="email">
                      </div>
                    </div>
                    <div v-if="isSysAdmin">
                      <label for="tenantId" class="block text-md font-medium text-gray-700">Tenant Id</label>
                      <div class="mt-2">
                        <input id="tenantId" name="tenantId" type="text" required
                          class="p-2 w-full rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-md" 
                          placeholder="Tenant Id" v-model="tenantId">
                      </div>
                    </div>
                    <div>
                      <label for="role" class="block text-md font-medium text-gray-700">Role</label>
                      <div class="mt-2 pb-6">
                        <select v-model="role" id="role-select"
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
                              required                 
                          >
                          <option disabled value="">Please select a role</option>
                          <option v-for="r in roles" v-bind:key="r.id">
                              {{r.value}}
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
  name: 'user',
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
      username: null,
      email: null,
      seed: null,
      createdDate: null,
      modifiedDate: null,
      status: null,
      enabled: null,
      role: null,
      tenantId: null,
      roles: [
        {
          "id": "tenantAdmin",
          "value": "TenantAdmin"
        },
        {
          "id": "tenantUser",
          "value": "TenantUser"
        }
      ]        
    }
  },
  props: {
    user: Object
  },
  computed: {
    isSysAdmin() {
      return this.$store.state.sysAdmin;
    }
  },
  mounted() {
    if (this.user) {
      this.seed = this.user.email;

      this.updateMode = true;
      this.username = this.user.user_name;
      this.email = this.user.email;
      this.createdDate = this.user.created_date;
      this.modifiedDate = this.user.modified_data;
      this.status = this.user.status;
      this.enabled = this.user.enabled;
      this.role = this.user.user_role;
    } else {
      this.updateMode = false;
    }
  },
  methods: {
    exit() {
      this.progress = false;
      this.$emit('exit-add-user');
    },
    async addOrUpdateUser() {
      if (this.progress) {
        return;
      }
      const accessToken = this.$auth.getAccessToken();
      if (!accessToken) {
        return;
      }
      this.progress = true;

      let body;
      if (this.updateMode) {
        this.url = `${import.meta.env.VITE_ADMIN_API_GATEWAY_URL}user/${this.user.user_name}`;
        this.apimethod = 'PUT';
        body = {
          userEmail: this.email,
          userRole: this.role
        }
      } else {
        this.url = `${import.meta.env.VITE_ADMIN_API_GATEWAY_URL}user`;
        this.apimethod = 'POST';
        body = {
          userName: this.username,
          userEmail: this.email,
          userRole: this.role,
          tenantId: this.tenantId
        }
      }
      const res = await fetch(
        this.url, {
        method: this.apimethod,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(body)
      });
      this.exit();
    }
  }
}
</script>