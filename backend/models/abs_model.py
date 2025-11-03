import json
from abc import ABC
from datetime import datetime
import sqlite3


class Model(ABC):
    """Tiny abstract base for sqlite-backed models (Django-ish, no typing)."""
    table_name = ""
    pk_name = ""
    db_columns = {}      # preserves order in modern Python
    json_fields = set()  # e.g., {"raw_json", "normalized_json"}

    # ---- meta ----
    @classmethod
    def columns(cls):
        return list(cls.db_columns.keys())

    @classmethod
    def _is_autoinc_pk(cls):
        return "AUTOINCREMENT" in cls.db_columns.get(cls.pk_name, "").upper()

    # ---- DDL ----
    @classmethod
    def create_table(cls, conn):
        cols = ", ".join(f"{name} {ctype}" for name, ctype in cls.db_columns.items())
        conn.execute(f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({cols})")
        conn.commit()

    # ---- helpers ----
    @staticmethod
    def _now():
        return datetime.utcnow().isoformat()

    @classmethod
    def _serialize_for_db(cls, data):
        out = dict(data)
        for k in cls.json_fields:
            if k in out and out[k] is not None and not isinstance(out[k], str):
                out[k] = json.dumps(out[k])
        return out

    @classmethod
    def _deserialize_from_db(cls, rec):
        out = dict(rec)
        for k in cls.json_fields:
            if k in out and isinstance(out[k], str):
                try:
                    out[k] = json.loads(out[k])
                except json.JSONDecodeError:
                    pass
        return out

    # aliasing hooks (override in subclasses if needed)
    @classmethod
    def pre_save(cls, data):
        """Map external aliases (e.g., id→policy_id, value→value_json)."""
        return data

    @classmethod
    def post_load(cls, rec):
        """Add external aliases back on reads."""
        return rec

    # ---- core CRUD ----
    @classmethod
    def insert(cls, conn, **data):
        data = cls.pre_save(data)
        if "created_at" in cls.db_columns and "created_at" not in data:
            data["created_at"] = cls._now()

        autoinc = cls._is_autoinc_pk()
        cols, vals = [], []
        for c in cls.columns():
            if c == cls.pk_name and autoinc and c not in data:
                continue
            if c in data:
                cols.append(c)
                vals.append(data[c])

        payload = cls._serialize_for_db(dict(zip(cols, vals)))
        placeholders = ", ".join("?" for _ in cols)
        sql = f"INSERT INTO {cls.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
        cur = conn.cursor()
        cur.execute(sql, list(payload.values()))
        conn.commit()
        return cur.lastrowid if autoinc else data.get(cls.pk_name)

    @classmethod
    def update(cls, conn, pk, **data):
        data = cls.pre_save(data)
        if "created_at" in cls.db_columns:
            data["created_at"] = cls._now()
        data.pop(cls.pk_name, None)

        set_cols = [c for c in cls.columns() if c in data]
        if not set_cols:
            return 0

        payload = cls._serialize_for_db({c: data[c] for c in set_cols})
        set_sql = ", ".join(f"{c} = ?" for c in set_cols)
        sql = f"UPDATE {cls.table_name} SET {set_sql} WHERE {cls.pk_name} = ?"
        cur = conn.cursor()
        cur.execute(sql, list(payload.values()) + [pk])
        conn.commit()
        return cur.rowcount

    @classmethod
    def delete(cls, conn, pk):
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {cls.table_name} WHERE {cls.pk_name} = ?", (pk,))
        conn.commit()
        return cur.rowcount

    @classmethod
    def get(cls, conn, pk):
        cols = ", ".join(cls.columns())
        row = conn.execute(
            f"SELECT {cols} FROM {cls.table_name} WHERE {cls.pk_name} = ?", (pk,)
        ).fetchone()
        if not row:
            return None
        rec = dict(zip(cls.columns(), row))
        return cls.post_load(cls._deserialize_from_db(rec))

    @classmethod
    def all(cls, conn):
        cols = ", ".join(cls.columns())
        rows = conn.execute(f"SELECT {cols} FROM {cls.table_name}").fetchall()
        out = []
        for r in rows:
            rec = dict(zip(cls.columns(), r))
            out.append(cls.post_load(cls._deserialize_from_db(rec)))
        return out

    # ---- light “manager-like” helpers ----
    @classmethod
    def _map_where_to_db(cls, where):
        """
        Map external where keys via pre_save() so 'id'/'value' work.
        Only '=' comparisons supported (simple AND).
        """
        db_where = {}
        for k, v in where.items():
            # try alias mapping using pre_save on a single-field dict
            mapped = cls.pre_save({k: v})
            used = False
            for mk, mv in mapped.items():
                if mk in cls.db_columns:
                    db_where[mk] = mv
                    used = True
            if not used and k in cls.db_columns:
                db_where[k] = v
        return db_where

    @classmethod
    def filter(cls, conn, **where):
        """
        Equality-only filtering with AND (safe and minimal).
        Example: Policies.filter(conn, field="role", operator="in")
        """
        db_where = cls._map_where_to_db(where)
        cols = ", ".join(cls.columns())
        if db_where:
            conds = [f"{k} = ?" for k in db_where.keys()]
            sql = f"SELECT {cols} FROM {cls.table_name} WHERE " + " AND ".join(conds)
            params = list(db_where.values())
        else:
            sql = f"SELECT {cols} FROM {cls.table_name}"
            params = []

        rows = conn.execute(sql, params).fetchall()
        out = []
        for r in rows:
            rec = dict(zip(cls.columns(), r))
            out.append(cls.post_load(cls._deserialize_from_db(rec)))
        return out

    @classmethod
    def get_one(cls, conn, **where):
        """Return first match or None (no exceptions on multiple)."""
        matches = cls.filter(conn, **where)
        return matches[0] if matches else None

    @classmethod
    def exists(cls, conn, **where):
        return cls.get_one(conn, **where) is not None

    @classmethod
    def count(cls, conn, **where):
        db_where = cls._map_where_to_db(where)
        if db_where:
            conds = [f"{k} = ?" for k in db_where.keys()]
            sql = f"SELECT COUNT(*) FROM {cls.table_name} WHERE " + " AND ".join(conds)
            params = list(db_where.values())
        else:
            sql = f"SELECT COUNT(*) FROM {cls.table_name}"
            params = []
        row = conn.execute(sql, params).fetchone()
        return row[0] if row else 0

    @classmethod
    def delete_where(cls, conn, **where):
        db_where = cls._map_where_to_db(where)
        if not db_where:
            return 0
        conds = [f"{k} = ?" for k in db_where.keys()]
        sql = f"DELETE FROM {cls.table_name} WHERE " + " AND ".join(conds)
        cur = conn.cursor()
        cur.execute(sql, list(db_where.values()))
        conn.commit()
        return cur.rowcount

    @classmethod
    def upsert(cls, conn, **data):
        """
        Try insert; if PK conflict, update. Intended mainly for TEXT PK tables
        (e.g., Policies). Requires PK value present in data (id/alias is OK).
        """
        data = cls.pre_save(data)
        pk_val = data.get(cls.pk_name)
        try:
            return cls.insert(conn, **data)
        except sqlite3.IntegrityError:
            if pk_val is None:
                raise
            cls.update(conn, pk_val, **data)
            return pk_val
