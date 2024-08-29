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

def set_lineups(df):
    if len(df.columns) == 8:
        df.columns = ["name", "pos", "no", "status", "g", "a", "pts", "pim"]
        df["id"] = range(1, len(df) + 1)
        return df[["id", "name", "pos", "no", "status", "g", "a", "pts", "pim"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 8 columns, but got {len(df.columns)} columns")

def format_goals(df):
    if df.empty:
        return []
    goals_df = df.iloc[:, :5].copy()  # Make a copy of the slice
    if len(goals_df.columns) == 5:
        goals_df.columns = ["Time", "Team", "ScoredBy", "Assist1", "Assist2"]
        goals_df.loc[:, "id"] = range(1, len(goals_df) + 1)  # Use .loc to set the new column
        return goals_df[["id", "Time", "Team", "ScoredBy", "Assist1", "Assist2"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 5 columns for goals, but got {len(goals_df.columns)} columns")

def format_penalties(df):
    if df.empty:
        return []
    penalties_df = df.iloc[:, 5:].copy()  # Make a copy of the slice
    if len(penalties_df.columns) == 5:
        penalties_df.columns = ["Time", "Team", "Player", "Penalty", "Duration"]
        penalties_df.loc[:, "id"] = range(1, len(penalties_df) + 1)  # Use .loc to set the new column
        return penalties_df[["id", "Time", "Team", "Player", "Penalty", "Duration"]].to_dict(orient='records')
    else:
        raise ValueError(f"Expected 5 columns for penalties, but got {len(penalties_df.columns)} columns")

def main():
    input_path = "game_template.json"
    output_path = "game_output.json"
    range_name1 = "scoresheet!A3:H14"  # Example range for team 1
    range_name2 = "scoresheet!K3:R14"  # Example range for team 2
    game_info_range = "gameinfo!A2:J2"  # Range for game info
    goals_range = "scoresheet!A18:I34"  # Example range for goals
    penalties_range = "scoresheet!J18:N34"  # Example range for penalties

    game_info = getRange(game_info_range)
    df_team1 = getRange(range_name1)
    df_team2 = getRange(range_name2)
    df_goals = getRange(goals_range)
    df_penalties = getRange(penalties_range)

    game_id = game_info.iloc[0, 0]
    game_date = game_info.iloc[0, 1]
    game_home = game_info.iloc[0, 2]
    game_away = game_info.iloc[0, 3]
    game_time = game_info.iloc[0, 4]
    game_ref1 = game_info.iloc[0, 5]
    game_ref2 = game_info.iloc[0, 6]

    df_home = set_lineups(df_team1)
    df_away = set_lineups(df_team2)
    goals = format_goals(df_goals)
    #penalties = format_penalties(df_penalties)

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