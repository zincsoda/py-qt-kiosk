import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Config
SPREADSHEET_ID = "1_nQy4xQsxJKceBe5Jg--sIlBIn1sb6Y2fcdYE86POFM"  # From URL: docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
SHEET_NAME = "hero"
TARGET_CELL = "D3"
SERVICE_ACCOUNT_FILE = "service_account.json"

def inspect_cell():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheets_service = build("sheets", "v4", credentials=creds)
    
    result = sheets_service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        ranges=[f"{SHEET_NAME}!{TARGET_CELL}"],
        includeGridData=True
    ).execute()
    
    # Print everything we get back about this cell
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    print("Full cell data:")
    pp.pprint(result)
    
    # Check for specific image-related data
    if 'sheets' in result:
        sheet = result['sheets'][0]
        if 'data' in sheet:
            cell_data = sheet['data'][0]['rowData'][0]['values'][0]
            print("\nImage-specific data:")
            pp.pprint(cell_data.get('effectiveValue', {}).get('image', None))

if __name__ == "__main__":
    inspect_cell()