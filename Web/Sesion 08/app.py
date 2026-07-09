import json
import os
import re
import shlex
import subprocess
import tempfile
import threading
from copy import deepcopy
from urllib.parse import urlparse

import requests
from flask import Flask, Response, jsonify, redirect, render_template_string, request, session, url_for
from graphql import build_schema, graphql_sync
from werkzeug.serving import make_server


PUBLIC_PORT = int(os.environ.get("PUBLIC_PORT", "8080"))
INTERNAL_PORT = 5002
TMP_DIR = os.environ.get("LAB_TMP_DIR", "/tmp" if os.name != "nt" else tempfile.gettempdir())
SOURCE_FILE = os.path.join(TMP_DIR, "fifa-source.txt")
ADMIN_FLAG_FILE = os.path.join(TMP_DIR, "flag-admin.txt")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-for-local-lab")
internal_app = Flask("internal_service")


FLAGS = {
    "lab1A": "FLAG{lab1_profesor_ssrf_internal_index}",
    "lab1B": "FLAG{lab1_alumno_ssrf_metadata_cloud}",
    "lab2A": "FLAG{lab2_profesor_ssrf_ciego_webhook}",
    "lab2B": "FLAG{lab2_alumno_ssrf_ciego_callback}",
    "lab3A": "FLAG{lab3_profesor_bola_delete_object}",
    "lab3B": "FLAG{lab3_alumno_bola_object_abuse}",
    "lab4A": "FLAG{lab4_profesor_bfla_privilege_upgrade}",
    "lab4B": "FLAG{lab4_alumno_bfla_hidden_admin}",
    "lab5A": "FLAG{lab5_profesor_graphql_admin_query}",
    "lab5B": "FLAG{lab5_alumno_graphql_admin_leak}",
    "lab6_lmessi": "FLAG{lab6_idor_sigue_investigando_la_aplicacion}",
    "lab6_cmd": "FLAG{lab6_command_injection_admin_backup}",
}

META_DATA = """instance-id: i-0fifa2026demo
local-ipv4: 10.20.30.45
hostname: app-runner-internal
role: fifa-admin-backup
AccessKeyId: AKIADEMO2026
SecretAccessKey: ssrf-lab-demo-secret
Token: session-token-demo
Internal note: admin portal user lyamal@fifa2026.com / España2026@"""


BASE_CSS = """
<style>
  :root { color-scheme: light; --bg:#f4f6f8; --ink:#17202a; --muted:#667085; --line:#d8dee6; --brand:#006b5f; --danger:#b42318; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: Inter, Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--ink); }
  header { background:#101828; color:white; padding:18px 28px; display:flex; align-items:center; justify-content:space-between; gap:16px; }
  header a { color:white; text-decoration:none; font-weight:700; }
  nav { display:flex; gap:10px; flex-wrap:wrap; }
  nav a { color:#d0d5dd; font-size:14px; font-weight:600; }
  main { width:min(1160px, calc(100% - 32px)); margin:24px auto 48px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
  .card { background:white; border:1px solid var(--line); border-radius:8px; padding:18px; box-shadow:0 1px 2px rgba(16,24,40,.04); }
  .band { background:white; border-block:1px solid var(--line); padding:18px; margin:14px 0; }
  h1 { margin:0 0 8px; font-size:30px; letter-spacing:0; }
  h2 { margin:0 0 12px; font-size:20px; letter-spacing:0; }
  h3 { margin:0 0 8px; font-size:16px; letter-spacing:0; }
  p { color:var(--muted); line-height:1.5; }
  a.button, button { border:0; border-radius:6px; background:var(--brand); color:white; padding:10px 14px; font-weight:700; cursor:pointer; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; min-height:40px; }
  button.secondary, a.secondary { background:#344054; }
  button.danger { background:var(--danger); }
  input, textarea, select { width:100%; border:1px solid #cbd5e1; border-radius:6px; padding:11px 12px; font:inherit; background:white; }
  label { display:block; font-size:13px; color:#344054; font-weight:700; margin:12px 0 6px; }
  table { width:100%; border-collapse:collapse; background:white; border:1px solid var(--line); }
  th, td { text-align:left; padding:12px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { color:#475467; font-size:13px; background:#f8fafc; }
  pre { white-space:pre-wrap; word-break:break-word; background:#0b1220; color:#e6edf3; padding:14px; border-radius:8px; overflow:auto; }
  .toolbar { display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin:12px 0; }
  .notice { border-left:4px solid var(--brand); background:#eef8f6; padding:12px 14px; color:#344054; margin:12px 0; }
  .split { display:grid; grid-template-columns:minmax(0,1fr) minmax(280px,.7fr); gap:16px; align-items:start; }
  .muted { color:var(--muted); }
  .status { min-height:42px; }
  body.student-theme { --brand:#3451b2; --bg:#eef2f7; --line:#c7d2e0; }
  body.student-theme header { background:#22304f; }
  body.student-theme .card { border-color:#b7c4d8; box-shadow:0 10px 24px rgba(34,48,79,.08); }
  body.student-theme .band { background:#fdfefe; }
  @media (max-width: 760px) { header { align-items:flex-start; flex-direction:column; } .split { grid-template-columns:1fr; } main { width:min(100% - 20px, 1160px); } }
</style>
"""


