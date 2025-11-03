from flask import Flask
from backend.db import init_db
from backend.api import register_blueprints


def create_app():
    app = Flask(__name__)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    init_db()  # ensure tables once at startup
    app.run(host="127.0.0.1", port=8000, debug=True)
