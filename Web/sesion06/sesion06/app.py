from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse, unquote
from http.cookies import SimpleCookie
import base64
import hashlib
import hmac
import html
import json
import os
import secrets


HOST = "0.0.0.0"
PORT = 8000
ROOT_USER = "root"
ROOT_PASS = "987654321"
FINAL_JWT_SECRET = "jwt_secret_final_labo_2026"
DEFAULT_JWT_SECRET = "public_demo_secret"

SESSIONS = {}

FLAGS = {
    "alumno": {
        "lab1": "FLAG{ALUMNO_IDOR_VOUCHER_20260510}",
        "lab2": "FLAG{ALUMNO_IDOR_PSEUDOGUID_00}",
        "lab4": "FLAG{ALUMNO_MASS_ASSIGNMENT_SUPERADMIN}",
    },
    "profesor": {
        "lab1": "FLAG{PROFESOR_IDOR_VOUCHER_20260510}",
        "lab2": "FLAG{PROFESOR_IDOR_PSEUDOGUID_00}",
        "lab4": "FLAG{PROFESOR_MASS_ASSIGNMENT_SUPERADMIN}",
    },
}

LAB_TITLES = {
    "lab1": "Tienda Online",
    "lab2": "Portal de Inventario",
    "lab3": "Biblioteca Interna",
    "lab4": "Centro de Cuenta",
}


