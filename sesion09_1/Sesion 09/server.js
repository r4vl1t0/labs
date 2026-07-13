const express = require("express");
const cookieParser = require("cookie-parser");
const crypto = require("crypto");
const path = require("path");
const fs = require("fs");
const ejs = require("ejs");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static(__dirname));

const sessions = new Map();

const flags = {
  A1: "FLAG{lab1_race_condition_cupon_profesor}",
  B1: "FLAG{lab1_race_condition_cupon_alumno}",
  A2: "FLAG{lab2_logica_negocio_email_profesor}",
  B2: "FLAG{lab2_logica_negocio_sms_alumno}",
  A3: "FLAG{lab3_deserializacion_insegura_profesor}",
  B3: "FLAG{lab3_deserializacion_insegura_alumno}",
  A4: "FLAG{lab4_prototype_pollution_profesor}",
  B4: "FLAG{lab4_prototype_pollution_alumno}",
  A5: "FLAG{lab5_lfi_to_rce_profesor}",
  B5: "FLAG{lab5_lfi_to_rce_alumno}",
  A6: "FLAG{lab6_logica_negocio_tres_vulnerabilidades_profesor}",
  B6: "FLAG{lab6_logica_negocio_tres_vulnerabilidades_alumno}",
  F7: "FLAG{lab7_encadenamiento_final_sesion}"
};

const productNames = [
  "Balon oficial", "Casaca local", "Casaca visitante", "Guantes elite", "Chimpunes pro",
  "Mochila tecnica", "Bufanda sede", "Pack stickers", "Entrada tour"
];

function sid(req, res) {
  let id = req.cookies.sid;
  if (!id || !sessions.has(id)) {
    id = crypto.randomBytes(16).toString("hex");
    sessions.set(id, freshSession());
    res.cookie("sid", id, { httpOnly: false, sameSite: "lax" });
  }
  return id;
}

function freshSession() {
  return {
    carts: {},
    messages: {},
    deserialization: {},
    pollution: {},
    lfi: {},
    lab6: {},
    final: {
      user: null,
      products: [
        { id: 1, name: "Kit de bienvenida", description: "Materiales base para operacion de sede.", malicious: false },
        { id: 2, name: "Credencial temporal", description: "Entrega controlada para personal tecnico.", malicious: false }
      ],
      xss: false
    }
  };
}

function state(req, res) {
  return sessions.get(sid(req, res));
}

function labKey(track, lab) {
  return `${track}${lab}`;
}

function products() {
  return productNames.map((name, i) => ({
    id: i + 1,
    name,
    price: 40,
    image: `/assets/product-${(i % 6) + 1}.svg`
  }));
}

function cart(st, key) {
  if (!st.carts[key]) st.carts[key] = { balance: 10, items: [], couponUses: 0, discount: 0 };
  return st.carts[key];
}

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.get("/api/catalog", (_req, res) => {
  res.json({ products: products() });
});

app.get("/api/:track/lab1/state", (req, res) => {
  const st = state(req, res);
  const c = cart(st, labKey(req.params.track, 1));
  res.json({ products: products(), cart: c, total: Math.max(0, c.items.length * 40 - c.discount) });
});

app.post("/api/:track/lab1/cart", (req, res) => {
  const st = state(req, res);
  const c = cart(st, labKey(req.params.track, 1));
  const id = Number(req.body.id);
  if (!products().some((p) => p.id === id)) return res.status(400).json({ error: "producto invalido" });
  c.items.push(id);
  res.json({ ok: true, cart: c });
});

app.post("/api/:track/lab1/coupon", (req, res) => {
  const st = state(req, res);
  const c = cart(st, labKey(req.params.track, 1));
  if (req.body.coupon !== "FIFA2026ABC") return res.status(400).json({ error: "cupon invalido" });
  const observedUses = c.couponUses;
  setTimeout(() => {
    if (observedUses < 1) {
      c.couponUses = observedUses + 1;
      c.discount += 8;
      return res.json({ ok: true, discount: c.discount, note: "cupon aplicado" });
    }
    res.status(409).json({ error: "cupon ya utilizado" });
  }, 180);
});

