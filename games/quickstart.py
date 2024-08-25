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

def process_json_template(input_path, output_path, df_team1, df_team2):
    def transform_df(df):
    # Ensure the DataFrame has 8 columns before renaming
        if len(df.columns) == 8:
            # Rename columns and exclude the original "id" column
            df.columns = ["id", "name", "pos", "no", "g", "a", "pts", "pim"]
            # Add a new "id" column with incrementing values starting from 1
            df["id"] = range(1, len(df) + 1)
            # Return the DataFrame as a list of dictionaries
            return df[["id", "name", "pos", "no", "g", "a", "pts", "pim"]].to_dict(orient='records')
        else:
            raise ValueError(f"Expected 8 columns, but got {len(df.columns)} columns")

    df_home = transform_df(df_team1)
    df_away = transform_df(df_team2)
    input_file_path = input_path
    output_file_path = output_path

    # Read the JSON template into memory
    with open(input_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Update the JSON template with Home team data
    data['Lineups']['Home'] = df_home
    
    # Update the JSON template with Away team data
    data['Lineups']['Away'] = df_away
    
    # Write the updated JSON template to the specified output file path
    with open(output_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"JSON template updated at {output_file_path}")

def main():
    input_path = "game_template.json"
    output_path = "game_output.json"
    range_name1 = "game1!A3:H14"  # Example range
    range_name2 = "game1!K3:R14"
    df_team1 = getRange(range_name1)
    df_team2 = getRange(range_name2)
    process_json_template(input_path, output_path, df_team1, df_team2)
    # # Print the DataFrames
    # print("Team 1 DataFrame:")
    print(df_team1)
    # print("\nTeam 2 DataFrame:")
    print(df_team2)

if __name__ == "__main__":
    main()