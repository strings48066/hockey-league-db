"""
Shared Google Sheets client for UHL operations.
Consolidates authentication and data fetching logic.
"""
import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

class SheetsClient:
    def __init__(self, service_account_file="service-account-key.json"):
        # Load environment variables from .env file
        load_env_file()
        
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        self.SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
        self.service_account_file = service_account_file
        self.service = None
        
        if not self.SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID not found. Please check your .env file or set the environment variable.")
        
        self._authenticate()
    
    def _authenticate(self):
        """Handle Google Sheets authentication using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.SCOPES
            )
            self.service = build("sheets", "v4", credentials=credentials)
            print("✅ Successfully authenticated with service account")
        except FileNotFoundError:
            raise ValueError(f"Service account file not found: {self.service_account_file}")
        except Exception as e:
            raise ValueError(f"Authentication failed: {e}")
    
    def get_range(self, range_name):
        """
        Fetch data from a specific range in the spreadsheet
        Returns pandas DataFrame
        """
        try:
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.SPREADSHEET_ID, range=range_name)
                .execute()
            )
            values = result.get("values", [])
            
            if not values:
                print(f"No data found in range: {range_name}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values)
            return df
            
        except HttpError as err:
            print(f"Error fetching range {range_name}: {err}")
            return pd.DataFrame()
    
    def get_range_with_headers(self, range_name):
        """
        Fetch data with first row as headers
        Returns pandas DataFrame with column names
        """
        df = self.get_range(range_name)
        if not df.empty and len(df) > 1:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        return df
