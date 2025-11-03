from .abs_model import Model


class Users(Model):
    table_name = "users"
    pk_name = "user_id"
    db_columns = {
        "user_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "username": "TEXT",
        "raw_json": "TEXT",
        "normalized_json": "TEXT",
        "created_at": "TEXT",
    }
    json_fields = {"raw_json", "normalized_json"}

    @classmethod
    def pre_save(cls, data):
        # allow alias id -> user_id on writes
        if "id" in data and "user_id" not in data:
            data["user_id"] = data.pop("id")
        return data

    @classmethod
    def post_load(cls, rec):
        # expose id alongside user_id on reads
        out = dict(rec)
        out["id"] = out.get("user_id")
        return out
