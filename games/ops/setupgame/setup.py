from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Define the scopes for Google Sheets and Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = 'google-creds.json'

def copy_google_sheet(sheet_id, new_title):
    # Authenticate using the service account file
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=creds)

    # Request body to copy the file
    body = {
        'name': new_title  # New title for the copied sheet
    }

    # Copy the Google Sheet
    try:
        copied_file = drive_service.files().copy(fileId=sheet_id, body=body).execute()
        print(f"Sheet copied successfully. New sheet ID: {copied_file['id']}")
        return copied_file['id']
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace with the Google Sheet ID you want to copy and the new title
original_sheet_id = '18epDeN0D1JwYv2Kg3351d9oy0ymXfNtgnNMBX63U9rw'
new_sheet_title = 'Copied Google Sheet'

# Call the function to copy the sheet
copied_sheet_id = copy_google_sheet(original_sheet_id, new_sheet_title)