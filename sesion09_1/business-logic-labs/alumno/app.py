import os
import sqlite3
import secrets
import datetime
from flask import Flask, request, redirect, url_for, render_template, session as flask_session, g, jsonify

APP_NAME = "TiendaCorp"
DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

PRODUCT_PRICE = 39.99
COUPON_CODE = "DESCUENTO8"
COUPON_DISCOUNT = 8  # porcentaje

FLAG = "FLAG{alumno_cadena_l0gica_neg0cio_r7m4t}"

# Usuario cuyas credenciales estan expuestas en el javascript de la aplicacion
LEAKED_USERNAME = "alumno_test"
LEAKED_PASSWORD = "Cl4veAlumno#2026"

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ---------------------------------------------------------------------------
# Manejo de sesiones "manual" (tabla en memoria) para que el robo de cookie
# via XSS sea directamente reproducible (sin firmar/cifrar el valor).
# ---------------------------------------------------------------------------
SESSIONS = {}  # token -> {"user_id": int, "is_admin": bool}


def create_session(user_id, is_admin):
    token = secrets.token_hex(20)
    SESSIONS[token] = {"user_id": user_id, "is_admin": bool(is_admin)}
    return token


def get_current_session():
    token = request.cookies.get("labsession")
    if not token:
        return None
    return SESSIONS.get(token)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            display_name TEXT NOT NULL,
            wallet REAL NOT NULL,
            photo_caption TEXT NOT NULL DEFAULT '',
            is_admin INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            amount_paid REAL NOT NULL,
            card_last4 TEXT NOT NULL,
            created_at TEXT NOT NULL,
            internal_note TEXT
        );

        CREATE TABLE captured_cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie_value TEXT NOT NULL,
            source_ip TEXT,
            created_at TEXT NOT NULL
        );
        """
    )
    now = datetime.datetime.utcnow().isoformat()
    db.execute(
        "INSERT INTO users (username, password, display_name, wallet, photo_caption, is_admin) VALUES (?,?,?,?,?,1)",
        ("admin", secrets.token_hex(12), "Administrador de Plataforma", 999999.0, "Cuenta oficial de administracion."),
    )
    db.execute(
        "INSERT INTO users (username, password, display_name, wallet, photo_caption, is_admin) VALUES (?,?,?,?,?,0)",
        (LEAKED_USERNAME, LEAKED_PASSWORD, "Cristiano R.", 15.00, "Fan del futbol."),
    )
    # Comprobante interno del admin (bóveda) - id 1
    db.execute(
        "INSERT INTO purchases (user_id, product_name, amount_paid, card_last4, created_at, internal_note) VALUES (1, 'Boveda Interna', 0, '0000', ?, ?)",
        (now, FLAG),
    )
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if get_current_session():
        return redirect(url_for("shop"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
        ).fetchone()
        if user:
            token = create_session(user["id"], user["is_admin"])
            resp = redirect(url_for("shop"))
            resp.set_cookie("labsession", token, httponly=False)
            return resp
        error = "Usuario o contrasena incorrectos."
    return render_template("login.html", error=error, app_name=APP_NAME,
                            leaked_username=LEAKED_USERNAME, leaked_password=LEAKED_PASSWORD)


@app.route("/logout")
def logout():
    token = request.cookies.get("labsession")
    if token in SESSIONS:
        del SESSIONS[token]
    resp = redirect(url_for("login"))
    resp.delete_cookie("labsession")
    return resp


def require_login():
    sess = get_current_session()
    if not sess:
        return None
    return sess


@app.route("/shop")
def shop():
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (sess["user_id"],)).fetchone()
    if "cart_total" not in flask_session:
        flask_session["cart_total"] = PRODUCT_PRICE
    return render_template(
        "shop.html",
        app_name=APP_NAME,
        user=user,
        product_price=PRODUCT_PRICE,
        cart_total=round(flask_session["cart_total"], 2),
        coupon_code_hint=None,
    )


@app.route("/apply_coupon", methods=["POST"])
def apply_coupon():
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    code = request.form.get("code", "").strip()
    if "cart_total" not in flask_session:
        flask_session["cart_total"] = PRODUCT_PRICE
    if code == COUPON_CODE:
        # VULNERABILIDAD: no se valida si el cupon ya fue aplicado antes,
        # por lo que cada request vuelve a descontar sobre el total actual.
        flask_session["cart_total"] = round(flask_session["cart_total"] * (1 - COUPON_DISCOUNT / 100), 2)
        flask_session.modified = True
    return redirect(url_for("shop"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (sess["user_id"],)).fetchone()
    total = round(flask_session.get("cart_total", PRODUCT_PRICE), 2)
    error = None
    if request.method == "POST":
        card_number = request.form.get("card_number", "")
        if total > user["wallet"]:
            error = f"Fondos insuficientes. Tu saldo disponible es ${user['wallet']:.2f}"
        elif len(card_number) < 4:
            error = "Numero de tarjeta invalido."
        else:
            now = datetime.datetime.utcnow().isoformat()
            cur = db.execute(
                "INSERT INTO purchases (user_id, product_name, amount_paid, card_last4, created_at) VALUES (?,?,?,?,?)",
                (user["id"], "Suscripcion Premium", total, card_number[-4:], now),
            )
            db.execute("UPDATE users SET wallet = wallet - ? WHERE id=?", (total, user["id"]))
            db.commit()
            new_id = cur.lastrowid
            flask_session["cart_total"] = PRODUCT_PRICE
            return redirect(url_for("voucher", voucher_id=new_id))
    return render_template("checkout.html", app_name=APP_NAME, total=total, error=error)


@app.route("/voucher/<int:voucher_id>")
def voucher(voucher_id):
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    db = get_db()
    # VULNERABILIDAD IDOR: no se valida que el comprobante pertenezca al usuario autenticado.
    purchase = db.execute("SELECT * FROM purchases WHERE id=?", (voucher_id,)).fetchone()
    if not purchase:
        return render_template("voucher.html", app_name=APP_NAME, purchase=None, buyer=None, show_internal=False)
    buyer = db.execute("SELECT * FROM users WHERE id=?", (purchase["user_id"],)).fetchone()
    show_internal = bool(sess.get("is_admin")) and purchase["internal_note"]
    return render_template(
        "voucher.html",
        app_name=APP_NAME,
        purchase=purchase,
        buyer=buyer,
        show_internal=show_internal,
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (sess["user_id"],)).fetchone()
    if request.method == "POST":
        caption = request.form.get("photo_caption", "")
        # VULNERABILIDAD: no se sanitiza ni se escapa este campo al renderizarlo despues.
        db.execute("UPDATE users SET photo_caption=? WHERE id=?", (caption, user["id"]))
        db.commit()
        user = db.execute("SELECT * FROM users WHERE id=?", (sess["user_id"],)).fetchone()
    return render_template("profile.html", app_name=APP_NAME, user=user)


@app.route("/profile/<username>")
def public_profile(username):
    sess = require_login()
    if not sess:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    return render_template("public_profile.html", app_name=APP_NAME, user=user)


@app.route("/collect")
def collect():
    cookie_value = request.args.get("c", "")
    now = datetime.datetime.utcnow().isoformat()
    db = get_db()
    db.execute(
        "INSERT INTO captured_cookies (cookie_value, source_ip, created_at) VALUES (?,?,?)",
        (cookie_value, request.remote_addr, now),
    )
    db.commit()
    return ("", 204)


@app.route("/debug/captured")
def debug_captured():
    db = get_db()
    rows = db.execute("SELECT * FROM captured_cookies ORDER BY id DESC").fetchall()
    return render_template("debug_captured.html", app_name=APP_NAME, rows=rows)


@app.route("/internal/_bot_credentials")
def internal_bot_credentials():
    # Solo accesible desde dentro del propio contenedor (el bot admin),
    # nunca expuesto a traves del puerto publicado en el host.
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return jsonify({"error": "forbidden"}), 403
    db = get_db()
    row = db.execute("SELECT password FROM users WHERE username='admin'").fetchone()
    return jsonify({"password": row["password"]})


@app.route("/internal/latest_id")
def internal_latest_id():
    db = get_db()
    row = db.execute("SELECT MAX(id) as m FROM purchases WHERE id > 1").fetchone()
    return jsonify({"id": row["m"]})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
