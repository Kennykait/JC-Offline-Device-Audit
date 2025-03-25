import sys
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import *

if len(sys.argv) != 3:
    print("Usage: python CreateGoogleSheet.py <SheetTitle> <ShareWithEmail>")
    sys.exit(1)

sheet_title = sys.argv[1]
share_email = sys.argv[2]

SERVICE_ACCOUNT_FILE = 'secrets/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Create sheet and share it
sheet = client.create(sheet_title)
sheet.share(share_email, perm_type='user', role='writer', notify=False)

# Setup the default worksheet
worksheet = sheet.get_worksheet(0)
headers = [
    "Hostname",
    "Device ID",
    "OS",
    "Last Contact",
    "Offline Days",
    "User Emails",
    "UserID",
    "Account Status",
    "In Vacation",
    "In Vacation Until"
]
worksheet.update("A1:K1", [headers])

# Freeze the first row
set_frozen(worksheet, rows=1)

# Format the header row
header_fmt = CellFormat(
    textFormat=textFormat(bold=True),
    backgroundColor=Color(0.86, 0.87, 0.89)
)
format_cell_range(worksheet, '1:1', header_fmt)

# Resize columns to fit content
for col_index in range(1, len(headers) + 1):
    set_column_width(worksheet, col_index, 220)

# Setup conditional formatting
rules = get_conditional_format_rules(worksheet)
rules.clear()

# Highlight 'None' in User Emails (F) and UserID (G)
rules.add(ConditionalFormatRule(
    ranges=[GridRange(sheetId=worksheet.id, startRowIndex=1, endRowIndex=1000, startColumnIndex=5, endColumnIndex=7)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('TEXT_EQ', ['None']),
        format=CellFormat(backgroundColor=Color(1, 1, 0))
    )
))

# Highlight 'Suspended' in Account Status (H)
rules.add(ConditionalFormatRule(
    ranges=[GridRange(sheetId=worksheet.id, startRowIndex=1, endRowIndex=1000, startColumnIndex=7, endColumnIndex=8)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('TEXT_EQ', ['Suspended']),
        format=CellFormat(textFormat=textFormat(foregroundColor=Color(1, 0, 0), bold=True))
    )
))

rules.save()

print(f"Created and formatted Google Sheet: {sheet.title}")
print(f"URL: {sheet.url}")
