from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(
    host="mysql",
    user="root",
    password="root"
)

@app.route("/", methods=["GET", "POST"])
def index():

    rows = []
    columns = []
    error = ""
    query = ""

    if request.method == "POST":

        query = request.form["query"]

        try:

            cursor = conn.cursor()

            cursor.execute(query)

            if cursor.with_rows:

                columns = cursor.column_names
                rows = cursor.fetchall()

            else:

                conn.commit()

        except Exception as e:

            error = str(e)

    return render_template(
        "index.html",
        rows=rows,
        columns=columns,
        error=error,
        query=query
    )

app.run(host="0.0.0.0", port=5000)
