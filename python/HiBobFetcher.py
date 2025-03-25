import os
import requests
import base64
import json
from datetime import datetime

user_id = os.getenv("HIBOB_SERVICE_USER_ID")
token = os.getenv("HIBOB_API_TOKEN")
if not user_id or not token:
    print("Missing HiBob credentials in environment variables.")
    exit(1)

auth_header = base64.b64encode(f"{user_id}:{token}".encode()).decode()
headers = {
    "accept": "application/json",
    "authorization": f"Basic {auth_header}"
}

today = datetime.today().strftime("%Y-%m-%d")
url = f"https://api.hibob.com/v1/timeoff/whosout?from={today}&to={today}"

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"HiBob API error: {response.status_code} - {response.text}")
    exit(1)

all_data = response.json()
filtered = []

for entry in all_data:
    policy_type = entry.get("policyTypeDisplayName", "")
    if policy_type in ["Annual Vacation", "Out of office"]:
        filtered.append({
            "email": entry.get("email"),
            "startDate": entry.get("startDate"),
            "endDate": entry.get("endDate"),
            "policyTypeDisplayName": policy_type
        })

with open("HiBobOutData.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, indent=4)

print(f"HiBob vacation data fetched. Entries found: {len(filtered)}")
