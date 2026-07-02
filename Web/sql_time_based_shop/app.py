from flask import Flask, render_template, request
import mysql.connector
import time

app = Flask(__name__)

conn = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root",
    database="shop"
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def products():

    search = request.args.get("search", "")

    cursor = conn.cursor()

    # VULNERABLE TIME BASED SQLi
    query = f"""
    SELECT name, price
    FROM products
    WHERE name LIKE '%{search}%'
    """

    start = time.time()

    try:
        cursor.execute(query)
        results = cursor.fetchall()

    except:
        results = []

    end = time.time()

    # simulamos respuesta uniforme (no leaks)
    time.sleep(0)

    return render_template(
        "index.html",
        products=results,
        query=search,
        delay=round(end - start, 2)
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