def b64url(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def sign_jwt(payload, secret):
    header = {"alg": "HS256", "typ": "JWT"}
    head = b64url(json.dumps(header, separators=(",", ":")))
    body = b64url(json.dumps(payload, separators=(",", ":")))
    sig = hmac.new(secret.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{b64url(sig)}"


def verify_jwt(token):
    try:
        head, body, sig = token.split(".")
        raw = f"{head}.{body}".encode()
        for secret in (DEFAULT_JWT_SECRET, FINAL_JWT_SECRET):
            expected = b64url(hmac.new(secret.encode(), raw, hashlib.sha256).digest())
            if hmac.compare_digest(expected, sig):
                return json.loads(b64url_decode(body))
    except Exception:
        return None
    return None


def page(title, body, active=""):
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --ink: #1d252d;
      --muted: #66717d;
      --line: #d9e0e7;
      --panel: #ffffff;
      --primary: #176b87;
      --primary-dark: #0d4e63;
      --accent: #b25f24;
      --ok: #20764f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }}
    header {{
      background: #15212b;
      color: #fff;
      padding: 18px 24px;
      border-bottom: 4px solid var(--accent);
    }}
    header a {{ color: #fff; text-decoration: none; font-weight: 700; }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px 18px 48px;
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      margin-bottom: 22px;
    }}
    h1 {{ margin: 0; font-size: clamp(26px, 4vw, 40px); letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 22px; letter-spacing: 0; }}
    p {{ color: var(--muted); margin: 0 0 16px; }}
    a {{ color: var(--primary-dark); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
      gap: 16px;
    }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 22px rgba(20, 32, 42, 0.06);
    }}
    .card h2 {{ font-size: 18px; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 14px; }}
    button, .btn {{
      appearance: none;
      border: 0;
      border-radius: 6px;
      background: var(--primary);
      color: #fff;
      min-height: 40px;
      padding: 10px 14px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 14px;
    }}
    button:hover, .btn:hover {{ background: var(--primary-dark); }}
    .secondary {{ background: #56616d; }}
    .secondary:hover {{ background: #404a54; }}
    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      min-height: 40px;
      padding: 9px 11px;
      font-size: 15px;
      background: #fff;
    }}
    label {{ display: block; font-weight: 700; margin: 12px 0 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px; border-bottom: 1px solid var(--line); text-align: left; }}
    th {{ background: #e9eef3; }}
    .price {{ color: var(--ok); font-weight: 800; }}
    .voucher {{
      border: 2px dashed #97a6b3;
      background: #fff;
      padding: 22px;
      border-radius: 8px;
      max-width: 620px;
    }}
    .flag {{
      background: #102027;
      color: #b7ffd9;
      border-radius: 6px;
      padding: 14px;
      font-family: Consolas, monospace;
      overflow-wrap: anywhere;
    }}
    .notice {{ color: #6a4d16; background: #fff7db; border: 1px solid #e9d28e; padding: 12px; border-radius: 6px; }}
    .filebox {{ background: #101820; color: #e9f3f4; padding: 16px; border-radius: 8px; white-space: pre-wrap; overflow: auto; }}
    iframe {{ width: 100%; min-height: 520px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    @media (max-width: 640px) {{
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      th, td {{ font-size: 14px; }}
    }}
  </style>
</head>
<body>
  <header><a href="/">Laboratorio IDOR y Control de Acceso</a></header>
  <main>{body}</main>
</body>
</html>"""


class LabHandler(BaseHTTPRequestHandler):
    server_version = "AccessLab/1.0"

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args))

    def send_html(self, title, body, status=200):
        data = page(title, body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_text(self, text, status=200, content_type="text/plain; charset=utf-8"):
        data = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, target, cookies=None):
        self.send_response(302)
        self.send_header("Location", target)
        if cookies:
            for cookie in cookies:
                self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def parsed(self):
        url = urlparse(self.path)
        return url.path, parse_qs(url.query)

    def cookies(self):
        raw = self.headers.get("Cookie", "")
        jar = SimpleCookie()
        jar.load(raw)
        return {key: val.value for key, val in jar.items()}

    def get_session(self, area):
        sid = self.cookies().get(f"sid_{area}")
        if not sid:
            return None
        return SESSIONS.get(sid)

    def require_login(self, area, scope, lab):
        session = self.get_session(f"{scope}_{lab}")
        if session and session.get("user") == ROOT_USER:
            return session
        self.redirect(f"/{scope}/{lab}/login")
        return None

    def do_GET(self):
        path, qs = self.parsed()
        if path == "/":
            self.home()
            return
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in ("alumno", "profesor"):
            scope, lab = parts[0], parts[1]
            rest = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"
            if lab == "lab1":
                self.lab1_get(scope, rest, qs)
                return
            if lab == "lab2":
                self.lab2_get(scope, rest, qs)
                return
            if lab == "lab3":
                self.lab3_get(scope, rest, qs)
                return
            if lab == "lab4":
                self.lab4_get(scope, rest, qs)
                return
        if path.startswith("/sse"):
            self.final_get(path, qs)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1><p>Pagina no encontrada.</p></div>", 404)

    def do_POST(self):
        path, qs = self.parsed()
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode()
        form = parse_qs(raw)
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in ("alumno", "profesor"):
            scope, lab = parts[0], parts[1]
            rest = "/" + "/".join(parts[2:]) if len(parts) > 2 else "/"
            if lab == "lab1":
                self.lab1_post(scope, rest, form)
                return
            if lab == "lab2":
                self.lab2_post(scope, rest, form)
                return
            if lab == "lab3":
                self.lab3_post(scope, rest, form)
                return
            if lab == "lab4":
                self.lab4_post(scope, rest, form)
                return
        if path.startswith("/sse"):
            self.final_post(path, form)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1><p>Pagina no encontrada.</p></div>", 404)

    def home(self):
        cards = []
        for scope in ("alumno", "profesor"):
            label = "Alumno" if scope == "alumno" else "Profesor"
            for lab in ("lab1", "lab2", "lab3", "lab4"):
                cards.append(f"""
                <article class="card">
                  <h2>{label} - {LAB_TITLES[lab]}</h2>
                  <p>Entorno practico de la clase.</p>
                  <a class="btn" href="/{scope}/{lab}">Abrir</a>
                </article>""")
        body = f"""
        <div class="topbar">
          <div>
            <h1>IDOR y Fallos de Control de Acceso</h1>
            <p>Laboratorios vulnerables para ejecutar en un unico contenedor.</p>
          </div>
        </div>
        <section class="grid">{''.join(cards)}</section>"""
        self.send_html("Laboratorios", body)

    def login_page(self, scope, lab, error=""):
        msg = "<p class='notice'>Credenciales invalidas.</p>" if error else ""
        body = f"""
        <section class="panel" style="max-width:480px;margin:auto">
          <h1>{LAB_TITLES[lab]}</h1>
          <p>Iniciar sesion para continuar.</p>
          {msg}
          <form method="post" action="/{scope}/{lab}/login">
            <label>Usuario</label>
            <input name="username" autocomplete="username">
            <label>Contrasena</label>
            <input name="password" type="password" autocomplete="current-password">
            <div class="actions"><button type="submit">Entrar</button><a class="btn secondary" href="/">Volver</a></div>
          </form>
        </section>"""
        self.send_html("Login", body)

    def handle_login(self, area, form, target):
        user = form.get("username", [""])[0]
        password = form.get("password", [""])[0]
        if user == ROOT_USER and password == ROOT_PASS:
            sid = secrets.token_urlsafe(24)
            SESSIONS[sid] = {"user": user, "role": "admin", "super": False}
            self.redirect(target, [f"sid_{area}={sid}; Path=/; HttpOnly; SameSite=Lax"])
            return
        return False

    def lab1_get(self, scope, rest, qs):
        if rest == "/":
            body = f"""
            <div class="topbar"><h1>Tienda Online</h1><a class="btn secondary" href="/">Inicio</a></div>
            <section class="grid">
              <article class="card"><h2>Teclado mecanico</h2><p>Switches silenciosos y estructura metalica.</p><p class="price">S/ 149.00</p><form method="post" action="/{scope}/lab1/buy"><input type="hidden" name="item" value="teclado"><button>Comprar</button></form></article>
              <article class="card"><h2>Mouse ergonomico</h2><p>Sensor optico y botones laterales.</p><p class="price">S/ 89.00</p><form method="post" action="/{scope}/lab1/buy"><input type="hidden" name="item" value="mouse"><button>Comprar</button></form></article>
              <article class="card"><h2>Audifonos USB</h2><p>Audio claro para reuniones y clases.</p><p class="price">S/ 119.00</p><form method="post" action="/{scope}/lab1/buy"><input type="hidden" name="item" value="audifonos"><button>Comprar</button></form></article>
            </section>"""
            self.send_html("Tienda Online", body)
            return
        if rest == "/voucher":
            voucher_id = qs.get("id", [""])[0]
            if voucher_id == "20260510":
                content = f"<p class='flag'>{FLAGS[scope]['lab1']}</p>"
            else:
                content = "<p>Compra registrada correctamente. Estado: pagado.</p><p>Total: S/ 149.00</p>"
            body = f"""
            <div class="topbar"><h1>Voucher de compra</h1><a class="btn secondary" href="/{scope}/lab1">Tienda</a></div>
            <section class="voucher">
              <h2>Comprobante #{html.escape(voucher_id)}</h2>
              {content}
            </section>"""
            self.send_html("Voucher", body)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab1_post(self, scope, rest, form):
        if rest == "/buy":
            self.redirect(f"/{scope}/lab1/voucher?id=20260523")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab2_get(self, scope, rest, qs):
        if rest == "/login":
            self.login_page(scope, "lab2")
            return
        session = self.require_login(f"{scope}_lab2", scope, "lab2")
        if not session:
            return
        if rest == "/":
            body = f"""
            <div class="topbar"><h1>Portal de Inventario</h1><a class="btn secondary" href="/">Inicio</a></div>
            <section class="panel">
              <h2>Productos asignados</h2>
              <table><tr><th>Codigo</th><th>Producto</th><th>Estado</th><th></th></tr>
              <tr><td>ARMGUID202607-PROD-15</td><td>Servidor ARM Edge</td><td>Activo</td><td><a class="btn" href="/{scope}/lab2/resource?guid=ARMGUID202607-PROD-15">Ver</a></td></tr>
              <tr><td>ARMGUID202607-PROD-16</td><td>Sensor Industrial</td><td>Activo</td><td><a class="btn" href="/{scope}/lab2/resource?guid=ARMGUID202607-PROD-16">Ver</a></td></tr>
              </table>
            </section>"""
            self.send_html("Inventario", body)
            return
        if rest == "/resource":
            guid = qs.get("guid", [""])[0]
            if guid == "ARMGUID202605-PROD-00":
                detail = f"<p class='flag'>{FLAGS[scope]['lab2']}</p>"
            else:
                detail = f"<p>Recurso {html.escape(guid)} disponible para revision administrativa.</p><p>Garantia activa y stock reservado.</p>"
            self.send_html("Recurso", f"<div class='topbar'><h1>Detalle de producto</h1><a class='btn secondary' href='/{scope}/lab2'>Volver</a></div><section class='panel'>{detail}</section>")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab2_post(self, scope, rest, form):
        if rest == "/login":
            if self.handle_login(f"{scope}_lab2", form, f"/{scope}/lab2") is False:
                self.login_page(scope, "lab2", "1")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab3_get(self, scope, rest, qs):
        if rest == "/login":
            self.login_page(scope, "lab3")
            return
        session = self.require_login(f"{scope}_lab3", scope, "lab3")
        if not session:
            return
        if rest == "/":
            body = f"""
            <div class="topbar"><h1>Biblioteca Interna</h1><a class="btn secondary" href="/">Inicio</a></div>
            <section class="panel">
              <h2>Documento disponible</h2>
              <p>Vista previa del documento asignado.</p>
              <iframe src="/{scope}/lab3/view?file=prueba.pdf"></iframe>
            </section>"""
            self.send_html("Biblioteca Interna", body)
            return
        if rest == "/view":
            requested = unquote(qs.get("file", [""])[0])
            path = requested if os.path.isabs(requested) else os.path.join(os.getcwd(), "uploads", requested)
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                content_type = "application/pdf" if requested.endswith(".pdf") else "text/plain; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except OSError:
                self.send_text("Archivo no disponible.", 404)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab3_post(self, scope, rest, form):
        if rest == "/login":
            if self.handle_login(f"{scope}_lab3", form, f"/{scope}/lab3") is False:
                self.login_page(scope, "lab3", "1")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab4_get(self, scope, rest, qs):
        if rest == "/login":
            self.login_page(scope, "lab4")
            return
        session = self.require_login(f"{scope}_lab4", scope, "lab4")
        if not session:
            return
        if rest == "/":
            super_button = ""
            if session.get("super"):
                super_button = f"<a class='btn' href='/{scope}/lab4/super'>Panel avanzado</a>"
            body = f"""
            <div class="topbar"><h1>Centro de Cuenta</h1><a class="btn secondary" href="/">Inicio</a></div>
            <section class="grid">
              <article class="card"><h2>Perfil</h2><p>Usuario: root</p><p>Rol: admin</p>{super_button}</article>
              <article class="card">
                <h2>Cambiar contrasena</h2>
                <form method="post" action="/{scope}/lab4/password">
                  <label>Nueva contrasena</label>
                  <input name="password" type="password">
                  <label>Confirmar contrasena</label>
                  <input name="confirm" type="password">
                  <div class="actions"><button>Guardar</button></div>
                </form>
              </article>
            </section>"""
            self.send_html("Centro de Cuenta", body)
            return
        if rest == "/super":
            if session.get("super"):
                self.send_html("Panel avanzado", f"<div class='topbar'><h1>Panel avanzado</h1><a class='btn secondary' href='/{scope}/lab4'>Volver</a></div><section class='panel'><p class='flag'>{FLAGS[scope]['lab4']}</p></section>")
            else:
                self.send_html("Acceso denegado", "<section class='panel'><h1>Acceso denegado</h1></section>", 403)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def lab4_post(self, scope, rest, form):
        if rest == "/login":
            if self.handle_login(f"{scope}_lab4", form, f"/{scope}/lab4") is False:
                self.login_page(scope, "lab4", "1")
            return
        session = self.require_login(f"{scope}_lab4", scope, "lab4")
        if not session:
            return
        if rest == "/password":
            if form.get("isSuperAdmin", ["false"])[0].lower() in ("1", "true", "yes", "on"):
                session["super"] = True
            self.redirect(f"/{scope}/lab4")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def final_cookie_payload(self):
        token = self.cookies().get("final_token")
        return verify_jwt(token) if token else None

    def final_get(self, path, qs):
        if path == "/sse":
            payload = self.final_cookie_payload()
            if not payload:
                body = """
                <section class="panel" style="max-width:480px;margin:auto">
                  <h1>Panel SSE</h1>
                  <p>Ingrese al panel de gestion.</p>
                  <form method="post" action="/sse/login">
                    <label>Usuario</label><input name="username">
                    <label>Contrasena</label><input name="password" type="password">
                    <div class="actions"><button>Entrar</button><a class="btn secondary" href="/">Inicio</a></div>
                  </form>
                </section>"""
                self.send_html("Panel SSE", body)
                return
            tool = ""
            if payload.get("role") == "superadmin":
                tool = """
                <section class="panel">
                  <h2>Consulta de archivos</h2>
                  <p class="notice">Solo lectura de archivos subidos en /uploads</p>
                  <form method="get" action="/sse/apiv2/files">
                    <label>Archivo</label>
                    <input name="file" value="saludo.txt">
                    <div class="actions"><button>Consultar</button></div>
                  </form>
                </section>"""
            body = f"""
            <div class="topbar"><h1>Recursos SSE</h1><a class="btn secondary" href="/">Inicio</a></div>
            <section class="panel">
              <h2>Archivos asociados</h2>
              <table><tr><th>UID</th><th>Nombre</th><th></th></tr>
              <tr><td>SSE-GUID-7841</td><td>saludo.txt</td><td><a class="btn" href="/sse/resource?uid=SSE-GUID-7841">Abrir</a></td></tr>
              <tr><td>SSE-GUID-7842</td><td>todo.txt</td><td><a class="btn" href="/sse/resource?uid=SSE-GUID-7842">Abrir</a></td></tr>
              </table>
            </section>
            {tool}"""
            self.send_html("Recursos SSE", body)
            return
        if path == "/sse/resource":
            payload = self.final_cookie_payload()
            if not payload:
                self.redirect("/sse")
                return
            uid = qs.get("uid", [""])[0]
            resources = {
                "SSE-GUID-7841": ("saludo.txt", open(os.path.join("uploads", "saludo.txt"), encoding="utf-8").read()),
                "SSE-GUID-7842": ("todo.txt", open(os.path.join("uploads", "todo.txt"), encoding="utf-8").read()),
                "SSE-GUID-7840": ("Contrasena jwt.txt", FINAL_JWT_SECRET),
            }
            name, content = resources.get(uid, ("archivo.txt", "Recurso no encontrado."))
            body = f"""
            <div class="topbar"><h1>{html.escape(name)}</h1><a class="btn secondary" href="/sse">Volver</a></div>
            <section class="panel"><pre class="filebox">{html.escape(content)}</pre></section>"""
            self.send_html(name, body)
            return
        if path == "/sse/apiv2/files":
            payload = self.final_cookie_payload()
            if not payload or payload.get("role") != "superadmin":
                self.send_html("Acceso denegado", "<section class='panel'><h1>Acceso denegado</h1></section>", 403)
                return
            requested = os.path.basename(qs.get("file", [""])[0])
            path_fs = os.path.join(os.getcwd(), "uploads", requested)
            self.file_result(path_fs)
            return
        if path == "/sse/apiv1/files":
            payload = self.final_cookie_payload()
            if not payload or payload.get("role") != "superadmin":
                self.send_html("Acceso denegado", "<section class='panel'><h1>Acceso denegado</h1></section>", 403)
                return
            requested = unquote(qs.get("file", [""])[0]).replace("//....", "/..")
            base = os.path.join(os.getcwd(), "uploads")
            path_fs = os.path.normpath(os.path.join(base, requested.lstrip("/")))
            if requested.startswith("/"):
                path_fs = os.path.normpath(requested)
            self.file_result(path_fs)
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def final_post(self, path, form):
        if path == "/sse/login":
            user = form.get("username", [""])[0]
            password = form.get("password", [""])[0]
            if user == ROOT_USER and password == ROOT_PASS:
                token = sign_jwt({"user": "root", "role": "user"}, DEFAULT_JWT_SECRET)
                self.redirect("/sse", [f"final_token={token}; Path=/; SameSite=Lax"])
                return
            self.redirect("/sse")
            return
        self.send_html("No encontrado", "<div class='panel'><h1>404</h1></div>", 404)

    def file_result(self, path_fs):
        try:
            with open(path_fs, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
            body = f"<div class='topbar'><h1>Resultado</h1><a class='btn secondary' href='/sse'>Volver</a></div><section class='panel'><pre class='filebox'>{html.escape(content)}</pre></section>"
            self.send_html("Resultado", body)
        except OSError:
            self.send_html("No disponible", "<section class='panel'><h1>Archivo no disponible</h1></section>", 404)


if __name__ == "__main__":
    print(f"Servidor iniciado en http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), LabHandler).serve_forever()
