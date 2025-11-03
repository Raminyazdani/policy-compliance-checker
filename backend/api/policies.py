from flask import Blueprint, request, jsonify
from backend.db import DBManager
from backend.models import Policies
import backend.validators as validators

policies_bp = Blueprint("policies", __name__)


@policies_bp.get("/policies")
def list_policies():
    with DBManager() as db:
        items = Policies.all(db.conn)
    # return a minimal, evaluator-friendly shape
    out = []
    for r in items:
        out.append({
            "id": r.get("id"),
            "description": r.get("description"),
            "field": r.get("field"),
            "operator": r.get("operator"),
            "value": r.get("value"),
        })
    return jsonify(out), 200


@policies_bp.get("/policies/<policy_id>")
def get_policy(policy_id):
    with DBManager() as db:
        item = Policies.get(db.conn, policy_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    # expose a tidy object
    resp = {
        "id": item.get("id"),
        "description": item.get("description"),
        "field": item.get("field"),
        "operator": item.get("operator"),
        "value": item.get("value"),
        "created_at": item.get("created_at"),
    }
    return jsonify(resp), 200


@policies_bp.post("/policies")
def create_policies():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "missing JSON body"}), 400

    payload = data if isinstance(data, list) else [data]

    validated = []
    for p in payload:
        try:
            validated.append(validators.validate_policy(p))
        except ValueError as e:
            return jsonify({"error": str(e), "bad_policy": p}), 400

    with DBManager() as db:
        for p in validated:
            Policies.upsert(db.conn, **p)  # TEXT PK upsert

    return jsonify({"stored": len(validated)}), 201


@policies_bp.put("/policies/<policy_id>")
def put_policy(policy_id):
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "body must be a JSON object"}), 400
    try:
        obj = validators.validate_policy(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    obj["id"] = policy_id  # path is source of truth

    with DBManager() as db:
        Policies.upsert(db.conn, **obj)

    return jsonify({"updated": policy_id}), 200


@policies_bp.patch("/policies/<policy_id>")
def patch_policy(policy_id):
    patch = request.get_json()
    if not isinstance(patch, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    with DBManager() as db:
        current = Policies.get(db.conn, policy_id)
        if not current:
            return jsonify({"error": "not found"}), 404

        allowed = {"description", "field", "operator", "value"}
        merged = {**current, **{k: v for k, v in patch.items() if k in allowed}}

        try:
            merged_valid = validators.validate_policy(merged)
            merged_valid["id"] = policy_id
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        Policies.upsert(db.conn, **merged_valid)

    return jsonify({"updated": policy_id}), 200


@policies_bp.delete("/policies/<policy_id>")
def delete_policy(policy_id):
    with DBManager() as db:
        removed = Policies.delete(db.conn, policy_id)
    if removed == 0:
        return jsonify({"error": "not found"}), 404
    return ("", 204)
