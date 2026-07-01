from flask import Flask, redirect, Response

app = Flask(__name__)

TOTAL_PAGES = 20

@app.route("/")
def index():
    return redirect("/pagina1", code=302)


@app.route("/pagina<int:num>")
def pagina(num):

    if num < 1 or num > TOTAL_PAGES:
        return "404", 404

    # Penúltima página
    if num == TOTAL_PAGES - 1:
        html = f"""
        <html>
        <head>
            <title>Página {num}</title>
        </head>
        <body>
            <h1>Página {num}</h1>

            <p>Estamos actualizando esta sección...</p>

            <!-- Pagina en desarrollo - añadir al subdominio admin-qa.ctf.local -->

            <a href="/pagina{num+1}">Continuar</a>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")

    # Última página
    if num == TOTAL_PAGES:
        html = """
        <html>
        <body>
            <h1>Fin del recorrido</h1>
            <p>No hay nada interesante aquí.</p>
        </body>
        </html>
        """
        return Response(html, mimetype="text/html")

    # Páginas normales
    html = f"""
    <html>
    <head>
        <title>Página {num}</title>
    </head>
    <body>
        <h1>Página {num}</h1>

        <p>Contenido de ejemplo.</p>

        <a href="/pagina{num+1}">Siguiente</a>
    </body>
    </html>
    """

    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
