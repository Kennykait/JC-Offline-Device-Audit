import gspread
from google.oauth2.service_account import Credentials
import json
import sys
from datetime import datetime
from gspread_formatting import *
from gspread.utils import rowcol_to_a1

# Google Sheets API Variable
SERVICE_ACCOUNT_FILE = r"C:\Credentials\service_account.json"  # ✅ Update with actual service account file path
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Read input arguments from pwsh and json
GOOGLE_SHEET_ID = sys.argv[1]
TAB_NAME = f"JumpCloud Report {datetime.today().strftime('%Y%m%d%H%M')}"
USERS_FILE = r"C:\Audit\JumpCloudData.json"

# Read JC Data from json
with open(USERS_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

# Column Mapping (You can update this to your liking)
column_mapping = {
    "DeviceName": "Hostname",
    "DeviceID": "Device ID",
    "Architecture": "OS",
    "LastContact": "Last Contact",
    "Days Offline": "Offline Days",
    "BoundUserEmails": "User Emails",
    "UserID": "User ID",
    "BoundUserStatuses": "Account Status",
    "In Vacation": "In Vacation",
    "In Vacation Until": "Vacation Until"
}
column_order = list(column_mapping.keys())  # ✅ Maintain column order
header = [column_mapping[col] for col in column_order]

# Formating for Sheets
sheet_data = [header]

for entry in data:
    row = []
    for col in column_order:
        value = entry.get(col, "N/A")

        # ✅ Create hyperlink for Device ID
        if col == "DeviceID" and value != "None":
            value = f'=HYPERLINK("https://console.jumpcloud.com/#/devices/{value}/details/highlights", "{value}")'

        # ✅ Create hyperlink for User ID
        if col == "UserID" and value != "None":
            value = f'=HYPERLINK("https://console.jumpcloud.com/#/users/{value}/details", "{value}")'

        row.append(value)
    
    sheet_data.append(row)

# Create a new tab in Sheets with date and customize it
spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
worksheet = spreadsheet.add_worksheet(title=TAB_NAME, rows=str(len(sheet_data) + 10), cols=str(len(header)))

worksheet.update(range_name="A1", values=sheet_data, value_input_option="USER_ENTERED")

for col_idx in range(len(header)):
    col_letter = rowcol_to_a1(1, col_idx + 1)[0]  # ✅ Convert column index to letter (A, B, C...)
    set_column_width(worksheet, col_letter, 200)

header_format = CellFormat(
    backgroundColor=Color(0.86, 0.87, 0.89),  # ✅ Background color #dbdfe4
    textFormat=TextFormat(bold=True)
)
format_cell_range(worksheet, "A1:J1", header_format)

spreadsheet.batch_update({
    "requests": [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": worksheet.id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        }
    ]
})

conditional_format_requests = [
    # 🔴 "Suspended" users (Column H) → Red
    {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [
                    {"sheetId": worksheet.id, "startRowIndex": 1, "endRowIndex": len(sheet_data), "startColumnIndex": 7, "endColumnIndex": 8}
                ],
                "booleanRule": {
                    "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "Suspended"}]},
                    "format": {"backgroundColor": {"red": 1.0, "green": 0.4, "blue": 0.4}}
                }
            },
            "index": 0
        }
    },
    # 🟡 "None" values in Columns F & G → Yellow
    {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [
                    {"sheetId": worksheet.id, "startRowIndex": 1, "endRowIndex": len(sheet_data), "startColumnIndex": 5, "endColumnIndex": 7}
                ],
                "booleanRule": {
                    "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": "None"}]},
                    "format": {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.6}}
                }
            },
            "index": 1
        }
    }
]
spreadsheet.batch_update({"requests": conditional_format_requests})

# Print output
print(f"✅ Google Sheet '{TAB_NAME}' successfully updated.")