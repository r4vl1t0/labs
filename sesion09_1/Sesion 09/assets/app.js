const root = document.getElementById("app");
const pathParts = location.pathname.split("/").filter(Boolean);
const track = pathParts[0];
const labSlug = pathParts[1] || "";

const finalCreds = {
  leaked: "operario@fifa2026.com : EnterpriseFIFA2026!",
  adminRoute: "/api/final/administradores/listar-usuarios"
};
const lab6StudentCreds = "cronaldo@fifa2026.com:Portugal2026@";
const params = new URLSearchParams(location.search);
const currentView = params.get("view") || "home";

function html(strings, ...values) {
  return strings.map((s, i) => s + (values[i] ?? "")).join("");
}

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw data;
  return data;
}

function setOut(data) {
  const out = document.getElementById("out");
  if (out) out.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  showFlag(data && data.flag);
}

function showFlag(flag) {
  const box = document.getElementById("flag");
  if (box && flag) box.textContent = flag;
}

function viewUrl(view) {
  return `${location.pathname}?view=${view}`;
}

function layout(title, body, links = []) {
  root.innerHTML = html`
    <main class="lab-shell">
      <nav class="appbar">
        <div>
          <p class="eyebrow">${track === "A" ? "Profesor" : track === "B" ? "Alumno" : "Final"}</p>
          <h1>${title}</h1>
        </div>
        <div class="toplinks">
          ${links.map((l) => `<a class="${currentView === l.view ? "active" : ""}" href="${viewUrl(l.view)}">${l.label}</a>`).join("")}
          <a href="/">Indice</a>
        </div>
      </nav>
      ${body}
    </main>
  `;
}

async function lab1() {
  const links = [{ view: "home", label: "Catalogo" }, { view: "cart", label: "Carrito" }];
  if (currentView === "cart") return lab1Cart(links);
  layout("Tienda MatchPoint", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">MatchPoint Store</p>
        <h2>Equipamiento oficial de sede</h2>
        <p>Catalogo de productos para clientes registrados y compras internas de la operacion.</p>
      </div>
    </section>
    <section class="screen-actions">
      <a class="link-button" href="${viewUrl("cart")}">Ver carrito</a>
    </section>
    <section class="cards" id="products"></section>
  `, links);
  const data = await api(`/api/${track}/lab1/state`);
  document.getElementById("products").innerHTML = data.products.map((p) => html`
    <article class="card">
      <img src="${p.image}" alt="">
      <div class="body stack">
        <h3>${p.name}</h3>
        <div class="price">US$ ${p.price}</div>
        <button data-id="${p.id}">Agregar al carrito</button>
      </div>
    </article>`).join("");
  document.querySelectorAll("[data-id]").forEach((btn) => btn.onclick = async () => {
    await api(`/api/${track}/lab1/cart`, { method: "POST", body: { id: btn.dataset.id } });
    location.href = viewUrl("cart");
  });
}

async function lab1Cart(links) {
  layout("Tienda MatchPoint", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Checkout</p>
        <h2>Resumen de compra</h2>
        <p>El sistema calcula promociones antes de confirmar el pago con saldo de usuario.</p>
      </div>
    </section>
    <section class="two">
      <div class="panel stack">
        <h2>Productos seleccionados</h2>
        <div class="checkout-list" id="items"></div>
        <a class="link-button" href="${viewUrl("home")}">Seguir comprando</a>
      </div>
      <aside class="panel stack">
        <h2>Pago</h2>
        <div class="stats" id="cartStats"></div>
        <input id="coupon" value="FIFA2026ABC">
        <button id="apply">Aplicar cupon</button>
        <button class="secondary" id="checkout">Comprar</button>
        <div id="flag" class="notice flag"></div>
        <pre id="out"></pre>
      </aside>
    </section>
  `, links);
  async function refresh() {
    const data = await api(`/api/${track}/lab1/state`);
    const names = new Map(data.products.map((p) => [p.id, p.name]));
    document.getElementById("items").innerHTML = data.cart.items.length
      ? data.cart.items.map((id) => `<div class="checkout-item"><strong>${names.get(id)}</strong><span>US$ 40</span></div>`).join("")
      : "<p>No hay productos en el carrito.</p>";
    document.getElementById("cartStats").innerHTML = html`
      <div class="stat"><span>Saldo</span><strong>US$ ${data.cart.balance}</strong></div>
      <div class="stat"><span>Descuento</span><strong>US$ ${data.cart.discount}</strong></div>
      <div class="stat"><span>Total</span><strong>US$ ${data.total}</strong></div>`;
  }
  document.getElementById("apply").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab1/coupon`, { method: "POST", body: { coupon: document.getElementById("coupon").value } })); }
    catch (e) { setOut(e); }
    refresh();
  };
  document.getElementById("checkout").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab1/checkout`, { method: "POST", body: {} })); }
    catch (e) { setOut(e); }
    refresh();
  };
  refresh();
}

