from flask import Blueprint, request, jsonify
from backend.db import DBManager
from backend.models import Policies
import backend.validators as validators
import json

policies_bp = Blueprint("policies", __name__)

# --- tiny helpers to map external<->DB and handle value JSON ---
def _to_db_policy(p):
    """external -> DB shape"""
    v = p.get("value")
    if not isinstance(v, str):
        try:
            v = json.dumps(v)
        except Exception:
            v = str(v)
    return {
        "policy_id": p.get("policy_id"),
        "description": p.get("description"),
        "field": p.get("field"),
        "operator": p.get("operator"),
        "value": v,
    }

def _from_db_policy(r):
    """DB -> external shape"""
    v = r.get("value")
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            # keep raw string (e.g., "@acme.com")
            pass
    return {
        "id": r.get("policy_id"),
        "description": r.get("description"),
        "field": r.get("field"),
        "operator": r.get("operator"),
        "value": v,
    }

def _save_policy(conn, db_obj):
    """minimal upsert without adding Model.upsert"""
    existing = Policies.get(conn, db_obj["policy_id"])
    if existing:
        Policies.update(conn, db_obj["policy_id"], **db_obj)
        return "updated"
    else:
        Policies.insert(conn, **db_obj)
        return "inserted"


@policies_bp.get("/policies")
def list_policies():
    with DBManager() as db:
        items = Policies.all(db.conn)  # DB shape
    out = [_from_db_policy(r) for r in items]
    return jsonify(out), 200


@policies_bp.get("/policies/<policy_id>")
def get_policy(policy_id):
    with DBManager() as db:
        item = Policies.get(db.conn, policy_id)  # DB shape
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(_from_db_policy(item)), 200


@policies_bp.post("/policies")
def create_policies():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "missing JSON body"}), 400

    payload = data if isinstance(data, list) else [data]

    validated = []
    for p in payload:
        try:
            validated.append(validators.validate_policy(p))  # external shape
        except ValueError as e:
            return jsonify({"error": str(e), "bad_policy": p}), 400

    with DBManager() as db:
        for p in validated:
            db_obj = _to_db_policy(p)
            _save_policy(db.conn, db_obj)

    return jsonify({"stored": len(validated)}), 201


@policies_bp.put("/policies/<policy_id>")
def put_policy(policy_id):
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    try:
        obj = validators.validate_policy(data)  # external shape
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    obj["id"] = policy_id  # path is source of truth
    db_obj = _to_db_policy(obj)

    with DBManager() as db:
        _save_policy(db.conn, db_obj)

    return jsonify({"updated": policy_id}), 200


@policies_bp.patch("/policies/<policy_id>")
def patch_policy(policy_id):
    patch = request.get_json()
    if not isinstance(patch, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    with DBManager() as db:
        current = Policies.get(db.conn, policy_id)  # DB shape
        if not current:
            return jsonify({"error": "not found"}), 404

        # build external base from DB, then merge allowed patch keys
        base_ext = _from_db_policy(current)
        allowed = {"description", "field", "operator", "value"}
        merged_ext = {**base_ext, **{k: v for k, v in patch.items() if k in allowed}}

        try:
            merged_valid = validators.validate_policy(merged_ext)  # external
            merged_valid["id"] = policy_id
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        db_obj = _to_db_policy(merged_valid)
        _save_policy(db.conn, db_obj)

    return jsonify({"updated": policy_id}), 200


@policies_bp.delete("/policies/<policy_id>")
def delete_policy(policy_id):
    with DBManager() as db:
        removed = Policies.delete(db.conn, policy_id)
    if removed == 0:
        return jsonify({"error": "not found"}), 404
    return ("", 204)