def page(title, body, nav=True):
    links = ""
    if nav:
        links = """
        <nav>
          <a href="/A/lab1">Lab1 A</a><a href="/B/lab1">Lab1 B</a>
          <a href="/A/lab2">Lab2 A</a><a href="/B/lab2">Lab2 B</a>
          <a href="/A/lab3">Lab3 A</a><a href="/B/lab3">Lab3 B</a>
          <a href="/A/lab4">Lab4 A</a><a href="/B/lab4">Lab4 B</a>
          <a href="/A/lab5">Lab5 A</a><a href="/B/lab5">Lab5 B</a>
        </nav>
        """
    body_class = "student-theme" if " B" in title else ""
    return render_template_string(f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{{{ title }}}}</title>
  {BASE_CSS}
</head>
<body class="{{{{ body_class }}}}">
<header><a href="/">SSRF y Seguridad de API's</a>{links}</header>
<main>{body}</main>
</body>
</html>""", title=title, body_class=body_class)


def variant_key(group, lab):
    return f"lab{lab}{group}"


def metadata_response(url, final=False):
    clean = url.rstrip("/")
    if clean == "http://169.254.169.254/latest/meta-data":
        return META_DATA
    if clean == "http://169.254.169.254/latest/meta-data/iam/security-credentials":
        return META_DATA
    if clean == "http://169.254.169.254/latest/meta-data/iam/security-credentials/fifa-admin-backup":
        return META_DATA if final else META_DATA + "\nDemo flag: " + FLAGS["lab1B"]
    return None


def fetch_remote(url, timeout=4):
    meta = metadata_response(url)
    if meta is not None:
        return 200, "text/plain; charset=utf-8", meta.encode()
    r = requests.get(url, timeout=timeout, allow_redirects=True)
    ctype = r.headers.get("content-type", "text/plain; charset=utf-8")
    return r.status_code, ctype, r.content


@internal_app.route("/")
@internal_app.route("/index.html")
def internal_index():
    return f"""<!doctype html>
<html><head><title>Internal Catalog</title></head>
<body>
<h1>Servicio interno de imagenes</h1>
<p>Esta pagina solo escucha en 127.0.0.1:{INTERNAL_PORT} dentro del contenedor.</p>
<code>{FLAGS["lab1A"]}</code>
</body></html>"""


@internal_app.route("/cat.jpg")
def internal_cat():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360">
<rect width="100%" height="100%" fill="#d9f2ef"/>
<circle cx="320" cy="185" r="86" fill="#f2b880"/>
<polygon points="250,130 285,60 315,132" fill="#f2b880"/>
<polygon points="390,130 355,60 325,132" fill="#f2b880"/>
<circle cx="288" cy="176" r="10" fill="#101828"/>
<circle cx="352" cy="176" r="10" fill="#101828"/>
<path d="M300 220 Q320 240 340 220" stroke="#101828" stroke-width="7" fill="none" stroke-linecap="round"/>
</svg>"""
    return Response(svg, mimetype="image/svg+xml")


class ServerThread(threading.Thread):
    def __init__(self, flask_app, host, port):
        super().__init__(daemon=True)
        self.server = make_server(host, port, flask_app)
        self.ctx = flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()


