import re
from backend.evaluators import OPS
from backend.models import Policies
from backend.models.Users import ALLOWED_ROLES

ALLOWED_OPERATORS = set(OPS.keys())
REQUIRED_POLICY_KEYS = Policies.db_columns.keys()
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_policy(policy):
    """Validate a single policy object."""
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
    v = policy.get("value")
    if op == "in" and not isinstance(v, (list, tuple, set)):
        raise ValueError("operator 'in' requires 'value' to be a list")
    if op == "includes" and not isinstance(v, str):
        raise ValueError("operator 'includes' requires 'value' to be a string")
    return dict(policy)


def validate_policies(policies):
    """Validate a list or single policy."""
    if policies is None:
        raise ValueError("missing JSON body")
    if isinstance(policies, dict):
        policies = [policies]
    if not isinstance(policies, list):
        raise ValueError("policies must be a list of objects")
    return [validate_policy(p) for p in policies]


def validate_username(v):
    if not isinstance(v, str) or not v.strip():
        raise ValueError("username must be a non-empty string")
    return v.strip()


def validate_name(v):
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError("name must be a string")
    return v.strip()


def validate_lastname(v):
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError("lastname must be a string")
    return v.strip()


def validate_email(v):
    if v is None:
        return None
    if not isinstance(v, str) or not _EMAIL_RE.match(v.strip()):
        raise ValueError("email is not valid")
    return v.strip().lower()


def validate_role(v):
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError("role must be a string")
    role = v.strip().lower()
    if role not in ALLOWED_ROLES:
        raise ValueError(f"role must be one of {sorted(ALLOWED_ROLES)}")
    return role


def validate_password(v):
    if not isinstance(v, str):
        raise ValueError("password must be a string")
    pwd = v
    if len(pwd) < 8:
        raise ValueError("password must be at least 8 characters")
    if not any(c.islower() for c in pwd):
        raise ValueError("password must contain a lowercase letter")
    if not any(c.isupper() for c in pwd):
        raise ValueError("password must contain an uppercase letter")
    if not any(c.isdigit() for c in pwd):
        raise ValueError("password must contain a digit")
    return pwd


def _coerce_int(x, field):
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, int):
        return x
    try:
        return int(str(x).strip())
    except Exception:
        raise ValueError(f"{field} must be an integer")


def _coerce_float(x, field):
    if isinstance(x, bool):
        return float(int(x))
    if isinstance(x, (int, float)):
        return float(x)
    try:
        return float(str(x).strip())
    except Exception:
        raise ValueError(f"{field} must be a number")


def validate_mfa_enabled(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1 if v else 0
    iv = _coerce_int(v, "mfa_enabled")
    if iv not in (0, 1):
        raise ValueError("mfa_enabled must be 0 or 1")
    return iv


def validate_login_count(v):
    if v is None:
        return None
    iv = _coerce_int(v, "login_count")
    if iv < 0:
        raise ValueError("login_count must be >= 0")
    return iv


def validate_age_days(v):
    if v is None:
        return None
    iv = _coerce_int(v, "age_days")
    if iv < 0:
        raise ValueError("age_days must be >= 0")
    return iv


def validate_age(v):
    if v is None:
        return None
    iv = _coerce_int(v, "age")
    if iv < 0 or iv > 130:
        raise ValueError("age must be between 0 and 130")
    return iv


def validate_income(v):
    if v is None:
        return None
    fv = _coerce_float(v, "income")
    if fv < 0:
        raise ValueError("income must be >= 0")
    return fv


def validate_user(u):
    """Validate a single user object."""
    if not isinstance(u, dict):
        raise ValueError("user must be a JSON object")
    out = {}
    out["username"] = validate_username(u.get("username"))
    out["password"] = validate_password(u.get("password"))
    out["name"] = validate_name(u.get("name"))
    out["lastname"] = validate_lastname(u.get("lastname"))
    out["email"] = validate_email(u.get("email"))
    out["role"] = validate_role(u.get("role"))
    out["mfa_enabled"] = validate_mfa_enabled(u.get("mfa_enabled"))
    out["login_count"] = validate_login_count(u.get("login_count"))
    out["age_days"] = validate_age_days(u.get("age_days"))
    out["age"] = validate_age(u.get("age"))
    out["income"] = validate_income(u.get("income"))
    return out


def validate_users(users):
    """Validate a list or single user."""
    if users is None:
        raise ValueError("missing JSON body")
    if isinstance(users, dict):
        users = [users]
    if not isinstance(users, list):
        raise ValueError("users must be a list of objects")
    return [validate_user(u) for u in users]
