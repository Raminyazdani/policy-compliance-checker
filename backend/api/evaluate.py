from flask import Blueprint, jsonify, request
from backend.db import DBManager
from backend.models import Policies, Users
from backend.evaluators import evaluate_user

eval_bp = Blueprint("evaluate", __name__)

@eval_bp.route("/evaluate", methods=["GET", "POST"])
def run_evaluation():
    with DBManager() as db:
        # policies in external evaluator shape
        pols = []
        for p in Policies.all(db.conn):
            pols.append({
                "id": p.get("id"),
                "description": p.get("description"),
                "field": p.get("field"),
                "operator": p.get("operator"),
                "value": p.get("value"),
            })
        # normalized users
        users = [u.get("normalized_json") for u in Users.all(db.conn)]

    results = [evaluate_user(u, pols) for u in users]
    return jsonify(results), 200
