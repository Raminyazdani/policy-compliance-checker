from flask import Blueprint, request, jsonify
from backend.db import DBManager
from backend.models import Users
import backend.validators as validators

users_bp = Blueprint("users", __name__)

# expose these fields in GET responses (omit password for safety)
_PUBLIC_FIELDS = [
    "user_id", "username", "name", "lastname", "email", "role",
    "mfa_enabled", "login_count", "age_days", "age", "income"
]

def _pick_public(r):
    return {k: r.get(k) for k in _PUBLIC_FIELDS if k in r}


def _prepare_db_obj(valid_user):
    """Take a validated user dict and return a DB-ready dict (may hash password)."""
    out = dict(valid_user)
    # keep only model columns
    return {k: v for k, v in out.items() if k in Users.db_columns and k != "user_id"}


@users_bp.get("/users")
def list_users():
    with DBManager() as db:
        rows = Users.all(db.conn)
    out = [_pick_public(r) for r in rows]
    return jsonify(out), 200


@users_bp.get("/users/<int:user_id>")
def get_user(user_id):
    with DBManager() as db:
        item = Users.get(db.conn, user_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(_pick_public(item)), 200


@users_bp.post("/users")
def create_users():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "missing JSON body"}), 400

    payload = data if isinstance(data, list) else [data]

    validated = []
    for u in payload:
        try:
            vu = validators.validate_user(u)   # field-level validation (includes password rules)
            validated.append(vu)
        except ValueError as e:
            return jsonify({"error": str(e), "bad_user": u}), 400

    created_ids = []
    with DBManager() as db:
        for vu in validated:
            db_obj = _prepare_db_obj(vu)
            new_id = Users.insert(db.conn, **db_obj)
            created_ids.append(new_id)

    return jsonify({"created_ids": created_ids}), 201


@users_bp.put("/users/<int:user_id>")
def put_user(user_id):
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    try:
        vu = validators.validate_user(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    with DBManager() as db:
        # ensure exists
        current = Users.get(db.conn, user_id)
        if not current:
            return jsonify({"error": "not found"}), 404

        db_obj = _prepare_db_obj(vu)
        updated = Users.update(db.conn, user_id, **db_obj)

    if updated == 0:
        return jsonify({"updated": user_id, "note": "no changes"}), 200
    return jsonify({"updated": user_id}), 200


@users_bp.patch("/users/<int:user_id>")
def patch_user(user_id):
    patch = request.get_json()
    if not isinstance(patch, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    with DBManager() as db:
        current = Users.get(db.conn, user_id)
        if not current:
            return jsonify({"error": "not found"}), 404

        # base = current (strip PK) + patch → validate
        base = {k: current.get(k) for k in Users.db_columns.keys() if k != "user_id"}
        base.update(patch)

        try:
            vu = validators.validate_user(base)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        db_obj = _prepare_db_obj(vu)
        updated = Users.update(db.conn, user_id, **db_obj)

    if updated == 0:
        return jsonify({"updated": user_id, "note": "no changes"}), 200
    return jsonify({"updated": user_id}), 200


@users_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    with DBManager() as db:
        removed = Users.delete(db.conn, user_id)
    if removed == 0:
        return jsonify({"error": "not found"}), 404
    return ("", 204)
