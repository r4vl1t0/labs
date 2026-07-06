function setStatus(id, message, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `status ${type || ""}`.trim();
  el.textContent = typeof message === "string" ? message : JSON.stringify(message, null, 2);
}

function saveToken(key, token) {
  localStorage.setItem(key, token);
}

function getToken(key) {
  return localStorage.getItem(key) || "";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { message: text };
  }
  if (!response.ok) {
    const error = new Error(data.message || "Error de la aplicacion");
    error.data = data;
    error.status = response.status;
    throw error;
  }
  return data;
}

function bindJwtLab(config) {
  const tokenKey = `token:${config.prefix}`;
  const loginForm = document.getElementById("login-form");
  const tokenBox = document.getElementById("token-box");
  const refreshToken = () => {
    tokenBox.textContent = getToken(tokenKey) || "Sin sesion.";
  };

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const body = Object.fromEntries(new FormData(loginForm));
    try {
      const data = await api(`/api/${config.prefix}/login`, {
        method: "POST",
        body: JSON.stringify(body)
      });
      saveToken(tokenKey, data.token);
      refreshToken();
      setStatus("main-status", `Bienvenido ${data.user.username}. Rol actual: ${data.user.role}`, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("profile-btn").addEventListener("click", async () => {
    try {
      const data = await api(`/api/${config.prefix}/profile`, {
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` }
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("report-btn").addEventListener("click", async () => {
    try {
      const data = await api(`/api/${config.prefix}/admin/report`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` },
        body: JSON.stringify({ action: "download" })
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("clear-btn").addEventListener("click", () => {
    localStorage.removeItem(tokenKey);
    refreshToken();
    setStatus("main-status", "Sesion local eliminada.");
  });

  refreshToken();
}

function bindResetLab() {
  const tokenKey = "token:lab3";
  const loginForm = document.getElementById("login-form");
  const forgotForm = document.getElementById("forgot-form");
  const resetForm = document.getElementById("reset-form");
  const tokenBox = document.getElementById("token-box");
  const refreshToken = () => {
    tokenBox.textContent = getToken(tokenKey) || "Sin sesion.";
  };

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/lab3/login", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(loginForm)))
      });
      saveToken(tokenKey, data.token);
      refreshToken();
      setStatus("main-status", `Sesion iniciada como ${data.user.username}`, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  forgotForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/lab3/forgot", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(forgotForm)))
      });
      setStatus("reset-status", data, "ok");
    } catch (error) {
      setStatus("reset-status", error.data || error.message, "err");
    }
  });

  resetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/lab3/reset", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(resetForm)))
      });
      setStatus("reset-status", data, "ok");
    } catch (error) {
      setStatus("reset-status", error.data || error.message, "err");
    }
  });

  document.getElementById("admin-btn").addEventListener("click", async () => {
    try {
      const data = await api("/api/lab3/admin", {
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` }
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  refreshToken();
}

function bindSessionLab() {
  const loginForm = document.getElementById("login-form");

  async function loadSession() {
    try {
      const data = await api(`/api/lab4/session${window.location.search}`);
      setStatus("session-status", data, "ok");
    } catch (error) {
      setStatus("session-status", error.data || error.message, "err");
    }
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/lab4/login", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(loginForm)))
      });
      setStatus("main-status", data, "ok");
      loadSession();
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("account-btn").addEventListener("click", async () => {
    try {
      const data = await api("/api/lab4/account");
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("session-btn").addEventListener("click", loadSession);
  loadSession();
}

function bindFinalLab() {
  const tokenKey = "token:final";
  const loginForm = document.getElementById("login-form");
  const forgotForm = document.getElementById("forgot-form");
  const resetForm = document.getElementById("reset-form");
  const commandForm = document.getElementById("command-form");
  const tokenBox = document.getElementById("token-box");
  const refreshToken = () => {
    tokenBox.textContent = getToken(tokenKey) || "Sin sesion.";
  };

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/final/login", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(loginForm)))
      });
      saveToken(tokenKey, data.token);
      refreshToken();
      setStatus("main-status", `Sesion iniciada como ${data.user.username}. Rol: ${data.user.role}`, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  forgotForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/final/forgot", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(forgotForm)))
      });
      setStatus("reset-status", data, "ok");
    } catch (error) {
      setStatus("reset-status", error.data || error.message, "err");
    }
  });

  resetForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/final/reset", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(new FormData(resetForm)))
      });
      setStatus("reset-status", data, "ok");
    } catch (error) {
      setStatus("reset-status", error.data || error.message, "err");
    }
  });

  document.getElementById("messages-btn").addEventListener("click", async () => {
    try {
      const data = await api("/api/final/messages", {
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` }
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("posts-btn").addEventListener("click", async () => {
    try {
      const data = await api("/api/final/posts", {
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` }
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  commandForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = await api("/api/final/command", {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken(tokenKey)}` },
        body: JSON.stringify(Object.fromEntries(new FormData(commandForm)))
      });
      setStatus("main-status", data, "ok");
    } catch (error) {
      setStatus("main-status", error.data || error.message, "err");
    }
  });

  document.getElementById("clear-btn").addEventListener("click", () => {
    localStorage.removeItem(tokenKey);
    refreshToken();
    setStatus("main-status", "Sesion local eliminada.");
  });

  refreshToken();
}
