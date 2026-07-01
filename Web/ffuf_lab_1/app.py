from flask import Flask, render_template, abort

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Disallow: /backup/\n",
        200,
        {"Content-Type": "text/plain"},
    )

@app.route("/mcp/message")
def mcp_message():
    return render_template("message.html")

@app.errorhandler(404)
def not_found(e):
    return "<h1>404 Not Found</h1>", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
