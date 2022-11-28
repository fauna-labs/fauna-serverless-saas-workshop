import { createStore } from 'vuex';
import VuexPersistence from 'vuex-persist';

const vuexLocal = new VuexPersistence({
  key: 'saas-fauna-workshop',
  storage: window.localStorage
})

export default createStore({
  state: {
    alertMessage: null,
    accessToken: null,
    loggedInName: null,
    apiGatewayUrl: null,
    showLogin: false,
    skip: false,
    sysAdmin: false,
    tenantAdmin: false,
    role: null
  },
  mutations: {
    RESTORE_MUTATION: vuexLocal.RESTORE_MUTATION,
    setAlert(state, message) {
      state.alertMessage = message;
    },
    setAccessToken(state, token) {
      state.accessToken = token;
    },
    setRole(state, value) {
      state.role = value
    },
    setTenantAdminFlag(state, value) {
      state.tenantAdmin = value;
    },
    setSysAdminFlag(state, value) {
      state.sysAdmin = value;
    },
    setLoggedInName(state, name) {
      state.loggedInName = name;
    },
    setApiGatewayUrl(state, url) {
      state.apiGatewayUrl = url;
    },
    logout(state) {
      state.accessToken = null;
      state.loggedInName = null;
    },
    showLogin(state) {
      state.showLogin = true;
    },
    hideLogin(state) {
      state.showLogin = false;
    },
    skipOne(state) {
      state.skip = true;
    },
    resetSkip(state) {
      state.skip = false;
    }
  },
  actions: {},
  modules: {},
  plugins: [vuexLocal.plugin]
})
