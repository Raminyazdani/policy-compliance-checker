from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/ping")
def ping():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
