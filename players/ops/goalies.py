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
    # Assuming df has columns: ["id", "FirstName", "Lastname", "Position", "Email", "Team", "SeasonID"]
    df.columns = ["id", "FirstName", "Lastname", "Email"]
    return df[["id", "FirstName", "Lastname"]].to_dict(orient='records')

def format_season(df):
    df.columns = ["id", "Team", "Position", "GP", "GS", "W", "L", "T", "GA", "GAA"]
    return df.to_dict(orient='records')

def main():
    input_path = "player_template.json"
    output_path = "output_goalies.json"
    range_players = "goalies!A1:D5"
    range_season = "goalies!E1:N5"
    
    df_players = getRange(range_players)
    df_season = getRange(range_season)
    
    players = format_players(df_players)
    seasons = format_season(df_season)
    
    # Combine players with their respective seasons based on index
    combined_data = []
    for i, player in enumerate(players):
        player_record = {
            "id": player["id"],
            "firstName": player["FirstName"],
            "lastName": player["Lastname"],
            "seasons": [seasons[i]] if i < len(seasons) else []
        }
        combined_data.append(player_record)

    # Output the combined data to a JSON file
    with open(output_path, 'w') as f:
        json.dump(combined_data, f, indent=4)

if __name__ == "__main__":
    main()