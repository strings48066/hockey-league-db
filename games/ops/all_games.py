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
    creds = None  # Initialize creds within the function
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../../google-creds.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame()  # Return an empty DataFrame

        # Convert the values to a DataFrame
        df = pd.DataFrame(values)
        return df
    except HttpError as err:
        print(err)
        return pd.DataFrame()  # Return an empty DataFrame in case of error

def format_game(df):
    df.columns = ["SeasonId", "id", "Date", "Time", "Home", "Away", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", "Ref1", "Ref2"]
    return df.to_dict(orient='records')

def main():
    # Dictionary mapping team IDs to team names
    TEAM_NAMES = {
        1: "New York",
        2: "Detroit",
        3: "Chicago",
        4: "Boston"
        # Add more mappings as needed
    }
    input_path = "game_template.json"
    output_path = "output.json"
    game_info_range = "games!A2:L55"  # Range for game info

    game_info = getRange(game_info_range)
    print(game_info)
    games = format_game(game_info)

    combined_data = []
    for i, game in enumerate(games):
        game_record = {
            "id": game["id"],
            "Date": game["Date"],
            "Time": game["Time"],
            "Home": game["HomeTeam"],
            "Away": game["AwayTeam"],
            "Ref1": game["Ref1"],
            "Ref2": game["Ref2"],
            "GameLink": "",
            "Score": "",
            "Played": "",
            "Lineups": {
                "Home": [],
                "Away": []
            },
            "Goals": [{}],
            "Penalties": [{}]
        }
        combined_data.append(game_record)

    with open(output_path, 'w') as json_file:
        json.dump(combined_data, json_file, indent=4)

if __name__ == "__main__":
    main()