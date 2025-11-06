from flask import Blueprint, jsonify, request
from backend.db import DBManager
from backend.models import Policies, Users
from backend.evaluators import evaluate_user
import json

eval_bp = Blueprint("evaluate", __name__)

def _decode_policy_value(v):
    if isinstance(v, str):
        try:
            return json.loads(v)  # handle lists/booleans/numbers stored as TEXT
        except Exception:
            return v              # keep plain strings like "@acme.com"
    return v

@eval_bp.route("/evaluate", methods=["GET", "POST"])
def run_evaluation():
    with DBManager() as db:
        # policies in evaluator shape (use policy_id; decode value if JSON)
        pols = []
        for p in Policies.all(db.conn):
            pols.append({
                "policy_id":  p.get("policy_id"),
                "description": p.get("description"),
                "field":       p.get("field"),
                "operator":    p.get("operator"),
                "value":       _decode_policy_value(p.get("value")),
            })

        # users: use direct row dicts (no normalized_json anymore)
        users = Users.all(db.conn)

    results = [evaluate_user(u, pols) for u in users]
    return jsonify(results), 200
