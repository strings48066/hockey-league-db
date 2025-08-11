"""
Shared Google Sheets client for UHL operations.
Consolidates authentication and data fetching logic.
"""
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import settings as config

class SheetsClient:
    def __init__(self, player_spreadsheet_id=None, game_spreadsheet_id=None):
        """Initialize the Google Sheets client with spreadsheet IDs"""
        
        # Use provided IDs or fall back to config defaults (environment loaded automatically)
        self.player_spreadsheet_id = (
            player_spreadsheet_id or 
            config.DEFAULT_PLAYER_SPREADSHEET_ID
        )
        
        self.game_spreadsheet_id = (
            game_spreadsheet_id or 
            config.DEFAULT_GAME_SPREADSHEET_ID
        )
        
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                config.SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Successfully authenticated with service account")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            raise
    
    def get_range(self, range_name, spreadsheet_type='player'):
        """
        Fetch data from a specific range in the spreadsheet
        Args:
            range_name: The range to fetch (e.g., 'Sheet1!A1:C10')
            spreadsheet_type: 'player' or 'game' to determine which spreadsheet to use
        Returns pandas DataFrame
        """
        # Determine which spreadsheet ID to use
        if spreadsheet_type == 'game':
            spreadsheet_id = self.game_spreadsheet_id
            if not spreadsheet_id:
                raise ValueError("Game spreadsheet ID not provided")
        else:
            spreadsheet_id = self.player_spreadsheet_id
            
        try:
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
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
    
    def get_range_with_headers(self, range_name, spreadsheet_type='player'):
        """
        Fetch data with first row as headers
        Args:
            range_name: The range to fetch (e.g., 'Sheet1!A1:C10')
            spreadsheet_type: 'player' or 'game' to determine which spreadsheet to use
        Returns pandas DataFrame with column names
        """
        df = self.get_range(range_name, spreadsheet_type)
        if not df.empty and len(df) > 1:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        return df