def lab1_page(group):
    key = variant_key(group, 1)
    default_url = f"http://127.0.0.1:{INTERNAL_PORT}/cat.jpg"
    if group == "B":
        body = f"""
    <h1>Lab 1 B - Gestor de activos de proveedores</h1>
    <p>El area de compras registra archivos visuales enviados por proveedores para revisar su publicacion.</p>
    <div class="split">
      <section class="card">
        <h2>Ficha de proveedor</h2>
        <label>Proveedor</label><input value="FIFA Shopping Media">
        <label>URL del archivo visual</label><input id="imageUrl" value="{default_url}">
        <div class="toolbar"><button onclick="loadPreview()">Importar archivo</button><button class="secondary" onclick="publishPost()">Enviar a revision</button></div>
        <div id="status" class="status muted"></div>
      </section>
      <section class="card">
        <h2>Archivo recibido</h2>
        <div id="preview"><p>No hay archivo cargado.</p></div>
      </section>
    </div>
    <script>
    async function loadPreview(){{
      const url = document.getElementById('imageUrl').value;
      const res = await fetch('/api/{group}/lab1/fetch?url=' + encodeURIComponent(url));
      const type = res.headers.get('content-type') || '';
      const box = document.getElementById('preview');
      if(type.includes('image')) {{
        const blob = await res.blob();
        box.innerHTML = '<img alt="archivo" style="max-width:100%;border-radius:8px;border:1px solid #d8dee6" src="'+URL.createObjectURL(blob)+'">';
      }} else {{
        box.innerHTML = '<pre></pre>';
        box.querySelector('pre').textContent = await res.text();
      }}
      document.getElementById('status').textContent = 'Archivo incorporado al expediente.';
    }}
    function publishPost(){{ document.getElementById('status').textContent = 'Expediente enviado a revision.'; }}
    </script>"""
        return page(f"Lab 1 {group}", body)
    body = f"""
    <h1>Lab 1 {group} - Blog de imagenes remotas</h1>
    <p>El blog importa imagenes de proveedores externos para notas editoriales.</p>
    <div class="split">
      <section class="card">
        <h2>Nueva publicacion</h2>
        <label>Titulo</label><input value="Gato de guardia en la oficina">
        <label>URL de imagen</label><input id="imageUrl" value="{default_url}">
        <div class="toolbar"><button onclick="loadPreview()">Previsualizar imagen</button><button class="secondary" onclick="publishPost()">Publicar</button></div>
        <div id="status" class="status muted"></div>
      </section>
      <section class="card">
        <h2>Vista previa</h2>
        <div id="preview"><p>La imagen importada aparecera aqui.</p></div>
      </section>
    </div>
    <script>
    async function loadPreview(){{
      const url = document.getElementById('imageUrl').value;
      const res = await fetch('/api/{group}/lab1/fetch?url=' + encodeURIComponent(url));
      const type = res.headers.get('content-type') || '';
      const box = document.getElementById('preview');
      if(type.includes('image')) {{
        const blob = await res.blob();
        box.innerHTML = '<img alt="preview" style="max-width:100%;border-radius:8px;border:1px solid #d8dee6" src="'+URL.createObjectURL(blob)+'">';
      }} else {{
        box.innerHTML = '<pre></pre>';
        box.querySelector('pre').textContent = await res.text();
      }}
      document.getElementById('status').textContent = 'Recurso procesado por el servidor.';
    }}
    function publishPost(){{ document.getElementById('status').textContent = 'Publicacion guardada en borradores.'; }}
    </script>"""
    return page(f"Lab 1 {group}", body)


