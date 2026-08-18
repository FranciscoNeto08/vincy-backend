const Auth = (function () {

  const SESSION_KEY = "meusite_sessao";

  function getSession() {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY));
    } catch {
      return null;
    }
  }

  function saveSession({ name, email, token }) {
    localStorage.setItem(SESSION_KEY, JSON.stringify({ name, email, token }));
  }

  function getToken() {
    const session = getSession();
    return session ? session.token : null;
  }

  function isLoggedIn() {
    return !!getToken();
  }

  function requireLogin() {
    if (!isLoggedIn()) {
      window.location.href = "index.html";
      throw new Error("Redirecionando para login...");
    }
    return getSession();
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
    window.location.href = "index.html";
  }

  return { getSession, saveSession, getToken, isLoggedIn, requireLogin, logout };

})();