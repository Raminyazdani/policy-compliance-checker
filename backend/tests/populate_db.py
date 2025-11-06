# populate.py
# pip install requests
import json
import requests

BASE_URL = "http://127.0.0.1:8000"
POLICIES_PATH = "../../data/policies_seed.json"
USERS_PATH = "../../data/users_seed.json"

with open(POLICIES_PATH, "r", encoding="utf-8") as f:
    policies = json.load(f)
res = requests.post(f"{BASE_URL}/policies", json=policies)
print("POST /policies ->", res.status_code, res.text)

with open(USERS_PATH, "r", encoding="utf-8") as f:
    users = json.load(f)
res = requests.post(f"{BASE_URL}/users", json=users)
print("POST /users    ->", res.status_code, res.text)

# res = requests.post(f"{BASE_URL}/evaluate")