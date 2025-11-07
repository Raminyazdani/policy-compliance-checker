from .app import app
from .db import init_db

def main():
    try:
        init_db()
    except Exception:
        pass
    app.run(host="127.0.0.1", port=8000, debug=True)

if __name__ == "__main__":
    main()
