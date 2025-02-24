import requests
import json
import sys
import base64
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Variables
AUTOMATION_PATH = "C:\Scripts\" # Absolute path to the automation
HIBOB_SERVICE_USER_ID = "NAME"
HIBOB_TOKEN = "API"
HIBOB_BASE_URL = "https://api.hibob.com/v1"


# Authorization to HiBob
auth_string = f"{HIBOB_SERVICE_USER_ID}:{HIBOB_TOKEN}"
auth_base64 = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {auth_base64}"
}

# Get the current date
current_date = datetime.today().strftime("%Y-%m-%d")

# API Url with query parameters
hibob_url = f"https://api.hibob.com/v1/timeoff/whosout?from={current_date}&to={current_date}&includeHourly=false&includePrivate=false&includePending=false"

# Get arguments from pwsh and json
GOOGLE_SHEET_ID = sys.argv[1]
USERS_FILE = r"{AUTOMATION_PATH}\Audit\JumpCloudData.json"

with open(USERS_FILE, "r", encoding="utf-8") as file:
    users = json.load(file)

# Fetch OOO data from HiBob
def fetch_whos_out():
    try:
        response = requests.get(hibob_url, headers=headers)

        # ✅ Detect HTML Response (Authentication Failed)
        if "text/html" in response.headers.get("Content-Type", ""):
            print(f"⚠️ Received an HTML response instead of JSON. Possible authentication issue.")
            print(f"🔍 Full Response Content:\n{response.text}")  # Print full response
            sys.exit(1)  # Exit script if authentication fails

        # ✅ Handle Unauthorized Error
        if response.status_code == 401:
            print("❌ Unauthorized request. Check service user credentials.")
            sys.exit(1)

        if response.status_code != 200:
            print(f"❌ API Error: HTTP {response.status_code}")
            return []

        # ✅ Parse JSON Response
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            print(f"❌ JSON Decode Error. Response: {response.text}")
            return []

        return data.get("outOfoffice", [])  # Extract the list of users on leave

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return []

whos_out_list = fetch_whos_out()

whos_out_dict = {}

for person in whos_out_list:
    email = person.get("email", "").lower()  # Ensure email is in lowercase
    policy_type = person.get("policyTypeDisplayName", "")

    if policy_type in ["Annual Vacation", "Out of office"]:
        whos_out_dict[email] = person.get("endDate", "N/A")

for user in users:
    email = user.get("BoundUserEmails").lower()

    if email in whos_out_dict:
        user["In Vacation"] = "Yes"
        user["In Vacation Until"] = whos_out_dict[email]
    else:
        user["In Vacation"] = "No"
        user["In Vacation Until"] = "N/A"

# Save json
with open(USERS_FILE, "w", encoding="utf-8") as file:
    json.dump(users, file, indent=4)

# Print output
print(f"✅ HiBob vacation data fetched for {current_date} and added to JSON.")