function lab2() {
  const channel = track === "A" ? "Correo electronico" : "SMS";
  const links = [{ view: "home", label: "Redactar" }, { view: "inbox", label: "Bandeja" }];
  if (currentView === "inbox") {
    layout(`Centro de comunicaciones ${channel}`, html`
      <section class="page-cover">
        <div>
          <p class="eyebrow">Comunicaciones</p>
          <h2>Bandeja simulada</h2>
          <p>Registro interno de mensajes enviados por el operador.</p>
        </div>
      </section>
      <section class="panel">
        <h2>Mensajes enviados</h2>
        <div class="messages" id="messages"></div>
      </section>
    `, links);
    loadLab2Messages();
    return;
  }
  layout(`Centro de comunicaciones ${channel}`, html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Comunicaciones</p>
        <h2>Nueva campana transaccional</h2>
        <p>Consola de envio para notificaciones operativas a clientes y personal autorizado.</p>
      </div>
    </section>
    <section class="two">
      <form class="panel stack" id="send">
        <h2>Nueva comunicacion</h2>
        <input name="destino" placeholder="${track === "A" ? "cliente@empresa.com" : "+51900111222"}">
        <select name="plantilla">
          <option value="bienvenida">Bienvenida</option>
          <option value="factura">Factura</option>
          <option value="soporte">Soporte</option>
        </select>
        <input name="cantidad" type="number" min="1" max="25" value="1">
        <button>Enviar</button>
        <div id="flag" class="notice flag"></div>
        <pre id="out"></pre>
      </form>
      <aside class="panel stack">
        <h2>Operacion</h2>
        <p>Los envios quedan registrados en la bandeja de auditoria de la sesion.</p>
        <a class="link-button" href="${viewUrl("inbox")}">Abrir bandeja</a>
      </aside>
    </section>
  `, links);
  document.getElementById("send").onsubmit = async (ev) => {
    ev.preventDefault();
    const body = Object.fromEntries(new FormData(ev.target).entries());
    try { setOut(await api(`/api/${track}/lab2/send`, { method: "POST", body })); }
    catch (e) { setOut(e); }
  };
}

async function loadLab2Messages() {
  const data = await api(`/api/${track}/lab2/messages`);
  document.getElementById("messages").innerHTML = data.messages.length
    ? data.messages.map((m) => html`<div class="message"><strong>${m.to}</strong><br>${m.type}<br>${m.body}</div>`).join("")
    : "<p>No hay mensajes enviados.</p>";
}

function lab3() {
  layout("Portal de importacion de cuentas", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Backoffice</p>
        <h2>Restauracion de cuentas</h2>
        <p>Importador de respaldos para recuperar estados de clientes y flujos de atencion.</p>
      </div>
    </section>
    <section class="two">
      <form class="panel stack" id="import">
        <h2>Restaurar paquete de cuenta</h2>
        <p>El portal restaura respaldos generados por sistemas internos de atencion.</p>
        <textarea name="blob"></textarea>
        <button>Importar</button>
        <div class="row">
          <button type="button" class="secondary" id="sample">Cargar ejemplo</button>
        </div>
        <div id="flag" class="notice flag"></div>
      </form>
      <aside class="panel">
        <h2>Resultado</h2>
        <pre id="out"></pre>
      </aside>
    </section>
  `, [{ view: "home", label: "Importar" }]);
  document.getElementById("sample").onclick = () => {
    document.querySelector("[name=blob]").value = btoa(JSON.stringify({ user: "cliente", role: "customer", credits: 25 }));
  };
  document.getElementById("import").onsubmit = async (ev) => {
    ev.preventDefault();
    try { setOut(await api(`/api/${track}/lab3/import`, { method: "POST", body: Object.fromEntries(new FormData(ev.target).entries()) })); }
    catch (e) { setOut(e); }
  };
}

