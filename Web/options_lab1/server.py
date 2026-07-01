from flask import Flask, request, jsonify, send_from_directory

import hashlib

app = Flask(__name__)

usuarios = []


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/gestion_usuario", methods=["POST","GET","DELETE","OPTIONS"])
def gestion():

    if request.method == "OPTIONS":

        r = app.make_default_options_response()

        r.headers["Allow"] = "GET, POST, DELETE, OPTIONS"

        return r

    if request.method == "POST":

        data = request.get_json()

        usuario = data["usuario"]

        usuarios.append(usuario)

        return jsonify({
            "mensaje":"Usuario creado",
            "usuario":usuario
        })

    if request.method == "GET":

        return jsonify(usuarios)

    if request.method == "DELETE":

        usuario = request.args.get("usuario")

        if usuario in usuarios:

            usuarios.remove(usuario)

            flag = 'GOOD_JOB'

            return jsonify({
                "mensaje":"Usuario eliminado",
                "flag":flag
            })

        return jsonify({
            "error":"No existe"
        }),404


if __name__=="__main__":
    app.run(debug=True)
