# Policy Compliance Checker (FReMP)

A small **FReMP** stack web app (**Flask + React + SQLite**) that evaluates user accounts against **dynamic** security policies. 
Policies and users can be uploaded as JSON or CSV, results are computed on the server, and a rich React UI shows a filterable, exportable table of all checks.

---

## Contents
- [Scenario & Goals](#scenario--goals)
- [Features](#features)
- [Architecture](#architecture)
- [Directory Layout](#directory-layout)
- [Data Model](#data-model)
- [API](#api)
  - [Health](#health)
  - [Policies](#policies)
  - [Users](#users)
  - [Evaluate](#evaluate)
  - [Upload](#upload)
- [Policy Semantics](#policy-semantics)
- [Validation Rules](#validation-rules)
- [Frontend (React)](#frontend-react)
- [Running Locally](#running-locally)
  - [Backend (Flask)](#backend-flask)
  - [Frontend (React--vite)](#frontend-react--vite)
- [Sample Payloads](#sample-payloads)
- [Implementation Steps (Build Log)](#implementation-steps-build-log)
- [Design Notes & Trade-offs](#design-notes--trade-offs)
- [Future Work / Alternative Directions](#future-work--alternative-directions)
- [Testing Utilities](#testing-utilities)
- [Conventions](#conventions)
- [License](#license)

---

## Scenario & Goals

**Scenario:** An organization needs to track how well users comply with a set of policies. Policies are **dynamic** and may change over time.

**Goals (assignment):**
1. Accept a set of policies in JSON.
2. Accept user data as JSON or CSV.
3. Dynamically evaluate each user against all policies.
4. Display results in a table (React).
5. Keep the code **modular, clean, readable**, and focused on correctness.

**Bonus implemented:**
- Interactive UI to upload users/policies (JSON or CSV).
- Sorting and **multi-select filtering** in the results table (by user and policy).
- **CSV export** for the evaluate table.

---

## Features

- **Dynamic policies** with operators: `==`, `!=`, `>=`, `<=`, `>`, `<`, `in`, `includes`.
- **Upload** users and policies via JSON or CSV (server validates and stores them in SQLite).
- **Strict validation**: users (password strength, email format, numeric/boolean coercions), policies (shape and operator/value consistency).
- **Evaluator** computes per-user check results; missing fields yield a failed check with a note.
- **React UI** (MUI + DataGrid + Zustand) with dynamic columns (no hard-coded table schema), multi-select filters, and CSV export.
- **Minimal model layer**: tiny `abs_model.py` providing CRUD + `upsert` + `delete_all` without heavyweight ORM.

---

## Architecture

Request flow:
1. Client uploads **policies** and **users** (JSON/CSV) → persisted in SQLite.
2. Client calls `/evaluate` → backend loads users + policies and computes results.
3. Frontend renders a flattened **check list** (one row per user-policy check) with filters and export.

---

## Directory Layout

```
root
├─ backend/
│  ├─ app.py                     # Flask app entry (factory + run)
│  ├─ db.py                      # DBManager, init, connection helpers
│  ├─ evaluators.py              # Policy evaluation engine
│  ├─ validators.py              # Strong validation for policies/users
│  ├─ models/
│  │  ├─ abs_model.py            # Minimal base model (CRUD, upsert, delete_all)
│  │  ├─ Users.py                # Users schema
│  │  └─ Policies.py             # Policies schema
│  └─ api/
│     ├─ __init__.py             # Blueprint registration (mounted under /api)
│     ├─ health.py               # GET /api/ping
│     ├─ policies.py             # CRUD /api/policies
│     ├─ users.py                # CRUD /api/users
│     ├─ evaluate.py             # GET/POST /api/evaluate
│     └─ upload.py               # POST /api/upload/{users|policies} (JSON/CSV, optional clear)
│
├─ data/
│  └─ compliance.db              # SQLite database (generated at runtime)
│
└─ frontend/
   ├─ src/
   │  ├─ api/http.js             # HTTP helper (JSON + FormData) with API_BASE=/api
   │  ├─ app/AppShell.jsx        # App chrome (top tabs + bottom nav on mobile)
   │  ├─ App.jsx                 # Tab switcher (Policies | Users | Evaluate)
   │  ├─ components/layout/*     # Section, Row, Col, Heading, Toolbar, Body
   │  ├─ components/table/
   │  │  ├─ DataTable.jsx        # MUI DataGrid wrapper + paging
   │  │  └─ inferColumns.jsx     # Dynamic column inference from row data
   │  ├─ features/
   │  │  ├─ policies/*           # Policies panel + form
   │  │  ├─ users/*              # Users panel + form
   │  │  └─ evaluate/*           # Evaluate panel (filters, export CSV)
   │  ├─ store/createStore.js    # Zustand store helper
   │  ├─ theme.js, main.jsx, *.css
   └─ package.json
```

---

## Data Model

### Users
Columns (all optional unless noted):
- `user_id` (INTEGER PK, auto)
- `username` **(required)**
- `password` **(required)** (validated: length ≥ 8, uppercase, lowercase, digit)
- `name`, `lastname`
- `email` (validated with regex)
- `role`
- `mfa_enabled` (0/1)
- `login_count` (int ≥ 0)
- `age_days` (int ≥ 0)
- `age` (0–130)
- `income` (float ≥ 0)

### Policies
Columns:
- `policy_id` (TEXT PK)
- `description` (TEXT)
- `field` (user field to check)
- `operator` (`==`, `!=`, `>=`, `<=`, `>`, `<`, `in`, `includes`)
- `value` (TEXT; for `in`, a list; for `includes`, a string)

> Note: Internally the model stores `value` as TEXT; for `in` it expects a JSON-encoded list. The upload and UI helpers coerce values appropriately.

---

## API

All endpoints are mounted under the prefix **`/api`**.

### Health
- `GET /api/ping` → `{ "status": "ok" }`

### Policies
- `GET /api/policies` → list of policies
- `GET /api/policies/<policy_id>` → single policy
- `POST /api/policies` → create (one or many). Body may be a single object or a list.
- `PUT /api/policies/<policy_id>` → replace (upsert)
- `PATCH /api/policies/<policy_id>` → partial update
- `DELETE /api/policies/<policy_id>` → delete

**Policy JSON shape (external):**
```json
{
  "policy_id": "age_min",
  "description": "Age must be >= 18",
  "field": "age",
  "operator": ">=",
  "value": 18
}
```
For `in`, `value` should be a list (e.g., `["admin","devops"]`).  
For `includes`, `value` should be a string (e.g., `"@company.com"`).

### Users
- `GET /api/users` → list of users
- `GET /api/users/<user_id>` → single user
- `POST /api/users` → create (one or many)
- `PUT /api/users/<user_id>` → replace
- `PATCH /api/users/<user_id>` → partial update
- `DELETE /api/users/<user_id>` → delete

**User JSON shape (example):**
```json
{
  "username": "alice",
  "password": "Alic3pass!",
  "email": "alice@example.com",
  "role": "admin",
  "mfa_enabled": 1,
  "age": 29,
  "income": 85000
}
```

### Evaluate
- `GET /api/evaluate` (also supports `POST`) → array of per-user results
```json
[
  {
    "username": "alice",
    "overall_compliant": true,
    "checks": [
      {
        "policy_id": "age_min",
        "description": "Age must be >= 18",
        "field": "age",
        "operator": ">=",
        "expected": 18,
        "actual": 29,
        "passed": true,
        "note": ""
      }
    ]
  }
]
```

### Upload
Supports JSON or CSV via `multipart/form-data` with a `file` field. Optional `clear=1` to wipe the target table before import.

- `POST /api/upload/users`
- `POST /api/upload/policies`

**Examples:**
```bash
# Policies JSON
curl -F "file=@policies.json" -F "clear=1" http://localhost:8000/api/upload/policies

# Users CSV
curl -F "file=@users.csv" -F "clear=1" http://localhost:8000/api/upload/users
```

**CSV parsing rules (server):**
- Header names must match field names (e.g., `username,email,age,...`).
- `in` values can be provided as a JSON array (e.g., `["admin","devops"]`) or as a comma-separated string which the UI helper can coerce for you.
- Booleans normalized to 0/1; numbers coerced if possible.

---

## Policy Semantics

Operators:
- `==`, `!=`, `>=`, `<=`, `>`, `<` → numeric/string comparisons as-is.
- `in` → checks if `user[field]` is in `value` (list).
- `includes` → checks if **`value`** (string) is a substring of `user[field]`.

Behavior details:
- **Missing field:** the check **fails** with `note = "missing field"`.
- **Unsupported operator:** the check fails with `note = "unsupported operator ..."`. 

---

## Validation Rules

### User validation (subset)
- **username**: non-empty string
- **password**: ≥ 8 chars, contains uppercase, lowercase, and digit
- **email**: regex-validated (`something@domain`)
- Numeric fields (`age`, `age_days`, `login_count`, `income`): coerced and range-checked as needed
- **mfa_enabled**: normalized to `0` or `1`

### Policy validation
- Must contain required keys: `policy_id`, `description`, `field`, `operator`, `value`
- Operator must be one of: `==`, `!=`, `>=`, `<=`, `>`, `<`, `in`, `includes`
- `in` requires `value` to be a list; `includes` requires a string

---

## Frontend (React)

- **MUI v5** for layout and components
- **@mui/x-data-grid** for large, virtualized tables
- **Zustand** for a tiny predictable state store
- **Dynamic columns** via `inferColumns()` so the UI adapts to schema changes
- **Evaluate** panel flattens per-user checks (one row per check), with multi-select filters by **policy** and **user**, plus **CSV export**

---

## Running Locally

### Backend (Flask)

Requirements: **Python 3.10+**

1) Create and activate a virtual environment:
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts ctivate
# macOS/Linux:
source .venv/bin/activate
```

2) Install dependencies:
```bash
pip install flask
# or if you maintain a requirements file:
# pip install -r requirements.txt
```

3) Run the server (choose one):
```bash
# Simple
python backend/app.py

# Flask CLI with app factory
# Windows PowerShell:
$env:FLASK_APP="backend.app:create_app"
flask run --port 8000
# macOS/Linux:
export FLASK_APP="backend.app:create_app"
flask run --port 8000
```

Backend listens on **http://127.0.0.1:8000** and mounts all endpoints under **/api**.  
The SQLite DB is created at **data/compliance.db** on first run.

### Frontend (React–Vite)

Requirements: **Node 18+**

```bash
cd frontend
npm install
npm run dev
```

Frontend serves at **http://127.0.0.1:5173** and calls the backend at `/api`.  
If your backend is not the same origin, configure a Vite proxy or adjust `src/api/http.js`.

---

## Sample Payloads

**Policies (`policies.json`)**
```json
[
  { "policy_id":"age_min", "description":"Age >= 18", "field":"age", "operator":">=", "value":18 },
  { "policy_id":"email_domain", "description":"Company email", "field":"email", "operator":"includes", "value":"@company.com" },
  { "policy_id":"role_allowed", "description":"Role in set", "field":"role", "operator":"in", "value":["admin","devops","security"] }
]
```

**Users (`users.csv`)**
```csv
username,password,email,role,mfa_enabled,login_count,age_days,age,income
alice,Alic3pass!,alice@company.com,admin,1,12,400,29,85000
bob,Bob12345!,bob@gmail.com,user,0,3,90,22,42000
```

Evaluate:
```bash
curl http://localhost:8000/api/evaluate
```

---

## Implementation Steps (Build Log)

1. **Data layer** — implemented a minimal `Model` base with `insert/update/delete/get/all`, plus `upsert` and `delete_all`. Added concrete `Users` and `Policies` models.
2. **Validation & evaluator** — strict validators for users and policies; compact evaluator covering the base operator set.
3. **API** — blueprints for health, users, policies, evaluate, and upload; clean, RESTful shapes and consistent error handling.
4. **Upload** — JSON/CSV import (`multipart/form-data`) with optional `clear=1` per target; simple coercion for `in`/`includes`.
5. **Frontend** — MUI shell, dynamic tables, panels for users/policies, evaluate with multi-select filters and CSV export.
6. **Polish** — consistent responses; stable row ids; small UX touches.

---

## Design Notes & Trade-offs

- **Minimal, explicit model layer** keeps the learning curve low while enforcing a consistent access pattern (no ORM).
- **Operators kept small** for safety, explainability, and testability.
- **Value coercion** for common policy shapes simplifies editing (e.g., list parsing for `in`).
- **Dynamic UI columns** via inference avoids drift when schemas evolve.

---

## Future Work / Alternative Directions

### 1) Function-style operators (e.g., `len`, transforms)
**Goal:** Support expressions such as `len(password) >= 12`, `lower(email) includes "@company.com"`.

- **Derived fields (preprocessing):** add a normalization step that enriches user objects (e.g., `password_length`, `email_lower`). The existing operator set remains unchanged. Lowest effort and very safe.
- **Expression mini-language:** allow limited function calls in `field` or `value` (whitelist: `len`, `lower`, `upper`, `regex_match`). Parse to AST, evaluate without `eval`, then apply the standard operator. Example:
  ```json
  { "policy_id":"pw_len_min", "description":"Password length >= 12",
    "field":"len(password)", "operator":">=", "value":12 }
  ```

### 2) Nested rules with AND/OR
**Goal:** Policy groups with boolean logic, including nested groups.

**Schema:** Replace `field/operator/value` with `rules` and `logic`:
```json
{
  "policy_id":"complex_example",
  "description":"(age >= 18 AND role in [...]) OR email includes @company.com",
  "logic":"OR",
  "rules":[
    {
      "logic":"AND",
      "rules":[
        { "field":"age", "operator":">=", "value":18 },
        { "field":"role", "operator":"in", "value":["admin","security"] }
      ]
    },
    { "field":"email", "operator":"includes", "value":"@company.com" }
  ]
}
```
Evaluation recursively processes groups and short-circuits, keeping leaf clauses simple.

### 3) Database-free “Ad-hoc Evaluation” mode
**Goal:** Web workflow that does **not persist** any data. Users provide a CSV/JSON of users (possibly with new columns) and a policy JSON with a minimal rule set; the system returns results immediately.

- **Server-based temporary endpoint:** `POST /api/eval/adhoc` accepts `users` (CSV/JSON) + `policies` (JSON), normalizes in memory, evaluates with the same engine, and returns results without touching SQLite. Useful for medium payloads, reuses server-side validators/evaluator.
- **Fully client-side (small data):** read CSV/JSON in the browser, run a shared evaluator module, render results and allow export—no server round trip. Useful for quick checks and demos.

**Minimal implementation now:** add only one endpoint `POST /api/eval/adhoc` that returns the same shape as `/api/evaluate`, reusing existing normalization and evaluator logic, but skipping persistence.

---

## Testing Utilities

Located under `backend/tests/` (examples):
- `wipe_db.py` — drops `users` and `policies` tables using the DB manager.
- `populate_db.py` — POSTS sample users/policies to the API (requires `requests`).
- `evaluate_db.py` — calls `/api/evaluate` and prints/saves the response.
- `restart.py` — sequentially runs wipe → populate → evaluate.
  
> Ensure `requests` is installed in the backend venv if you use these helpers:
> ```bash
> pip install requests
> ```
> Also ensure the backend is running at `http://127.0.0.1:8000` before running the test scripts.

---

## Conventions

- **Coding style:** small, explicit modules; minimal comments; clear naming.
- **Commit style (example):**  
  `Ramin | policy-compliance-checker | feat(policies) | add policy CRUD + validation`  
  Body lines describe what changed and why.

---
![ERD.png](diagram/ERD.png)
![Sketch_developement.png](diagram/Sketch_developement.png)
![Full_flow.png](diagram/Full_flow.png)

## License

MIT 

