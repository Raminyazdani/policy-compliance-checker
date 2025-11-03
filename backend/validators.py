from backend.evaluators import OPS
from backend.models import Policies

ALLOWED_OPERATORS = set(OPS.keys())
REQUIRED_POLICY_KEYS = Policies.db_columns.keys()


def validate_policy(policy):
    """
    Validate a single policy object in external form:
      { id, description, field, operator, value }
    """
    if not isinstance(policy, dict):
        raise ValueError("policy must be a JSON object")

    keys = set(policy.keys())
    missing = REQUIRED_POLICY_KEYS - keys
    if missing:
        raise ValueError(f"missing required keys: {sorted(missing)}")

    extra = keys - REQUIRED_POLICY_KEYS
    if extra:
        raise ValueError(f"unexpected keys: {sorted(extra)}")

    op = policy.get("operator")
    if op not in ALLOWED_OPERATORS:
        raise ValueError(f"invalid operator '{op}'. allowed: {sorted(ALLOWED_OPERATORS)}")

    # Basic type rules for operators
    if op == "in" and not isinstance(policy.get("value"), list):
        raise ValueError("operator 'in' requires 'value' to be a list")
    if op == "includes" and not isinstance(policy.get("value"), str):
        raise ValueError("operator 'includes' requires 'value' to be a string")

    return policy


def validate_policies(policies):
    """Validate a list (or single object) of policies in external form."""
    if policies is None:
        raise ValueError("missing JSON body")
    if isinstance(policies, dict):
        policies = [policies]
    if not isinstance(policies, list):
        raise ValueError("policies must be a list of objects")

    out = []
    for p in policies:
        out.append(validate_policy(p))
    return out


def validate_user(u):
    """
    Minimal user validation for evaluator input.
    (You can add stronger type checks later if needed.)
    """
    if not isinstance(u, dict):
        raise ValueError("user must be a JSON object")
    if "username" not in u:
        raise ValueError("missing username")
    return dict(u)
