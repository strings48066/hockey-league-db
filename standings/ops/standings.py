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

def set_standings(df):
    if len(df.columns) == 12:
        df.columns = ["id", "Team", "W", "L", "T", "P", "GF", "GA", "PIM", "Home", "Away", "Streak"]
        return df[["id", "Team", "W", "L", "T", "P", "GF", "GA", "PIM", "Home", "Away", "Streak"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 5 columns for standings, but got {len(df.columns)} columns")

def main():
    input_path = "standings_template.json"
    output_path = "output.json"
    range_standings = "standings!A2:L5"  # Example range for team 1
    df_standings = getRange(range_standings)
    
    data_list = []
    for index, row in df_standings.iterrows():
        team_id = row[0]
        team = row[1]
        wins = row[2]
        losses = row[3]
        ties = row[4]
        points = row[5]
        goalsfor = row[6]
        goalsagainst = row[7]
        penaltyminutes = row[8]
        homerecord = row[9]
        awayrecord = row[10]
        streak = row[11]

        data = {}
        data['id'] = team_id
        data['Team'] = team
        data['W'] = wins
        data['L'] = losses
        data['T'] = ties
        data['GF'] = goalsfor
        data['GA'] = goalsagainst
        data['PIM'] = penaltyminutes
        data['Streak'] = streak
        data['Home'] = homerecord
        data['Away'] = awayrecord

        data_list.append(data)

    with open(output_path, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)

    print(f"Data has been written to {output_path}")

if __name__ == "__main__":
    main()