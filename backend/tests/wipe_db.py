# wipe_db.py
from backend.db import DBManager

with DBManager() as db:
    cur = db.conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS policies")
    db.conn.commit()
with DBManager() as db:
    pass
print("Dropped tables: users, policies")
