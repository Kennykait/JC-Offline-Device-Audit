import sys
import argparse
import gspread
from google.oauth2.service_account import Credentials
import json

parser = argparse.ArgumentParser()
parser.add_argument("sheet_id", help="Google Sheet ID")
parser.add_argument("ignore_tab", help="Ignore List tab name")
parser.add_argument("--creds", default="secrets/service_account.json", help="Path to service account file")
args = parser.parse_args()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(args.creds, scopes=SCOPES)
client = gspread.authorize(creds)

sheet = client.open_by_key(args.sheet_id)
worksheet = sheet.worksheet(args.ignore_tab)
ignore_data = worksheet.col_values(1)[1:]  # Skip header

# Save to JSON file for PowerShell to consume
ignore_json = [{"DeviceName": name} for name in ignore_data]
with open("C:/Scripts/NordSec/Audit/IgnoreList.json", "w", encoding="utf-8") as f:
    json.dump(ignore_json, f, indent=2)

print(f"✅ Ignore list saved with {len(ignore_data)} entries.")
