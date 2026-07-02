from flask import Flask, render_template, request
import mysql.connector

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

    query = f"""
    SELECT name, price
    FROM products
    WHERE name LIKE '%{search}%'
    """

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            return render_template("index.html", products=results, query=search)
        else:
            return render_template("index.html", products=[], query=search)

    except:
        # IMPORTANTE: no mostrar errores → blind SQLi
        return render_template("index.html", products=[], query=search)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
