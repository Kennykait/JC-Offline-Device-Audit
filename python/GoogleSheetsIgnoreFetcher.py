import sys
import gspread
import json
from google.oauth2.service_account import Credentials

# Arguments from Jenkins pipeline
if len(sys.argv) != 3:
    print("Usage: python GoogleSheetsIgnoreFetcher.py <GoogleSheetID> <IgnoreTabName>")
    sys.exit(1)

sheet_id = sys.argv[1]
ignore_tab = sys.argv[2]

SERVICE_ACCOUNT_FILE = 'secrets/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id)
worksheet = sheet.worksheet(ignore_tab)
device_names = worksheet.col_values(1)[1:]  # Skip header
with open('IgnoreList.json', 'w', encoding='utf-8') as f:
    json.dump({'DeviceName': device_names}, f, indent=4)
print(f"Ignore list fetched: {len(device_names)} devices.")
