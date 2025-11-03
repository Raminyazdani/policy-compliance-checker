# backend/db.py
import sqlite3
from pathlib import Path
from backend.models import Users, Policies

DB_PATH = Path(__file__).parent / "compliance.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def _ensure_tables(conn):
    """Single source of truth for creating tables."""
    Users.create_table(conn)
    Policies.create_table(conn)


def init_db():
    """Call this once at startup if you won't use DBManager early."""
    conn = get_conn()
    try:
        _ensure_tables(conn)
    finally:
        conn.close()


class DBManager:
    """Tiny context manager that just provides a ready connection."""
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._conn = None

    def __enter__(self):
        self._conn = sqlite3.connect(self.db_path)
        _ensure_tables(self._conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._conn is not None:
            self._conn.close()
        self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            _ensure_tables(self._conn)
        return self._conn
