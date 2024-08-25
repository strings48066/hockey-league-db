import gspread
from google.oauth2.service_account import Credentials

# Path to your service account key file
SERVICE_ACCOUNT_FILE = './crucial-matter-330121-f5cf1545c17c.json'

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate using the service account
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)

# Open the Google Sheet by name
sheet = client.open("scoresheet-template-2024-25").game1

# Fetch all records from the sheet
records = sheet.get_all_records()

# Print the records
print(records)