function lab4() {
  layout("Configuracion de perfil empresarial", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Preferencias</p>
        <h2>Panel de configuracion</h2>
        <p>Configuracion JSON usada por la plataforma para personalizar la sesion del operador.</p>
      </div>
    </section>
    <section class="two">
      <form class="panel stack" id="prefs">
        <h2>Preferencias JSON</h2>
        <textarea name="json">{ "theme": "claro", "notifications": true }</textarea>
        <button>Guardar preferencias</button>
        <div id="flag" class="notice flag"></div>
      </form>
      <aside class="panel">
        <h2>Respuesta del servidor</h2>
        <pre id="out"></pre>
      </aside>
    </section>
  `, [{ view: "home", label: "Perfil" }]);
  document.getElementById("prefs").onsubmit = async (ev) => {
    ev.preventDefault();
    try {
      const body = JSON.parse(new FormData(ev.target).get("json"));
      setOut(await api(`/api/${track}/lab4/preferences`, { method: "POST", body }));
    } catch (e) { setOut(e); }
  };
}

function lab5() {
  const links = [{ view: "home", label: "Documentos" }, { view: "support", label: "Soporte" }];
  if (currentView === "support") {
    layout("Visor documental de soporte", html`
      <section class="page-cover">
        <div>
          <p class="eyebrow">Mesa de ayuda</p>
          <h2>Centro de soporte</h2>
          <p>Portal operativo que registra las visitas de agentes y herramientas internas.</p>
        </div>
      </section>
      <section class="two">
        <div class="panel stack">
          <h2>Estado de servicio</h2>
          <p>Las solicitudes a esta consola quedan en el log de acceso de la aplicacion.</p>
          <button id="ping">Verificar disponibilidad</button>
          <a class="link-button" href="${viewUrl("home")}">Volver a documentos</a>
        </div>
        <aside class="panel">
          <h2>Respuesta</h2>
          <pre id="out"></pre>
        </aside>
      </section>
    `, links);
    document.getElementById("ping").onclick = async () => {
      try { setOut(await api(`/api/${track}/lab5/ping`, { method: "POST", body: {} })); }
      catch (e) { setOut(e); }
    };
    return;
  }
  layout("Visor documental de soporte", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Documentacion</p>
        <h2>Biblioteca de soporte</h2>
        <p>Consulta de archivos publicados para operadores de la mesa de ayuda.</p>
      </div>
    </section>
    <section class="two">
      <div class="panel stack">
        <h2>Documentos publicados</h2>
        <input id="file" value="pages/home.html">
        <button id="read">Abrir archivo</button>
        <a class="link-button" href="${viewUrl("support")}">Abrir soporte</a>
        <div id="flag" class="notice flag"></div>
      </div>
      <aside class="panel">
        <h2>Vista previa</h2>
        <pre id="out"></pre>
      </aside>
    </section>
  `, links);
  document.getElementById("read").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab5/file?name=${encodeURIComponent(document.getElementById("file").value)}`)); }
    catch (e) { setOut(e); }
  };
}

function lab6() {
  const links = [{ view: "home", label: "Tienda" }, { view: "checkout", label: "Checkout" }, { view: "profile", label: "Perfil" }];
  if (currentView === "checkout") return lab6Checkout(links);
  if (currentView === "profile") return lab6Profile(links);
  layout("FIFA Commerce", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Commerce</p>
        <h2>Catalogo de tienda</h2>
        <p>Portal de compras con cupones, vouchers y ordenes simuladas para clientes de sede.</p>
      </div>
    </section>
    <section class="panel stack">
      <div id="banner" class="notice"></div>
      <div class="screen-actions">
        <a class="link-button" href="${viewUrl("checkout")}">Ir a checkout</a>
        <a class="link-button" href="${viewUrl("profile")}">Editar perfil</a>
      </div>
      <div class="cards" id="products"></div>
    </section>
  `, links);
  api("/api/catalog").then((data) => {
    document.getElementById("products").innerHTML = data.products.slice(0, 6).map((p) => html`
      <article class="card"><img src="${p.image}" alt=""><div class="body stack"><h3>${p.name}</h3><div class="price">US$ ${p.price}</div><button>Agregar</button></div></article>`).join("");
  });
  api(`/api/${track}/lab6/state`).then((s) => {
    document.getElementById("banner").style.display = s.banner ? "block" : "none";
    document.getElementById("banner").textContent = s.banner;
  });
}

