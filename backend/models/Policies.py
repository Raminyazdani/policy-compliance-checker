from .abs_model import Model


class Policies(Model):
    table_name = "policies"   # SQLite table name
    pk_name = "policy_id"     # primary key column
    db_columns = {
        "policy_id": "TEXT PRIMARY KEY",  # stable text PK (e.g., "mfa_required")
        "description": "TEXT",            # human-readable policy summary
        "field": "TEXT",                  # user field to check (e.g., "email")
        "operator": "TEXT",               # comparison op (==, !=, >=, <=, >, <, in, includes)
        "value": "TEXT",                  # expected value (stored as TEXT; JSON string if needed)
    }
