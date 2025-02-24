import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import json
import os

sys.stdout.reconfigure(encoding='utf-8')

# Pass Google Sheet ID and Name as arguments from PWSH
GOOGLE_SHEET_ID = sys.argv[1]  # Google Sheet ID from PowerShell
IGNORE_TAB_NAME = sys.argv[2]  # Tab Name for Ignore List

# GCP Service Account json
AUTOMATION_PATH = r"C:\Scripts" # Absolute path to the automation
SERVICE_ACCOUNT_FILE = os.path.join(AUTOMATION_PATH, "Credenials", "service_account.json")
IGNORE_LIST_FILE = os.path.join(AUTOMATION_PATH, "Audit", "IgnoreList.json")

# Google Sheets API Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)

# Open the Sheet and navigate to the Ignore List tab
sheet = client.open_by_key(GOOGLE_SHEET_ID)
worksheet = sheet.worksheet(IGNORE_TAB_NAME)

# Read the ignore list (Assuming "DeviceName" is in the first column)
ignore_data = worksheet.col_values(1)  # Reads all values in column A

# Remove header (assuming first row is "DeviceName")
ignore_data = ignore_data[1:]  # Skips the header

# Save ignore list to JSON file
with open(IGNORE_LIST_FILE, "w", encoding="utf-8") as file:
    json.dump({"DeviceName": ignore_data}, file, indent=4)

print(f"✅ Ignore list saved to {IGNORE_LIST_FILE}")