function lab6Checkout(links) {
  layout("FIFA Commerce", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Checkout</p>
        <h2>Pago y beneficios</h2>
        <p>Validacion de cupones, vouchers y tarjeta para completar una compra simulada.</p>
      </div>
    </section>
    <section class="two">
      <div class="panel stack">
        <h2>Beneficios</h2>
        <input id="coupon" value="FIFA2026ABC">
        <button id="couponBtn">Aplicar cupon</button>
        <input id="voucher" value="7001">
        <button id="voucherBtn" class="secondary">Consultar voucher</button>
      </div>
      <aside class="panel stack">
        <h2>Tarjeta</h2>
        <input id="card" placeholder="4111 1111 1111 1111">
        <button id="pay">Pagar</button>
        <div id="flag" class="notice flag"></div>
        <pre id="out"></pre>
      </aside>
    </section>
  `, links);
  async function refresh() {
    const s = await api(`/api/${track}/lab6/state`);
    setOut(s);
  }
  document.getElementById("couponBtn").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab6/coupon`, { method: "POST", body: { coupon: document.getElementById("coupon").value } })); }
    catch (e) { setOut(e); }
  };
  document.getElementById("voucherBtn").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab6/vouchers/${document.getElementById("voucher").value}`)); }
    catch (e) { setOut(e); }
  };
  document.getElementById("pay").onclick = async () => {
    try { setOut(await api(`/api/${track}/lab6/pay`, { method: "POST", body: { card: document.getElementById("card").value } })); }
    catch (e) { setOut(e); }
  };
  refresh();
}

function lab6Profile(links) {
  layout("FIFA Commerce", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Cuenta</p>
        <h2>Perfil de cliente</h2>
        <p>Administracion de datos publicos del comprador dentro del portal.</p>
      </div>
    </section>
    <section class="two">
      <div class="panel stack">
        <h2>Foto de perfil</h2>
        <input id="photo" placeholder="URL de foto de perfil">
        <button id="savePhoto">Guardar foto</button>
        <div class="profile-preview" id="preview"></div>
      </div>
      <aside class="panel">
        <h2>Respuesta</h2>
        <div id="flag" class="notice flag"></div>
        <pre id="out"></pre>
      </aside>
    </section>
  `, links);
  document.getElementById("savePhoto").onclick = async () => {
    const photo = document.getElementById("photo").value;
    document.getElementById("preview").innerHTML = photo;
    try { setOut(await api(`/api/${track}/lab6/profile`, { method: "POST", body: { photo } })); }
    catch (e) { setOut(e); }
  };
}

