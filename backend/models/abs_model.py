from abc import ABC
from collections import OrderedDict

class Model(ABC):
    table_name = ""
    pk_name = ""
    db_columns = OrderedDict()  # preserves insertion order

    # ---- meta ----
    @classmethod
    def columns(cls):
        return list(cls.db_columns.keys())

    # ---- DDL ----
    @classmethod
    def create_table(cls, conn):
        cols = ", ".join(f"{name} {ctype}" for name, ctype in cls.db_columns.items())
        conn.execute(f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({cols})")
        conn.commit()

    # ---- core CRUD ----
    @classmethod
    def insert(cls, conn, **data):
        cols = [c for c in cls.columns() if c in data]
        if not cols:
            raise ValueError("no data to insert")
        vals = [data[c] for c in cols]

        placeholders = ", ".join("?" for _ in cols)
        sql = f"INSERT INTO {cls.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
        cur = conn.cursor()
        cur.execute(sql, vals)
        conn.commit()

        # return provided PK (e.g., TEXT PK) if present; else autoincrement id
        return data.get(cls.pk_name, cur.lastrowid)

    @classmethod
    def update(cls, conn, pk, **data):
        if pk is None:
            raise ValueError("pk is required")
        data.pop(cls.pk_name, None)  # never update PK in SET

        set_cols = [c for c in cls.columns() if c in data]
        if not set_cols:
            return 0

        set_sql = ", ".join(f"{c} = ?" for c in set_cols)
        sql = f"UPDATE {cls.table_name} SET {set_sql} WHERE {cls.pk_name} = ?"
        params = [data[c] for c in set_cols] + [pk]

        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount

    @classmethod
    def delete(cls, conn, pk):
        if pk is None:
            raise ValueError("pk is required")
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
        return dict(zip(cls.columns(), row))

    @classmethod
    def all(cls, conn):
        cols = ", ".join(cls.columns())
        rows = conn.execute(f"SELECT {cols} FROM {cls.table_name}").fetchall()
        return [dict(zip(cls.columns(), r)) for r in rows]
