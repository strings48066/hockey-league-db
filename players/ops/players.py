import os.path
import pandas as pd
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def getRange(range_name):
    creds = None  
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../../google-creds.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame() 

        # Convert the list to a DataFrame, assuming the first row is the header
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except HttpError as err:
        print(err)
        return pd.DataFrame()  

def format_players(df):
    if df.empty:
        return []
    # Ensure correct slicing based on actual column structure
    players_df = df.iloc[:, :].copy()  # Adjust this slice if needed
    
    if len(players_df.columns) == 7:
        players_df.columns = ["id", "FirstName", "Lastname", "Position", "JerseyNum", "Email", "TeamId"]
        players_df = players_df.drop(columns=["Email"])  # Remove the Email column
        return players_df[["id", "FirstName", "Lastname", "Position", "JerseyNum", "TeamId"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 7 columns for players, but got {len(players_df.columns)} columns")

def main():
    input_path = "player_template.json"
    output_path = "output.json"
    range_players = "players!A1:G48"
    df_players = getRange(range_players)
    print(df_players)
    players = format_players(df_players) 
    
    # with open(input_path, 'r') as json_file:
    #     data = json.load(json_file)
    
    data = players 
    # # Ensure data is a dictionary
    # if isinstance(data, list):
    #     data = data[0]  # Assuming the first element is the dictionary you need

    # #Template data
    # data['id'] = player_id

    # Write back to the JSON file
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    main()