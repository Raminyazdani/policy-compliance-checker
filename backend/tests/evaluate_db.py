# populate.py
# pip install requests
import json
import requests

BASE_URL = "http://127.0.0.1:8000"

res = requests.post(f"{BASE_URL}/evaluate")
print("GET /policies ->", res.status_code, res.text)

