
OPS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b,
    "in": lambda a, b: a in b,
    "includes": lambda a, b: b in a,
}


def evaluate_user(user_obj, policies):
    """
    Check one user against all policies.

    Returns:
    {
      "username": "...",
      "overall_compliant": bool,
      "checks": [ { policy_id, description, field, operator, expected, actual, passed, note }, ... ]
    }
    """
    checks = []

    for p in policies:
        policy_id = p["policy_id"]
        desc = p["description"]
        field = p["field"]
        operator = p["operator"]
        expected = p["value"]

        actual = user_obj.get(field)
        note = ""
        passed = False

        if actual is None:
            passed = False
            note = "missing field"
        else:
            fn = OPS.get(operator)
            if fn is None:
                passed = False
                note = f"unsupported operator {operator}"
            else:
                try:
                    passed = fn(actual, expected)
                except Exception as e:
                    passed = False
                    note = f"error: {str(e)}"

        checks.append({
            "policy_id": policy_id,
            "description": desc,
            "field": field,
            "operator": operator,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "note": note,
        })

    overall_ok = all(c["passed"] for c in checks)

    return {
        "username": user_obj.get("username", "<unknown>"),
        "overall_compliant": overall_ok,
        "checks": checks,
    }
