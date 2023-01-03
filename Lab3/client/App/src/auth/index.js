let instance;

const authStateHelper = (app, options) => {
  const store = app.config.globalProperties.$store;

  if (instance) return instance;

  const loginRequired = ()=>{
    if (!store.state.skip) {
      store.commit('showLogin');
    }
    store.commit('skipOne');
    return null;
  }

  const getAccessToken = ()=>{
    const token = store.state.accessToken;

    if (!token) {
      return loginRequired();
    }

    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const exp = decoded.exp;
    const now = Math.floor(Date.now()/1000);
    if (now > exp) {
      return loginRequired();
    }

    return token;
  }

  const setAccessToken = (idToken)=>{
    store.commit('setAccessToken', idToken.jwtToken);
    store.commit('setLoggedInName', idToken.payload.email);
    store.commit('setRole', idToken.payload['custom:userRole']);
    store.commit('setTenantAdminFlag', idToken.payload['custom:userRole'] && idToken.payload['custom:userRole'].toUpperCase() == 'TENANTADMIN');
    store.commit('setSysAdminFlag', idToken.payload['custom:userRole'] && idToken.payload['custom:userRole'].toUpperCase() == 'SYSTEMADMIN');
  }

  instance = {
    getAccessToken: getAccessToken,
    setAccessToken: setAccessToken
  }
  return instance;
};


export default {
  install: (app, options) => {
    app.config.globalProperties.$auth = authStateHelper(app, options);
  }
}