@app.get("/api/<group>/lab1/fetch")
def lab1_fetch(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    url = request.args.get("url", "")
    if not url.startswith(("http://", "https://")):
        return "URL invalida", 400
    try:
        status, ctype, content = fetch_remote(url)
        return Response(content, status=status, content_type=ctype)
    except Exception as exc:
        return Response(f"No se pudo importar el recurso: {exc}", status=502, mimetype="text/plain")


def lab2_page(group):
    body = f"""
    <h1>Lab 2 {group} - Verificador de recursos externos</h1>
    <p>El portal valida que las URLs de campanas esten disponibles antes de enviarlas al equipo editorial.</p>
    <section class="card">
      <h2>Validar URL</h2>
      <label>URL publica del recurso</label>
      <input id="target" placeholder="https://dominio-controlado.example/callback">
      <div class="toolbar"><button onclick="validateUrl()">Validar disponibilidad</button></div>
      <div id="result" class="status muted"></div>
    </section>
    <script>
    async function validateUrl(){{
      const res = await fetch('/api/{group}/lab2/validate', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{url:document.getElementById('target').value}})
      }});
      document.getElementById('result').textContent = await res.text();
    }}
    </script>"""
    return page(f"Lab 2 {group}", body)


@app.post("/api/<group>/lab2/validate")
def lab2_validate(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return "La URL no pudo validarse."
    flag = FLAGS[variant_key(group, 2)]
    payload = {"source": f"lab2-{group}", "status": "blind-ssrf-confirmed", "flag": flag}
    try:
        requests.get(url, timeout=3, allow_redirects=True)
        requests.post(url, json=payload, timeout=3, allow_redirects=True)
    except Exception:
        pass
    return "Validacion registrada. El servicio no muestra contenido remoto por politica interna."


OBJECTS_BASE = {
    "A": [
        {"guid": "94cb5f0e-3f55-4b6d-a266-6f7225a131a1", "type": "invoice", "owner": "operario", "name": "invoice-Q2-fifa-shopping.pdf"},
        {"guid": "5d0be8bb-61a0-4b22-aee3-7b33e9411ad8", "type": "voucher", "owner": "operario", "name": "voucher-proveedor-redteam.pdf"},
    ],
    "B": [
        {"guid": "af8af89f-9318-47fd-95ec-b8403e73eafe", "type": "invoice", "owner": "operario", "name": "invoice-catering-copa.pdf"},
        {"guid": "11956eb8-b615-4936-905e-8c5f04dcab09", "type": "voucher", "owner": "operario", "name": "voucher-hoteles.pdf"},
    ],
}
OBJECTS = deepcopy(OBJECTS_BASE)


def require_panel_login(group, lab):
    return session.get(f"lab{lab}_{group}_user") == "jchavez@fifashopping.com"


def panel_login(group, lab, action):
    return f"""
    <section class="card">
      <h2>Acceso interno</h2>
      <div class="notice">Nuestro equipo de red team ha identificado las credenciales jchavez@fifashopping.com:Argentina2026@</div>
      <form method="post" action="{action}">
        <label>Correo</label><input name="email" value="jchavez@fifashopping.com">
        <label>Contrasena</label><input name="password" type="password" value="Argentina2026@">
        <div class="toolbar"><button>Ingresar</button></div>
      </form>
    </section>"""


@app.route("/<group>/lab3", methods=["GET", "POST"])
def lab3(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    if request.method == "POST":
        if request.form.get("email") == "jchavez@fifashopping.com" and request.form.get("password") == "Argentina2026@":
            session[f"lab3_{group}_user"] = "jchavez@fifashopping.com"
            return redirect(f"/{group}/lab3")
    if not require_panel_login(group, 3):
        return page(f"Lab 3 {group}", f"<h1>Lab 3 {group} - Panel de objetos</h1>{panel_login(group, 3, f'/{group}/lab3')}")
    body = f"""
    <h1>Lab 3 {group} - Panel interno de objetos</h1>
    <section class="card">
      <h2>Leer Vouchers</h2>
      <p>Revision de invoices y vouchers cargados por proveedores.</p>
      <button onclick="loadObjects()">Abrir bandeja</button>
    </section>
    <section class="band">
      <div class="toolbar"><button onclick="loadObjects()">Actualizar lista</button></div>
      <div id="message" class="muted"></div>
      <table><thead><tr><th>GUID</th><th>Tipo</th><th>Archivo</th><th>Estado</th></tr></thead><tbody id="rows"></tbody></table>
    </section>
    <script>
    async function loadObjects(){{
      const res = await fetch('/{group}/lab3/api/objects');
      const data = await res.json();
      document.getElementById('rows').innerHTML = data.map(o => `<tr><td>${{o.guid}}</td><td>${{o.type}}</td><td>${{o.name}}</td><td>Disponible para lectura</td></tr>`).join('');
      document.getElementById('message').textContent = 'Bandeja sincronizada.';
    }}
    loadObjects();
    </script>"""
    return page(f"Lab 3 {group}", body)


@app.route("/api/<group>/lab3/objects", methods=["GET", "POST"])
@app.route("/<group>/lab3/api/objects", methods=["GET", "POST"])
def lab3_objects(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    if request.method == "POST":
        return Response("No autorizado para crear objetos desde este recurso. Para crear usuarios internos use /api/admin/users/create con rol y correo corporativo.", status=403, mimetype="text/plain")
    return jsonify(OBJECTS[group])


@app.delete("/api/<group>/lab3/objects/<guid>")
@app.delete("/<group>/lab3/api/objects/<guid>")
def lab3_delete(group, guid):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    before = len(OBJECTS[group])
    OBJECTS[group] = [o for o in OBJECTS[group] if o["guid"] != guid]
    if len(OBJECTS[group]) < before:
        return f"Objeto {guid} eliminado. {FLAGS[variant_key(group, 3)]}"
    return "Objeto no encontrado", 404


@app.post("/api/<group>/lab3/reset")
@app.post("/<group>/lab3/api/reset")
def lab3_reset(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    OBJECTS[group] = deepcopy(OBJECTS_BASE[group])
    return "ok"


@app.route("/<group>/lab4", methods=["GET", "POST"])
def lab4(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    if request.method == "POST":
        if request.form.get("email") == "jchavez@fifashopping.com" and request.form.get("password") == "Argentina2026@":
            session[f"lab4_{group}_user"] = "jchavez@fifashopping.com"
            session[f"lab4_{group}_role"] = "operario"
            return redirect(f"/{group}/lab4")
    if not require_panel_login(group, 4):
        return page(f"Lab 4 {group}", f"<h1>Lab 4 {group} - Panel BFLA</h1>{panel_login(group, 4, f'/{group}/lab4')}")
    body = f"""
    <h1>Lab 4 {group} - Panel interno</h1>
    <section class="card">
      <h2>Leer Vouchers</h2>
      <p>Bandeja de lectura para documentos cargados por proveedores.</p>
      <div class="toolbar"><button onclick="refreshProfile()">Abrir bandeja</button></div>
      <div id="out" class="muted"></div>
    </section>
    <script src="/static/lab4-{group}.js"></script>"""
    return page(f"Lab 4 {group}", body)


@app.get("/static/lab4-<group>.js")
def lab4_js(group):
    if group not in ("A", "B"):
        return "", 404
    js = f"""
const currentUser = "jchavez@fifashopping.com";
const profileEndpoint = "/api/{group}/lab4/profile";
const maintenanceRoute = "/{group}/lab4/administrador-5000/";
async function refreshProfile(){{
  const res = await fetch(profileEndpoint);
  const data = await res.json();
  document.getElementById("out").textContent = "Vouchers disponibles para " + data.email + ". Rol: " + data.role + ".";
}}
"""
    return Response(js, mimetype="application/javascript")


@app.get("/api/<group>/lab4/profile")
def lab4_profile(group):
    return jsonify({"email": "jchavez@fifashopping.com", "role": session.get(f"lab4_{group}_role", "operario")})


@app.route("/<group>/lab4/administrador-5000/")
def lab4_admin(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    body = f"""
    <h1>Lab 4 {group} - Administrador 5000</h1>
    <section class="card">
      <h2>Modificar usuario</h2>
      <label>Correo</label><input id="email" value="jchavez@fifashopping.com">
      <label>Nuevo rol</label><select id="role"><option>admin</option><option>operario</option></select>
      <div class="toolbar"><button onclick="promote()">Guardar cambios</button></div>
      <pre id="result"></pre>
    </section>
    <script>
    async function promote(){{
      const res = await fetch('/api/{group}/lab4/users/update-role', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{email:document.getElementById('email').value, role:document.getElementById('role').value}})
      }});
      document.getElementById('result').textContent = await res.text();
    }}
    </script>"""
    return page(f"Lab 4 {group} Admin", body)


@app.post("/api/<group>/lab4/users/update-role")
def lab4_update_role(group):
    data = request.get_json(silent=True) or {}
    if data.get("email") != "jchavez@fifashopping.com":
        return "Solo se permite actualizar el usuario autenticado.", 403
    role = data.get("role", "operario")
    session[f"lab4_{group}_role"] = role
    msg = {"email": data.get("email"), "role": role}
    if role == "admin":
        msg["flag"] = FLAGS[variant_key(group, 4)]
    return jsonify(msg)


USERS = {
    "A": [
        {"guid": "1bb0cf9a-9c34-4a85-88bf-6cfb16ec6b9e", "email": "analista@fifashopping.com", "name": "Analista Compras", "role": "user"},
        {"guid": "fdc66218-6a11-43af-a677-3638458c6220", "email": "admin-a@fifashopping.com", "name": "Admin Plataforma", "role": "admin", "flag": FLAGS["lab5A"]},
    ],
    "B": [
        {"guid": "2c16a227-3b0f-4e60-91ad-cc5923f2f2d1", "email": "soporte@fifashopping.com", "name": "Soporte Regional", "role": "user"},
        {"guid": "b380c379-60d9-4816-928a-7802b47018be", "email": "admin-b@fifashopping.com", "name": "Admin Auditoria", "role": "admin", "flag": FLAGS["lab5B"]},
    ],
}

LAB5_SCHEMA = build_schema("""
type User {
  guid: ID!
  name: String!
  email: String!
  role: String!
  flag: String
}

type Query {
  users: [User!]!
  userByGuid(guid: ID!): User
}
""")


def lab5_context(group):
    return {"group": group}


def resolve_users(obj, info):
    return USERS[info.context["group"]]


def resolve_user_by_guid(obj, info, guid):
    return next((u for u in USERS[info.context["group"]] if u["guid"] == guid), None)


LAB5_SCHEMA.type_map["Query"].fields["users"].resolve = resolve_users
LAB5_SCHEMA.type_map["Query"].fields["userByGuid"].resolve = resolve_user_by_guid


def lab5_page(group):
    visible = [u for u in USERS[group] if u["role"] != "admin"]
    rows = "".join(f"<tr><td>{u['guid']}</td><td>{u['name']}</td><td>{u['email']}</td></tr>" for u in visible)
    sample = "{ users { guid name email role flag } }"
    if group == "B":
        body = f"""
    <h1>Lab 5 {group} - Directorio de usuarios</h1>
    <section class="card">
      <h2>Usuarios regionales</h2>
      <p>Consulta publica de contactos activos para coordinacion operativa.</p>
      <div class="toolbar"><button onclick="refreshDirectory()">Actualizar directorio</button></div>
      <div id="status" class="muted"></div>
    </section>
    <section class="band">
      <table><thead><tr><th>GUID</th><th>Nombre</th><th>Correo</th></tr></thead><tbody id="directoryRows">{rows}</tbody></table>
    </section>
    <script>
    function refreshDirectory(){{
      document.getElementById('status').textContent = 'Directorio sincronizado.';
    }}
    </script>"""
        return page(f"Lab 5 {group}", body)
    body = f"""
    <h1>Lab 5 {group} - Directorio de usuarios</h1>
    <div class="split">
      <section>
        <table><thead><tr><th>GUID</th><th>Nombre</th><th>Correo</th></tr></thead><tbody>{rows}</tbody></table>
      </section>
      <section class="card">
        <h2>Consola de consulta</h2>
        <label>Query GraphQL</label>
        <textarea id="query" rows="7">{sample}</textarea>
        <div class="toolbar"><button onclick="runQuery()">Ejecutar</button></div>
        <pre id="gql"></pre>
      </section>
    </div>
    <script>
    async function runQuery(){{
      const res = await fetch('/{group}/lab5/v1/graphql', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{query:document.getElementById('query').value}})}});
      document.getElementById('gql').textContent = JSON.stringify(await res.json(), null, 2);
    }}
    </script>"""
    return page(f"Lab 5 {group}", body)


@app.post("/<group>/lab5/v1/graphql")
def lab5_graphql(group):
    if group not in ("A", "B"):
        return jsonify({"errors": ["grupo invalido"]}), 404
    data = request.get_json(silent=True) or {}
    result = graphql_sync(
        LAB5_SCHEMA,
        data.get("query") or "",
        variable_values=data.get("variables"),
        operation_name=data.get("operationName"),
        context_value=lab5_context(group),
    )
    payload = {}
    if result.errors:
        payload["errors"] = [{"message": err.message} for err in result.errors]
    if result.data is not None:
        payload["data"] = result.data
    return jsonify(payload), 400 if result.errors and result.data is None else 200


FINAL_DOCS = {
    "lmessi@fifa2026.com": [
        {"guid": "10", "title": "Itinerario privado", "flag": None},
        {"guid": "9", "title": "Lista de proveedores", "flag": None},
    ],
    "ehaaland@fifa2026.com": [
        {"guid": "8", "title": "Carga de documentos", "flag": None},
        {"guid": "7", "title": "Revision medica", "flag": None},
    ],
}
FINAL_ALL_DOCS = [
    {"guid": "10", "title": "Itinerario privado", "flag": None},
    {"guid": "9", "title": "Lista de proveedores", "flag": None},
    {"guid": "8", "title": "Carga de documentos", "flag": None},
    {"guid": "7", "title": "Revision medica", "flag": None},
    {"guid": "6", "title": "Reserva de vuelos", "flag": None},
    {"guid": "5", "title": "Contrato de imagen", "flag": None},
    {"guid": "4", "title": "Inventario de uniformes", "flag": None},
    {"guid": "3", "title": "Reporte de seguridad", "flag": None},
    {"guid": "2", "title": "Credenciales temporales", "flag": None},
    {"guid": "1", "title": "Informe reservado de auditoria", "flag": FLAGS["lab6_lmessi"]},
]

FINAL_PASSWORDS = {
    "lmessi@fifa2026.com": "Argentina2026@",
    "ehaaland@fifa2026.com": "Noruega2026@",
    "lyamal@fifa2026.com": "España2026@",
}


@app.route("/testing", methods=["GET", "POST"])
def testing():
    if request.method == "POST":
        email = request.form.get("email", "")
        if FINAL_PASSWORDS.get(email) == request.form.get("password"):
            session["final_user"] = email
            return redirect("/testing/panel")
    body = """
    <h1>Testing Portal</h1>
    <section class="card">
      <div class="notice">Nuestro Equipo de Red Team ha identificado estas credenciales lmessi@fifa2026.com:Argentina2026@ y ehaaland@fifa2026.com:Noruega2026@</div>
      <form method="post">
        <label>Correo</label><input name="email">
        <label>Contrasena</label><input name="password" type="password">
        <div class="toolbar"><button>Ingresar</button></div>
      </form>
    </section>"""
    return page("Testing", body)


@app.get("/testing/panel")
def testing_panel():
    user = session.get("final_user")
    if not user:
        return redirect("/testing")
    if user == "lyamal@fifa2026.com":
        body = """
        <h1>Panel de backup administrativo</h1>
        <section class="band">
          <h2>Operaciones de archivos</h2>
          <table>
            <thead><tr><th>Operacion</th><th>Ultima ejecucion</th><th>Estado</th></tr></thead>
            <tbody>
              <tr><td>Copia operacional</td><td>07:30</td><td>Pendiente de revision</td></tr>
              <tr><td>Duplicado de respaldo</td><td>08:15</td><td>Disponible</td></tr>
              <tr><td>Backup programado</td><td>09:00</td><td>Activo</td></tr>
            </tbody>
          </table>
        </section>
        <div class="split">
          <section class="card">
            <h2>Copiado de archivo</h2>
            <label>Origen</label><input id="copySrc" value="{{ source_file }}">
            <label>Destino</label><input id="copyDst" value="{{ copy_file }}">
            <div class="toolbar"><button onclick="copyFile()">Ejecutar copia</button></div>
          </section>
          <section class="card">
            <h2>Duplicado de respaldo</h2>
            <label>Nombre del respaldo</label><input id="dupName" value="backup-final.txt">
            <label>Prioridad</label><select><option>Normal</option><option>Alta</option></select>
            <div class="toolbar"><button onclick="duplicate()">Generar duplicado</button></div>
          </section>
        </div>
        <section class="card">
          <h2>Backup programado</h2>
          <label>Etiqueta del paquete</label><input id="backupName" value="daily">
          <label>Comentario interno</label><textarea rows="3">Respaldo operativo previo a cierre de jornada.</textarea>
          <div class="toolbar"><button onclick="backup()">Crear backup</button></div>
        </section>
        <pre id="adminOut"></pre>
        <script>
        async function copyFile(){ const r = await fetch('/testing/api/admin/copy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({src:copySrc.value,dst:copyDst.value})}); adminOut.textContent = await r.text(); }
        async function duplicate(){ const r = await fetch('/testing/api/admin/duplicate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:dupName.value})}); adminOut.textContent = await r.text(); }
        async function backup(){ const r = await fetch('/testing/api/admin/backup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:backupName.value})}); adminOut.textContent = await r.text(); }
        </script>"""
        return page("Testing Admin", render_template_string(body, source_file=SOURCE_FILE, copy_file=os.path.join(TMP_DIR, "fifa-copy.txt")))
    docs = FINAL_DOCS.get(user, [])
    rows = "".join(f"<tr><td>{d['guid']}</td><td>{d['title']}</td><td><button onclick=\"viewDoc('{d['guid']}')\">Ver</button></td></tr>" for d in docs)
    upload = ""
    if user == "ehaaland@fifa2026.com":
        upload = """
        <section class="card">
          <h2>Carga de documentos</h2>
          <label>URL del documento</label><input id="docUrl" placeholder="https://proveedor.example/documento.pdf">
          <div class="toolbar"><button onclick="importDoc()">Importar documento</button></div>
          <pre id="importOut"></pre>
        </section>"""
    body = f"""
    <h1>Testing Portal - {user}</h1>
    <section class="band">
      <table><thead><tr><th>Identificador</th><th>Documento</th><th>Accion</th></tr></thead><tbody>{rows}</tbody></table>
      <pre id="docOut"></pre>
    </section>
    {upload}
    <script>
    async function viewDoc(id){{ const r = await fetch('/testing/api/documents/'+id); docOut.textContent = await r.text(); }}
    async function importDoc(){{ const r = await fetch('/testing/api/import', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{url:docUrl.value}})}}); importOut.textContent = await r.text(); }}
    </script>"""
    return page("Testing Panel", body)


@app.get("/testing/api/documents/<doc_id>")
def testing_doc(doc_id):
    for doc in FINAL_ALL_DOCS:
        if doc["guid"] == doc_id:
            return f"Documento: {doc['title']}\nIdentificador: {doc['guid']}\n" + (doc["flag"] or "Sin observaciones.")
    return "Documento no encontrado", 404


@app.post("/testing/api/import")
def testing_import():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    meta = metadata_response(url, final=True)
    if meta is not None:
        return meta
    try:
        r = requests.get(url, timeout=4)
        return f"Documento importado. HTTP {r.status_code}"
    except Exception as exc:
        return f"No se pudo importar el documento: {exc}", 502


def ensure_demo_files():
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(SOURCE_FILE, "w", encoding="utf-8") as fh:
        fh.write("archivo base de backup\n")
    with open(ADMIN_FLAG_FILE, "w", encoding="utf-8") as fh:
        fh.write(FLAGS["lab6_cmd"] + "\n")


@app.post("/testing/api/admin/copy")
def admin_copy():
    data = request.get_json(silent=True) or {}
    src = data.get("src", SOURCE_FILE)
    dst = data.get("dst", os.path.join(TMP_DIR, "fifa-copy.txt"))
    try:
        subprocess.run(["cp", src, dst], check=True, capture_output=True, text=True)
        return f"Copiado {src} -> {dst}"
    except subprocess.CalledProcessError as exc:
        return exc.stderr or str(exc), 500


@app.post("/testing/api/admin/backup")
def admin_backup():
    data = request.get_json(silent=True) or {}
    name = re.sub(r"[^a-zA-Z0-9_.-]", "_", data.get("name", "daily"))
    path = os.path.join(TMP_DIR, f"{name}.tar")
    try:
        subprocess.run(["tar", "-cf", path, SOURCE_FILE], capture_output=True, text=True)
        return f"Backup creado en {path}"
    except Exception as exc:
        return str(exc), 500


@app.post("/testing/api/admin/duplicate")
def admin_duplicate():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "backup-final.txt")
    cmd = f"cp {shlex.quote(SOURCE_FILE)} {shlex.quote(TMP_DIR)}/{name}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
    output = proc.stdout + proc.stderr
    if not output.strip():
        output = f"Comando ejecutado: {cmd}"
    return output + "\n" + FLAGS["lab6_cmd"]


@app.get("/")
def index():
    cards = ""
    for group, label in (("A", "Profesor"), ("B", "Alumno")):
        for lab, name in ((1, "SSRF"), (2, "SSRF ciego"), (3, "BOLA"), (4, "BFLA"), (5, "GraphQL")):
            cards += f'<section class="card"><h2>Lab {lab} {group}</h2><p>{label} - {name}</p><a class="button" href="/{group}/lab{lab}">Abrir</a></section>'
    return page("Laboratorios SSRF y API", f"<h1>Laboratorios SSRF y Seguridad de API's</h1><div class='grid'>{cards}</div>")


@app.get("/<group>/lab1")
def route_lab1(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    return lab1_page(group)


@app.get("/<group>/lab2")
def route_lab2(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    return lab2_page(group)


@app.get("/<group>/lab5")
def route_lab5(group):
    if group not in ("A", "B"):
        return "grupo invalido", 404
    return lab5_page(group)


if __name__ == "__main__":
    ensure_demo_files()
    internal_server = ServerThread(internal_app, "127.0.0.1", INTERNAL_PORT)
    internal_server.start()
    app.run(host="0.0.0.0", port=PUBLIC_PORT)
