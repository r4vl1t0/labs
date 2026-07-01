from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    query = f"""
    SELECT * FROM users
    WHERE username='{username}'
    AND password='{password}'
    """

    cursor.execute(query)

    user = cursor.fetchone()

    conn.close()

    if user:
        return render_template("dashboard.html")

    return "Credenciales incorrectas",401

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002)
