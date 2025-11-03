from .abs_model import Model


class Policies(Model):
    table_name = "policies"
    pk_name = "policy_id"
    db_columns = {
        "policy_id": "TEXT PRIMARY KEY",
        "description": "TEXT",
        "field": "TEXT",
        "operator": "TEXT",
        "value_json": "TEXT",
        "created_at": "TEXT",
    }
    json_fields = {"value_json"}

    @classmethod
    def pre_save(cls, data):
        # accept id -> policy_id, value -> value_json on writes
        d = dict(data)
        if "id" in d and "policy_id" not in d:
            d["policy_id"] = d.pop("id")
        if "value" in d and "value_json" not in d:
            d["value_json"] = d.pop("value")
        return d

    @classmethod
    def post_load(cls, rec):
        # expose id and value on reads
        out = dict(rec)
        out["id"] = out.get("policy_id")
        if "value_json" in out and "value" not in out:
            out["value"] = out["value_json"]
        return out
