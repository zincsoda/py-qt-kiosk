import gspread

gc = gspread.service_account(filename='credentials.json')

# Open the Google Sheet by its title
sheet_title = 'Hanzi'
sheet = gc.open(sheet_title)

# Select a specific worksheet by its title
worksheet_title = 'Hero'
worksheet = sheet.worksheet(worksheet_title)

# Get all values from the worksheet
data = worksheet.get_all_values()

# Print the data
for row in data:
    print(row[1], )
