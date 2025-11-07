# backend/api/upload.py
import io, json, csv
from flask import Blueprint, request, jsonify
from backend.db import DBManager
from backend.models import Policies, Users
import backend.validators as validators

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")

def _truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")

# ---------- Policies ----------
def _coerce_policy_value(op, raw):
    s = str(raw).strip()
    if op == "in":
        if s.startswith("["):
            try:
                v = json.loads(s)
                return v if isinstance(v, list) else [s]
            except Exception:
                pass
        return [x.strip() for x in s.split(",")] if s else []
    if op == "includes":
        return s
    # عدد/بولین
    try:
        if s and s.lower() not in ("true","false","null"):
            n = float(s)
            return int(n) if n.is_integer() else n
    except Exception:
        pass
    if s.lower() == "true": return True
    if s.lower() == "false": return False
    # JSON کلی
    if s.startswith("{") or s.startswith("["):
        try:
            return json.loads(s)
        except Exception:
            pass
    return raw

def _policies_from_csv(file_stream):
    text = file_stream.read().decode("utf-8", errors="ignore")
    rd = csv.DictReader(io.StringIO(text))
    items = []
    for row in rd:
        op = (row.get("operator") or "").strip()
        items.append({
            "policy_id": (row.get("policy_id") or row.get("id") or "").strip(),
            "description": (row.get("description") or "").strip(),
            "field": (row.get("field") or "").strip(),
            "operator": op,
            "value": _coerce_policy_value(op, row.get("value")),
        })
    return items

@upload_bp.post("/policies")
def upload_policies():
    """
    multipart/form-data:
      file: .json (list/object) یا .csv
      clear: اختیاری (true/1) → قبل از درج، جدول policies پاک می‌شود
    """
    if "file" not in request.files:
        return jsonify({"error": "file is required (multipart/form-data, key='file')"}), 400

    f = request.files["file"]
    clear = _truthy(request.form.get("clear"))

    try:
        if f.filename.lower().endswith(".json"):
            payload = json.load(f.stream)
            items = payload if isinstance(payload, list) else [payload]
            # سازگاری id → policy_id
            fixed = []
            for p in items:
                p = dict(p)
                if "policy_id" not in p and "id" in p:
                    p["policy_id"] = p.pop("id")
                fixed.append(p)
            validated = validators.validate_policies(fixed)
        elif f.filename.lower().endswith(".csv"):
            items = _policies_from_csv(f.stream)
            validated = validators.validate_policies(items)
        else:
            return jsonify({"error": "unsupported file type; use .json or .csv"}), 400

        with DBManager() as db:
            if clear:
                Policies.delete_all(db.conn)
            # ذخیره با upsert (کلید متنی policy_id)
            for p in validated:
                # value را به TEXT ذخیره می‌کنیم (ساده: برای غیر-رشته، JSON-string)
                v = p.get("value")
                if not isinstance(v, str):
                    try: v = json.dumps(v)
                    except Exception: v = str(v)
                Policies.upsert(
                    db.conn,
                    policy_id=p["policy_id"],
                    description=p.get("description"),
                    field=p.get("field"),
                    operator=p.get("operator"),
                    value=v,
                )
        return jsonify({"stored": len(validated), "cleared": bool(clear)}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"failed to process file: {str(e)}"}), 500

# ---------- Users ----------
def _users_from_csv(file_stream):
    text = file_stream.read().decode("utf-8", errors="ignore")
    rd = csv.DictReader(io.StringIO(text))
    out = []
    for row in rd:
        print(row)
        r = dict(row)
        # تبدیل‌های ساده
        v = (r.get("mfa_enabled") or "").strip().lower()
        if v in ("1","true","yes","y"): r["mfa_enabled"] = 1
        elif v in ("0","false","no","n"): r["mfa_enabled"] = 0
        # اعداد
        for k in ("age","age_days","login_count","income"):
            if k in r and r[k] not in (None,""):
                try:
                    r[k] = float(r[k]) if k == "income" else int(float(r[k]))
                except Exception:
                    pass
        out.append(r)
    return out

@upload_bp.post("/users")
def upload_users():
    """
    multipart/form-data:
      file: .json (list/object) یا .csv
      clear: اختیاری (true/1) → قبل از درج، جدول users پاک می‌شود
    """
    if "file" not in request.files:
        return jsonify({"error": "file is required (multipart/form-data, key='file')"}), 400

    f = request.files["file"]
    clear = _truthy(request.form.get("clear"))

    try:
        if f.filename.lower().endswith(".json"):
            payload = json.load(f.stream)
            items = payload if isinstance(payload, list) else [payload]
        elif f.filename.lower().endswith(".csv"):
            items = _users_from_csv(f.stream)
        else:
            return jsonify({"error": "unsupported file type; use .json or .csv"}), 400

        prepared = []
        for u in items:
            vu = validators.validate_user(u)   # قوانین ایمیل/پسورد و ...
            # فقط ستون‌های مدل را نگه داریم (بدون user_id)
            db_obj = {k: vu.get(k) for k in Users.db_columns.keys() if k != "user_id"}
            prepared.append(db_obj)

        with DBManager() as db:
            if clear:
                Users.delete_all(db.conn)
            for obj in prepared:
                Users.insert(db.conn, **obj)

        return jsonify({"stored": len(prepared), "cleared": bool(clear)}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"failed to process file: {str(e)}"}), 500
