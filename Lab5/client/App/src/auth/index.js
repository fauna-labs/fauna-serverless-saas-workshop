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
    console.log('getAccessToken');

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