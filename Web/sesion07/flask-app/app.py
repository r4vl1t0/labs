import os
import subprocess
from html import escape
from flask import Flask, request, render_template_string

app = Flask(__name__)

STYLE = """
<style>
  :root { color-scheme: light; font-family: Inter, Segoe UI, Arial, sans-serif; }
  body { margin: 0; background: #f4f6f8; color: #1d2733; }
  header { background: #17202a; color: white; padding: 22px 30px; }
  main { max-width: 980px; margin: 28px auto; padding: 0 18px; }
  nav { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }
  a.card, section.panel { background: white; border: 1px solid #d8dee6; border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
  a.card { display: block; color: inherit; text-decoration: none; }
  a.card:hover { border-color: #607d9b; }
  label { display: block; font-weight: 650; margin: 14px 0 7px; }
  input, textarea, select { width: 100%; box-sizing: border-box; padding: 11px; border: 1px solid #b8c2cc; border-radius: 6px; font: inherit; background: white; }
  textarea { min-height: 132px; resize: vertical; }
  button { margin-top: 14px; background: #255f85; color: white; border: 0; border-radius: 6px; padding: 11px 15px; font-weight: 700; cursor: pointer; }
  button.secondary { background: #536270; }
  pre, .result { background: #101820; color: #d6f5e3; padding: 14px; border-radius: 6px; overflow: auto; white-space: pre-wrap; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
  .muted { color: #586575; }
</style>
"""

def page(title, body):
    return f"""
    <!doctype html>
    <html lang="es">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>{STYLE}</head>
    <body><header><h1>{escape(title)}</h1></header><main>{body}</main></body></html>
    """

@app.get("/")
def index():
    cards = []
    labs = [
        ("A", "Profesor"),
        ("B", "Alumno"),
    ]
    for prefix, name in labs:
        cards.extend([
            (f"/{prefix}/lab1-command-injection-1", f"{name} - Panel de conectividad"),
            (f"/{prefix}/lab2-command-njection2", f"{name} - Gestor de archivos"),
            (f"/{prefix}/lab3-ssti-pebble", f"{name} - Comunicados internos"),
            (f"/{prefix}/lab4-ssti-jinja2", f"{name} - Plantillas de notas"),
            (f"/{prefix}/lab5-xxe", f"{name} - Centro de reportes"),
        ])
    html = "<nav>" + "".join(f'<a class="card" href="{url}"><strong>{text}</strong><p class="muted">Abrir modulo</p></a>' for url, text in cards) + "</nav>"
    return page("Laboratorios de Inyecciones Avanzadas y XXE", html)

def ping_panel(area, separator_name):
    title = "Panel de conectividad"
    target = request.form.get("target", "127.0.0.1")
    output = ""
    if request.method == "POST":
        if area == "A" and "|" in target:
            output = "El valor ingresado no cumple el formato esperado."
        elif area == "B" and ";" in target:
            output = "El valor ingresado no cumple el formato esperado."
        else:
            cmd = f"ping -c 1 {target}"
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=4)
            except subprocess.CalledProcessError as exc:
                output = exc.output
            except subprocess.TimeoutExpired:
                output = "La operacion tardo demasiado."
    body = f"""
    <section class="panel">
      <h2>Verificacion de host</h2>
      <p class="muted">Ejecuta una prueba rapida de disponibilidad contra un servidor autorizado.</p>
      <form method="post">
        <label>Host o direccion IP</label>
        <input name="target" value="{escape(target)}">
        <button>Ejecutar prueba</button>
      </form>
      <h3>Resultado</h3>
      <pre>{escape(output)}</pre>
    </section>
    """
    return page(title, body)

@app.route("/A/lab1-command-injection-1", methods=["GET", "POST"])
def a_lab1():
    return ping_panel("A", ";")

@app.route("/B/lab1-command-injection-1", methods=["GET", "POST"])
def b_lab1():
    return ping_panel("B", "|")

def file_manager(area):
    title = "Gestor de archivos"
    action = request.form.get("action", "copy")
    filename = request.form.get("filename", "reporte.txt")
    output = ""
    if request.method == "POST":
        if action == "copy":
            cmd = ["cp", "/app/workspace/reporte.txt", "/app/workspace/copia_reporte.txt"]
            subprocess.run(cmd, capture_output=True, text=True)
            output = "Archivo copiado correctamente."
        elif action == "paste":
            with open("/app/workspace/notas.txt", "a", encoding="utf-8") as f:
                f.write("Nueva entrada agregada desde el panel.\n")
            output = "Contenido agregado correctamente."
        elif action == "duplicate":
            if " " in filename or "whoami" in filename.lower():
                output = "Nombre de archivo rechazado por la politica del panel."
            else:
                cmd = f"cp /app/workspace/{filename} /app/workspace/{filename}.bak"
                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=4)
                    output = output or "Archivo duplicado correctamente."
                except subprocess.CalledProcessError as exc:
                    output = exc.output
                except subprocess.TimeoutExpired:
                    output = "La operacion tardo demasiado."
    body = f"""
    <section class="panel">
      <h2>Operaciones disponibles</h2>
      <form method="post">
        <label>Operacion</label>
        <select name="action">
          <option value="copy" {"selected" if action == "copy" else ""}>Copiar archivo</option>
          <option value="paste" {"selected" if action == "paste" else ""}>Pegar archivo</option>
          <option value="duplicate" {"selected" if action == "duplicate" else ""}>Duplicar archivo</option>
        </select>
        <label>Archivo</label>
        <input name="filename" value="{escape(filename)}">
        <button>Procesar</button>
      </form>
      <h3>Estado</h3>
      <pre>{escape(output)}</pre>
    </section>
    """
    return page(title, body)

@app.route("/A/lab2-command-njection2", methods=["GET", "POST"])
def a_lab2():
    return file_manager("A")

@app.route("/B/lab2-command-njection2", methods=["GET", "POST"])
def b_lab2():
    return file_manager("B")

def jinja_lab(area):
    title = "Plantillas de notas"
    template = request.form.get("template", "Hola {{ nombre }}, tu solicitud fue registrada.")
    result = ""
    if request.method == "POST":
        try:
            result = render_template_string(template, nombre="Operador", area=area)
        except Exception as exc:
            result = f"Error al generar la vista: {exc}"
    body = f"""
    <section class="panel">
      <h2>Previsualizacion de nota</h2>
      <p class="muted">El equipo usa este formulario para revisar mensajes antes de publicarlos.</p>
      <form method="post">
        <label>Contenido</label>
        <textarea name="template">{escape(template)}</textarea>
        <button>Previsualizar</button>
      </form>
      <h3>Vista generada</h3>
      <div class="result">{escape(result)}</div>
    </section>
    """
    return page(title, body)

@app.route("/A/lab4-ssti-jinja2", methods=["GET", "POST"])
def a_lab4():
    return jinja_lab("A")

@app.route("/B/lab4-ssti-jinja2", methods=["GET", "POST"])
def b_lab4():
    return jinja_lab("B")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
