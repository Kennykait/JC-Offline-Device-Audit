import sys
import json
import argparse
import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import *

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("sheet_id", help="Google Sheet ID")
parser.add_argument("tab_name", help="Tab name for new worksheet")
parser.add_argument("--creds", default="secrets/service_account.json", help="Path to service account JSON")
args = parser.parse_args()

# Load credentials
creds = Credentials.from_service_account_file(args.creds, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)
sheet = client.open_by_key(args.sheet_id)
worksheet = sheet.add_worksheet(title=args.tab_name, rows="1000", cols="20")

# Load audit results
with open("JumpCloudData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Upload rows
header = list(data[0].keys())
rows = [header] + [[row.get(col, '') for col in header] for row in data]
worksheet.update("A1", rows, value_input_option="USER_ENTERED")

# Resize columns
for col_index in range(1, len(header) + 1):
    set_column_width(worksheet, col_index, 220)

# Header styling
header_fmt = CellFormat(textFormat=textFormat(bold=True), backgroundColor=Color(0.86, 0.87, 0.89))
format_cell_range(worksheet, '1:1', header_fmt)
set_frozen(worksheet, rows=1)

# Conditional formatting
rules = get_conditional_format_rules(worksheet)
rules.clear()

rules.add(ConditionalFormatRule(
    ranges=[GridRange(sheetId=worksheet.id, startRowIndex=1, endRowIndex=len(rows), startColumnIndex=5, endColumnIndex=7)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('TEXT_EQ', ['None']),
        format=CellFormat(backgroundColor=Color(1, 1, 0))
    )
))

rules.add(ConditionalFormatRule(
    ranges=[GridRange(sheetId=worksheet.id, startRowIndex=1, endRowIndex=len(rows), startColumnIndex=7, endColumnIndex=8)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('TEXT_EQ', ['Suspended']),
        format=CellFormat(textFormat=textFormat(foregroundColor=Color(1, 0, 0), bold=True))
    )
))

rules.save()
print(f"Data uploaded to Google Sheet tab: {args.tab_name}")