app.post("/api/:track/lab1/checkout", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 1);
  const c = cart(st, key);
  const total = Math.max(0, c.items.length * 40 - c.discount);
  if (!c.items.length) return res.status(400).json({ error: "carrito vacio" });
  if (total > c.balance) return res.status(402).json({ error: "saldo insuficiente", total, balance: c.balance });
  c.balance -= total;
  c.items = [];
  res.json({ ok: true, total, flag: flags[key] });
});

app.get("/api/:track/lab2/messages", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 2);
  if (!st.messages[key]) st.messages[key] = [];
  res.json({ messages: st.messages[key] });
});

app.post("/api/:track/lab2/send", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 2);
  if (!st.messages[key]) st.messages[key] = [];
  const allowed = ["bienvenida", "factura", "soporte"];
  const unknownBlank = Object.entries(req.body).find(([k, v]) => !["destino", "plantilla", "mensaje", "cantidad"].includes(k) && v === "");
  if (unknownBlank) return res.status(400).json({ error: "falta field mensaje" });
  if (!req.body.destino) return res.status(400).json({ error: "falta field destino" });
  const chosen = req.body.mensaje || req.body.plantilla;
  if (!allowed.includes(chosen) && !req.body.mensaje) return res.status(400).json({ error: "falta field mensaje" });
  const count = Math.min(Number(req.body.cantidad || 1), 25);
  for (let i = 0; i < count; i += 1) {
    st.messages[key].unshift({
      to: req.body.destino,
      type: chosen || "sin_plantilla",
      body: bodyForMessage(req.params.track, chosen),
      at: new Date().toISOString()
    });
  }
  const flag = req.body.mensaje && count >= 6 ? flags[key] : null;
  res.json({ ok: true, sent: count, flag });
});

function bodyForMessage(track, type) {
  const channel = track === "A" ? "correo" : "SMS";
  const templates = {
    bienvenida: `Mensaje de bienvenida por ${channel}.`,
    factura: `Confirmacion de factura por ${channel}.`,
    soporte: `Ticket recibido por ${channel}.`,
    promocion_masiva: `Campana masiva enviada por ${channel}.`,
    alerta_seguridad: `Alerta operativa enviada por ${channel}.`
  };
  return templates[type] || `Plantilla dinamica ${type}`;
}

app.post("/api/:track/lab3/import", (req, res) => {
  const key = labKey(req.params.track, 3);
  try {
    const decoded = Buffer.from(String(req.body.blob || ""), "base64").toString("utf8");
    const payload = JSON.parse(decoded);
    const account = Object.assign({ user: "cliente", role: "customer", credits: 0, workflow: "standard" }, payload);
    const won = account.role === "admin" || account.workflow === "release_flag" || account.credits > 9000;
    res.json({ ok: true, account, flag: won ? flags[key] : null });
  } catch (_err) {
    res.status(400).json({ error: "paquete invalido" });
  }
});

app.post("/api/:track/lab4/preferences", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 4);
  if (!st.pollution[key]) st.pollution[key] = { profile: { theme: "claro", notifications: true } };
  vulnerableMerge(st.pollution[key].profile, req.body || {});
  const probe = {};
  const won = probe.isAdmin === true || probe.canApproveRefunds === true || probe.role === "admin";
  delete Object.prototype.isAdmin;
  delete Object.prototype.canApproveRefunds;
  delete Object.prototype.role;
  res.json({ ok: true, profile: st.pollution[key].profile, adminPanel: won, flag: won ? flags[key] : null });
});

function vulnerableMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === "object") {
      if (!target[key]) target[key] = {};
      vulnerableMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

const labFiles = {
  "pages/home.html": "<h2>Portal de Sede</h2><p>Panel interno de operaciones FIFA 2026.</p>",
  "pages/contact.html": "<h2>Contacto</h2><p>Formulario de soporte para clientes.</p>",
  "logs/access.log": "GET /pages/home.html 200 UA=Mozilla/5.0\nGET /pages/contact.html 200 UA=Mozilla/5.0\n",
  "config/app.ini": "app=portal-sede\nmode=training\nsecret=internal-file-map\n"
};

function logLab5Request(req) {
  const ua = String(req.headers["user-agent"] || "unknown").slice(0, 300);
  const route = String(req.originalUrl || req.url).replace(/\s+/g, "_");
  labFiles["logs/access.log"] += `${new Date().toISOString()} GET ${route} UA=${ua}\n`;
}

function renderLab5Template(content) {
  return ejs.render(content, {
    require,
    process
  });
}

app.get("/api/:track/lab5/file", (req, res) => {
  logLab5Request(req);
  const name = String(req.query.name || "pages/home.html");
  const normalized = path.posix.normalize(name).replace(/^(\.\.\/)+/, "");
  const content = labFiles[name] || labFiles[normalized];
  if (!content) return res.status(404).json({ error: "archivo no encontrado" });
  let rendered = content;
  if (name.includes("logs/") || normalized.includes("logs/")) {
    try {
      rendered = renderLab5Template(rendered);
    } catch (err) {
      rendered = `template render error: ${err.message}`;
    }
  }
  res.json({ file: name, content: rendered });
});

app.post("/api/:track/lab5/ping", (req, res) => {
  logLab5Request(req);
  res.json({ ok: true, logged: true });
});

app.get("/api/:track/lab6/state", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 6);
  if (!st.lab6[key]) st.lab6[key] = { couponUses: 0, voucher: false, xss: false, orders: [] };
  res.json(lab6View(req.params.track, key, st.lab6[key]));
});

app.post("/api/:track/lab6/coupon", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 6);
  if (!st.lab6[key]) st.lab6[key] = { couponUses: 0, voucher: false, xss: false, orders: [] };
  if (req.body.coupon !== "FIFA2026ABC") return res.status(400).json({ error: "cupon invalido" });
  st.lab6[key].couponUses += 1;
  res.json(lab6View(req.params.track, key, st.lab6[key]));
});

app.get("/api/:track/lab6/vouchers/:id", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 6);
  if (!st.lab6[key]) st.lab6[key] = { couponUses: 0, voucher: false, xss: false, orders: [] };
  const vouchers = {
    "7001": { owner: "cliente@fifa2026.com", discount: 5 },
    "7002": { owner: "vip@fifa2026.com", discount: 95, code: "VIP-SEDE-95" },
    "7003": { owner: "logistica@fifa2026.com", discount: 15 }
  };
  const voucher = vouchers[req.params.id];
  if (!voucher) return res.status(404).json({ error: "voucher no existe" });
  if (req.params.id !== "7001") st.lab6[key].voucher = true;
  res.json({ voucher, progress: lab6View(req.params.track, key, st.lab6[key]) });
});

app.post("/api/:track/lab6/pay", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 6);
  if (!st.lab6[key]) st.lab6[key] = { couponUses: 0, voucher: false, xss: false, orders: [] };
  st.lab6[key].orders.push({ card: String(req.body.card || "").slice(-4), at: new Date().toISOString() });
  res.json({ ok: true, message: "orden simulada registrada", progress: lab6View(req.params.track, key, st.lab6[key]) });
});

app.post("/api/:track/lab6/profile", (req, res) => {
  const st = state(req, res);
  const key = labKey(req.params.track, 6);
  if (!st.lab6[key]) st.lab6[key] = { couponUses: 0, voucher: false, xss: false, orders: [] };
  const photo = String(req.body.photo || "");
  if (photo.includes("<") && /onerror|script|svg|iframe/i.test(photo)) st.lab6[key].xss = true;
  res.json(lab6View(req.params.track, key, st.lab6[key]));
});

