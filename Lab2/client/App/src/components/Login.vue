<!--
Copyright Fauna, Inc.
SPDX-License-Identifier: MIT-0
-->
<template>
  <div class="flex min-h-full items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
    @click.self="exit"
    >
    <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all p-4">
      <div class="w-full max-w-md space-y-8">
        <div>
          <h2 class="mt-6 text-center text-2xl font-bold tracking-tight text-gray-900">Sign in to your account</h2>
        </div>
        <form class="mt-8 space-y-6" @submit.prevent="login">
          <input type="hidden" name="remember" value="true">
          <div class="-space-y-px rounded-md shadow-sm">

            <div>
              <label for="username" class="sr-only">Username</label>
              <input id="username" name="username" type="text" autocomplete="username" 
                required :disabled="setNewPasswordFlow"
                class="relative block w-full appearance-none rounded-none rounded-t-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                placeholder="username"
                v-model="username">
            </div>
            <div v-if="!setNewPasswordFlow">
              <label for="password" class="sr-only">Password</label>
              <input id="password" name="password" type="password" autocomplete="current-password"
                required :disabled="setNewPasswordFlow"
                class="relative block w-full appearance-none rounded-none rounded-b-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                placeholder="Password"
                v-model="password">
            </div>
          </div>

          <div v-if="setNewPasswordFlow" class="py-1">
            <p class="m-2 text-sm max-w-xs">Password reset required. Please provide a new password below and click Submit.</p>
            <label for="newPassword" class="sr-only">New password</label>
            <input id="newPassword" name="newPassword" type="password" autocomplete="new-password"
              required
              class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              placeholder="New password"
              v-model="newPassword">
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input id="remember-me" name="remember-me" type="checkbox"
                :disabled="setNewPasswordFlow"
                class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
              <label for="remember-me" class="ml-2 block text-sm text-gray-900">Remember me |&nbsp;</label>
            </div>

            <div class="text-sm" @click="tbd">
              <a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">Forgot your password?</a>
            </div>
          </div>

          <div>
            <Button :label='setNewPasswordFlow ? "Submit" : "Sign in"' full :inactive="loggingIn"
              icon="M10 1a4.5 4.5 0 00-4.5 4.5V9H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2v-6a2 2 0 00-2-2h-.5V5.5A4.5 4.5 0 0010 1zm3 8V5.5a3 3 0 10-6 0V9h6z"
            />
          </div>
          <div class="text-sm">
            Don't have an account?&nbsp;<a href="#" @click="signup" class="font-medium text-indigo-600 hover:text-indigo-500">Signup&nbsp;</a>now
          </div>          
        </form>
        <ProgressBar v-if="loggingIn"/>
      </div>      
    </div>
  </div>
</template>


<script>
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import ProgressBar from '@/components/ProgressBar.vue';
import Button from '@/components/Button.vue';


export default {
  name: 'Login',
  components: {
    ProgressBar,
    Button
  },
  data() {
    return {
      username: null,
      password: null,
      newPassword: null,
      loggingIn: false,
      sessionUserAttributes: null,
      cognitoUser: null,
      setNewPasswordFlow: false
    }
  },
  methods: {
    exit() {
      this.$store.commit("hideLogin");
      this.$router.push('/');
    },
    async login() {
      this.loggingIn = true;    

      if (this.setNewPasswordFlow) {
        this.handleNewPassword();
        return;
      }

      let poolData;

      poolData = {
        UserPoolId: import.meta.env.VITE_ADMIN_USERPOOL_ID,
        ClientId: import.meta.env.VITE_ADMIN_APPCLIENTID
      };

      const userPool = new CognitoUserPool(poolData);
      this.cognitoUser = new CognitoUser({ 
        Username: this.username,
        Pool: userPool,
      });
      const authenticationDetails = new AuthenticationDetails({
          Username: this.username,
          Password: this.password,
      });
      this.cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: data => {
          this.$auth.setAccessToken(data.idToken);
          this.$store.commit("hideLogin");
        },

        onFailure: err => {
          console.log('Failed', err);
          alert(err);
        },

        newPasswordRequired: (userAttributes, requiredAttributes) => {   
          delete userAttributes.email_verified;       
          this.sessionUserAttributes = {
            // ...userAttributes
          }
          this.setNewPasswordFlow = true;
        }
      });

      this.loggingIn = false;

    },
    handleNewPassword() {
      this.cognitoUser.completeNewPasswordChallenge(this.newPassword, this.sessionUserAttributes, {
        onSuccess: (result) => {
          this.$auth.setAccessToken(result.idToken);
          this.$store.commit("hideLogin");
          this.setNewPasswordFlow = false;
        },
        onFailure: (err) => {
          alert(err);
          this.setNewPasswordFlow = false;
        }
      });
    },
    tbd() {
      alert('Functionality not implemented yet');
    },
    signup() {
      this.$store.commit('hideLogin');
      this.$router.push('/register');
    }
  }
}
</script>