function finalLab() {
  const links = [{ view: "home", label: "Acceso" }, { view: "projects", label: "Proyectos" }, { view: "users", label: "Usuarios" }, { view: "products", label: "Productos" }];
  layout("Panel de autenticacion FIFA Enterprise", html`
    <section class="page-cover">
      <div>
        <p class="eyebrow">Enterprise</p>
        <h2>Consola de sede</h2>
        <p>Portal operativo para personal interno y gestion de proyectos asignados.</p>
      </div>
    </section>
    <section class="two">
      <div class="stack">
        <form class="panel stack" id="login">
          <h2>Acceso de personal</h2>
          <input name="email" placeholder="correo">
          <input name="password" type="password" placeholder="contrasena">
          <button>Ingresar</button>
        </form>
        <div class="panel stack" id="dashboard"></div>
      </div>
      <aside class="panel stack">
        <h2>Respuesta</h2>
        <div id="flag" class="notice flag"></div>
        <pre id="out"></pre>
      </aside>
    </section>
  `, links);
  document.getElementById("login").onsubmit = async (ev) => {
    ev.preventDefault();
    try { setOut(await api("/api/final/login", { method: "POST", body: Object.fromEntries(new FormData(ev.target).entries()) })); }
    catch (e) { setOut(e); }
    drawFinal();
  };
  drawFinal();
}

async function drawFinal() {
  const dash = document.getElementById("dashboard");
  const me = await api("/api/final/me");
  if (!me.user) {
    dash.innerHTML = "<h2>Proyectos</h2><p>Autenticacion requerida.</p>";
    return;
  }
  const products = await api("/api/final/products");
  showFlag(products.flag || me.flag);
  if (currentView === "projects") {
    dash.innerHTML = html`<h2>Proyectos</h2><div id="plist"></div>`;
    try {
      const data = await api("/api/final/projects");
      setOut(data);
      dash.querySelector("#plist").innerHTML = data.projects.map((p) => html`<div class="project"><span>${p.id} ${p.name}</span><strong>${p.status}</strong></div>`).join("");
    } catch (e) { setOut(e); }
    return;
  }
  if (currentView === "users") {
    dash.innerHTML = html`<h2>Usuarios</h2><div id="plist"></div>`;
    try { setOut(await api("/api/final/administradores/listar-usuarios")); }
    catch (e) { setOut(e); }
    return;
  }
  if (currentView === "products") {
    dash.innerHTML = html`
      <h2>Productos</h2>
      ${products.canAdd ? html`
        <input id="pname" placeholder="Nombre">
        <textarea id="pdesc" placeholder="Descripcion"></textarea>
        <button id="addProduct">Agregar producto</button>
        <button id="reset" class="danger">Resetear laboratorio</button>` : ""}
      <div id="plist">${products.products.map((p) => `<div class="message"><strong>${p.name}</strong><br>${p.description}</div>`).join("")}</div>
    `;
  } else {
    dash.innerHTML = html`
      <h2>Proyectos</h2>
      <p>Sesion activa: ${me.user.email}</p>
      <div class="screen-actions">
        <a class="link-button" href="${viewUrl("projects")}">Abrir proyectos</a>
        <a class="link-button" href="${viewUrl("users")}">Listar usuarios</a>
        <a class="link-button" href="${viewUrl("products")}">Gestionar productos</a>
      </div>
    `;
  }
  const add = document.getElementById("addProduct");
  if (add) add.onclick = async () => {
    try {
      setOut(await api("/api/final/products", { method: "POST", body: { name: document.getElementById("pname").value, description: document.getElementById("pdesc").value } }));
      drawFinal();
    } catch (e) { setOut(e); }
  };
  const reset = document.getElementById("reset");
  if (reset) reset.onclick = async () => {
    try { setOut(await api("/api/final/reset", { method: "POST", body: {} })); drawFinal(); }
    catch (e) { setOut(e); }
  };
}

if (location.pathname.includes("lab7-final")) finalLab();
else if (labSlug.includes("lab1")) lab1();
else if (labSlug.includes("lab2")) lab2();
else if (labSlug.includes("lab3")) lab3();
else if (labSlug.includes("lab4")) lab4();
else if (labSlug.includes("lab5")) lab5();
else if (labSlug.includes("lab6")) lab6();