function lab6View(track, key, s) {
  const done = s.couponUses >= 2 && s.voucher && s.xss;
  return {
    banner: track === "A" ? "Nuestro equipo de Red Team ha identificado las siguientes credenciales cronaldo@fifa2026.com:Portugal2026@" : "",
    couponUses: s.couponUses,
    voucher: s.voucher,
    xss: s.xss,
    flag: done ? flags[key] : null
  };
}

const users = {
  "operario@fifa2026.com": { password: "EnterpriseFIFA2026!", role: "operario" },
  "tecnico@fifa2026.com": { password: "EnterpriseFIFA2026!", role: "tecnico" },
  "inter-operario@fifa2026.com": { password: "InterSede2026!", role: "inter-operario" },
  "administrador@fifa2026.com": { password: "AdminFIFA2026!", role: "administrador" },
  "luis.caval@fifa2026.com": { password: "Caval2026!", role: "auditor" }
};

const projects = Array.from({ length: 16 }, (_, i) => ({
  id: 2000 + i,
  sede: "Sede Pacifico",
  name: `Proyecto operativo ${2000 + i}`,
  status: i % 3 === 0 ? "Revision" : "Activo"
})).concat(Array.from({ length: 16 }, (_, i) => ({
  id: 1000 + i,
  sede: "Sede Atlantico",
  name: `Proyecto reservado ${1000 + i}`,
  status: "Reservado"
})));

app.post("/api/final/login", (req, res) => {
  const st = state(req, res);
  const user = users[String(req.body.email || "").toLowerCase()];
  if (!user || user.password !== req.body.password) return res.status(401).json({ error: "credenciales invalidas" });
  st.final.user = { email: String(req.body.email).toLowerCase(), role: user.role };
  res.json({ ok: true, user: st.final.user });
});

app.get("/api/final/me", (req, res) => {
  const st = state(req, res);
  res.json({ user: st.final.user, xss: st.final.xss, flag: st.final.xss ? flags.F7 : null });
});

app.get("/api/final/projects", (req, res) => {
  const st = state(req, res);
  if (!st.final.user) return res.status(401).json({ error: "no autenticado" });
  res.json({ projects: projects.filter((p) => p.id >= 2000) });
});

app.get("/api/final/projects/:id", (req, res) => {
  const st = state(req, res);
  if (!st.final.user) return res.status(401).json({ error: "no autenticado" });
  const project = projects.find((p) => p.id === Number(req.params.id));
  if (!project) return res.status(404).json({ error: "proyecto no existe" });
  res.json({ project });
});

app.get("/api/final/administradores/listar-usuarios", (req, res) => {
  const st = state(req, res);
  if (!st.final.user) return res.status(401).json({ error: "no autenticado" });
  res.json({
    users: ["inter-operario", "administrador", "luis.caval", "operario", "tecnico"].map((u) => ({
      usuario: u,
      email: `${u}@fifa2026.com`
    }))
  });
});

app.get("/api/final/products", (req, res) => {
  const st = state(req, res);
  if (!st.final.user) return res.status(401).json({ error: "no autenticado" });
  res.json({ products: st.final.products, canAdd: st.final.user.role === "tecnico", flag: st.final.xss ? flags.F7 : null });
});

app.post("/api/final/products", (req, res) => {
  const st = state(req, res);
  if (!st.final.user) return res.status(401).json({ error: "no autenticado" });
  if (st.final.user.role !== "tecnico") return res.status(403).json({ error: "solo tecnico" });
  const description = String(req.body.description || "");
  const product = {
    id: Date.now(),
    name: String(req.body.name || "Producto agregado"),
    description,
    malicious: /<|onerror|script|svg|iframe/i.test(description)
  };
  st.final.products.push(product);
  if (product.malicious) st.final.xss = true;
  res.json({ ok: true, product, flag: st.final.xss ? flags.F7 : null });
});

app.post("/api/final/reset", (req, res) => {
  const st = state(req, res);
  st.final.products = st.final.products.filter((p) => !p.malicious);
  st.final.xss = false;
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`Sesion 09 labs running on http://localhost:${PORT}`);
});
