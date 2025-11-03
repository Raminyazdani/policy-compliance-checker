from flask import Blueprint, request, jsonify
from backend.db import DBManager
from backend.models import Users
import backend.validators as validators
import backend.utils as utils

users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
def list_users():
    with DBManager() as db:
        rows = Users.all(db.conn)
    # brief: normalized + user_id
    out = []
    for r in rows:
        norm = r.get("normalized_json") or {}
        d = dict(norm)
        d["user_id"] = r.get("user_id")
        out.append(d)
    return jsonify(out), 200


@users_bp.get("/users/<int:user_id>")
def get_user(user_id):
    with DBManager() as db:
        item = Users.get(db.conn, user_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    resp = {
        "user_id": item.get("user_id"),
        "username": item.get("username"),
        "raw": item.get("raw_json"),
        "normalized": item.get("normalized_json"),
        "created_at": item.get("created_at"),
    }
    return jsonify(resp), 200


@users_bp.post("/users")
def create_users():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "missing JSON body"}), 400

    payload = data if isinstance(data, list) else [data]

    to_store = []
    for u in payload:
        try:
            validators.validate_user(u)
            normalized = utils.normalize_user(u)
            to_store.append((u, normalized))
        except ValueError as e:
            return jsonify({"error": str(e), "bad_user": u}), 400

    created_ids = []
    with DBManager() as db:
        for raw_u, norm_u in to_store:
            new_id = Users.insert(
                db.conn,
                username=raw_u.get("username", "<unknown>"),
                raw_json=raw_u,
                normalized_json=norm_u,
            )
            created_ids.append(new_id)

    return jsonify({"created_ids": created_ids}), 201


@users_bp.put("/users/<int:user_id>")
def put_user(user_id):
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    try:
        validators.validate_user(data)
        normalized = utils.normalize_user(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    with DBManager() as db:
        # ensure exists (so 404 is meaningful)
        if not Users.get(db.conn, user_id):
            return jsonify({"error": "not found"}), 404
        updated = Users.update(
            db.conn,
            user_id,
            username=data.get("username", "<unknown>"),
            raw_json=data,
            normalized_json=normalized,
        )

    if updated == 0:
        # nothing changed; still OK
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

        merged_raw = dict(current.get("raw_json") or {})
        merged_raw.update(patch)

        try:
            validators.validate_user(merged_raw)
            merged_norm = utils.normalize_user(merged_raw)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        updated = Users.update(
            db.conn,
            user_id,
            username=merged_raw.get("username", "<unknown>"),
            raw_json=merged_raw,
            normalized_json=merged_norm,
        )

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
