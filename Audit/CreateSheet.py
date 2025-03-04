import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Variables
AUTOMATION_PATH = r"C:\Scripts" # Absolute path to the automation
SERVICE_ACCOUNT_FILE = os.path.join(AUTOMATION_PATH, "Credentials", "service_account.json")
USER_EMAIL = "admin@gmail.com"  # Your email (To send an invitation

# Google API Scopes for Sheet creation.
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Google API Authentication
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
client = gspread.authorize(creds)

#New Google Sheet Creation
spreadsheet = client.create("JumpCloud Audit Report")
spreadsheet_id = spreadsheet.id  # Get the new spreadsheet ID

print(f"✅ Google Sheet Created: {spreadsheet.url}")

# Invite your user as an editor
drive_service = build("drive", "v3", credentials=creds)
permission = {
    "type": "user",
    "role": "writer",
    "emailAddress": USER_EMAIL
}
drive_service.permissions().create(
    fileId=spreadsheet_id,
    body=permission,
    transferOwnership=False
).execute()

print(f"✅ Shared Google Sheet with {USER_EMAIL} as Editor")

# Transfer ownership of Sheet
ownership_permission = {
    "type": "user",
    "role": "owner",
    "emailAddress": USER_EMAIL
}
drive_service.permissions().create(
    fileId=spreadsheet_id,
    body=ownership_permission,
    transferOwnership=True
).execute()

print(f"✅ Ownership Transferred to {USER_EMAIL}")

# Output Google Sheet ID
print(f"📌 Use this Sheet ID in your scripts: {spreadsheet_id}")
