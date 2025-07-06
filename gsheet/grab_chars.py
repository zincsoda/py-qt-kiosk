import os
import io
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from PIL import Image

# ===== CONFIGURATION ===== #
SPREADSHEET_ID = "1_nQy4xQsxJKceBe5Jg--sIlBIn1sb6Y2fcdYE86POFM"  # From URL: docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
SHEET_NAME = "hero"                   # Exact tab name
COLUMN = "D"                            # Column where images are inserted
OUTPUT_FOLDER = "downloaded_images"
SERVICE_ACCOUNT_FILE = "credentials.json"
# ========================= #

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive", 
                "https://www.googleapis.com/auth/spreadsheets"]
    )
    sheets_service = build("sheets", "v4", credentials=creds)
    return sheets_service

def get_column_images(sheets_service):
    # Get only the specific column data
    range_name = f"{SHEET_NAME}!{COLUMN}:{COLUMN}"
    result = sheets_service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        ranges=[range_name],
        includeGridData=True,
        fields="sheets(data(rowData(values(effectiveValue,formattedValue))))"
    ).execute()

    images = []
    for sheet in result.get('sheets', []):
        for grid_data in sheet.get('data', []):
            for row_data in grid_data.get('rowData', []):
                for cell_data in row_data.get('values', []):
                    if 'effectiveValue' in cell_data:
                        # Image in cell
                        if 'image' in cell_data['effectiveValue']:
                            image_url = cell_data['effectiveValue']['image']['imageUrl']
                            images.append(image_url)
                        # IMAGE() formula
                        elif 'formulaValue' in cell_data['effectiveValue']:
                            formula = cell_data['effectiveValue']['formulaValue']
                            if formula.startswith('=IMAGE('):
                                images.append(formula.split('"')[1])
    return images

def download_images(image_urls):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    for i, url in enumerate(image_urls, 1):
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            # Save as JPG if URL ends with .jpg, otherwise PNG
            ext = 'jpg' if url.lower().endswith('.jpg') else 'png'
            img.save(f"{OUTPUT_FOLDER}/image_{i}.{ext}")
            print(f"✅ Downloaded image_{i}.{ext}")
        except Exception as e:
            print(f"❌ Failed to download image {i}: {str(e)}")


def verify_access(sheets_service):
    # Verify sheet access
    spreadsheet = sheets_service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="properties/title,sheets(properties(title))"
    ).execute()
    
    print(f"\n🔹 Access to: {spreadsheet['properties']['title']}")
    print("🔹 Available sheets:")
    for sheet in spreadsheet['sheets']:
        print(f"- {sheet['properties']['title']}")
    
    # Verify column D data
    range_name = f"{SHEET_NAME}!{COLUMN}:{COLUMN}"
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name
    ).execute()
    
    print(f"\n🔹 Data in column {COLUMN}:")
    if 'values' in result:
        for i, value in enumerate(result['values'], 1):
            print(f"Row {i}: {value[0] if value else '<empty>'}")
    else:
        print("No data found in column")


def main():
    print("🔍 Authenticating...")
    sheets_service = authenticate()

    # Add this to your main() function before searching for images
    verify_access(sheets_service)
    
    print(f"📄 Searching for images in column {COLUMN}...")
    images = get_column_images(sheets_service)
    
    if not images:
        print("\n❌ No images found in column {COLUMN}. Possible reasons:")
        print("1. Images not inserted via 'Insert > Image > Image in cell'")
        print("2. Column letter is incorrect (currently set to '{COLUMN}')")
        print("3. Sheet name '{SHEET_NAME}' is incorrect")
        print("4. Service account lacks permissions")
        print("\n💡 Test suggestion:")
        print("- Insert a new test image in column D via 'Insert > Image > Image in cell'")
        print("- Verify the sheet is shared with your service account email")
    else:
        print(f"🖼️ Found {len(images)} images. Downloading...")
        download_images(images)
        print("🎉 Download complete!")

if __name__ == "__main__":
    main()