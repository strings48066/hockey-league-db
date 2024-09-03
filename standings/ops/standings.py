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
                "credentials.json", SCOPES
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

def set_standings(df):
    if len(df.columns) == 8:
        df.columns = ["id", "Team", "W", "L", "T", "GF", "GA", "PIM", "Streak", "Home", "Away"]
        df["id"] = range(1, len(df) + 1)
        return df[["id", "Team", "W", "L", "T", "GF", "GA", "PIM", "Streak", "Home", "Away"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 8 columns, but got {len(df.columns)} columns")

def main():
    input_path = "standings_template.json"
    output_path = "output.json"
    range_standings = "scoresheet!A1:N5"  # Example range for team 1

    standings = getRange(range_standings)
    print(standings)

    with open(input_path, 'r') as json_file:
        data = json.load(json_file)

    data['Lineups']['Home'] = df_home
    data['Lineups']['Away'] = df_away
    data['Goals'] = goals
    #data['Penalties'] = penalties
    data['id'] = game_id
    data['Date'] = game_date
    data['Home'] = game_home
    data['Away'] = game_away
    data['Time'] = game_time
    data['Referee1'] = game_ref1
    data['Referee2'] = game_ref2

    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    main()