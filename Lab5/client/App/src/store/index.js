import { createStore } from 'vuex';
import VuexPersistence from 'vuex-persist';

const vuexLocal = new VuexPersistence({
  key: 'saas-fauna-workshop',
  storage: window.localStorage
})

export default createStore({
  state: {
    accessToken: null,
    loggedInName: null,
    apiGatewayUrl: null,
    showLogin: false,
    skip: false,
  },
  mutations: {
    RESTORE_MUTATION: vuexLocal.RESTORE_MUTATION,
    setAccessToken(state, token) {
      state.accessToken = token;
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
