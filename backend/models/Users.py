from .abs_model import Model

ALLOWED_ROLES = {"admin", "analyst", "devops", "intern", "guest"}

class Users(Model):
    table_name = "users"          # SQLite table name
    pk_name = "user_id"           # primary key column
    db_columns = {
        "user_id": "INTEGER PRIMARY KEY AUTOINCREMENT",  # autoincrement PK
        "username": "TEXT",            # login handle
        "name": "TEXT",                # first/given name
        "lastname": "TEXT",            # last/family name
        "email": "TEXT",               # email address
        "role": "TEXT",                # e.g., admin/analyst/devops/guest
        "password": "TEXT",            # password
        "mfa_enabled": "INTEGER",      # boolean as 0/1
        "login_count": "INTEGER",      # total logins
        "age_days": "INTEGER",         # account age in days
        "age": "INTEGER",              # user age (years)
        "income": "REAL",              # numeric income
    }
