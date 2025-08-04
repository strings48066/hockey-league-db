"""
Data formatters for UHL operations.
Handles conversion from Google Sheets data to standardized JSON formats.
"""
import json

class GameFormatter:
    @staticmethod
    def format_all_games(df):
        """Format games data from Google Sheets"""
        df.columns = ["SeasonId", "id", "Date", "Time", "Home", "Away", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", "Ref1", "Ref2"]
        return df.to_dict(orient='records')
    
    @staticmethod
    def create_game_structure(game_data):
        """Create standardized game structure"""
        return {
            "id": game_data.get("id", ""),
            "Date": game_data.get("Date", ""),
            "Time": game_data.get("Time", ""),
            "Home": game_data.get("HomeTeam", ""),
            "Away": game_data.get("AwayTeam", ""),
            "Ref1": game_data.get("Ref1", ""),
            "Ref2": game_data.get("Ref2", ""),
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

class PlayerFormatter:
    @staticmethod
    def format_players(df):
        """Format basic player info"""
        df.columns = ["id", "FirstName", "Lastname"]
        return df[["id", "FirstName", "Lastname"]].to_dict(orient='records')
    
    @staticmethod
    def format_season_stats(df):
        """Format player season statistics"""
        df.columns = ["Team", "JerseyNumber", "Position", "GP", "G", "A", "PTS", "PIM", "GWG", "GS"]
        df["id"] = "1"
        return df.to_dict(orient='records')
    
    @staticmethod
    def combine_player_data(players, seasons):
        """Combine player info with season stats"""
        combined_data = []
        for i, player in enumerate(players):
            player_record = {
                "id": player["id"],
                "firstName": player["FirstName"],
                "lastName": player["Lastname"],
                "seasons": [seasons[i]] if i < len(seasons) else []
            }
            combined_data.append(player_record)
        return combined_data

class StandingsFormatter:
    @staticmethod
    def format_standings(df):
        """Format standings data from Google Sheets"""
        standings_data = []
        
        for index, row in df.iterrows():
            data = {
                'id': row[0],
                'Team': row[1],
                'W': row[2],
                'L': row[3],
                'T': row[4],
                'P': row[5] if len(row) > 5 else '',
                'GF': row[6] if len(row) > 6 else '',
                'GA': row[7] if len(row) > 7 else '',
                'PIM': row[8] if len(row) > 8 else '',
                'Home': row[9] if len(row) > 9 else '',
                'Away': row[10] if len(row) > 10 else '',
                'Streak': row[11] if len(row) > 11 else ''
            }
            standings_data.append(data)
        
        return standings_data

class OutputManager:
    @staticmethod
    def save_json(data, output_path, indent=4):
        """Save data to JSON file"""
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=indent)
        print(f"Data saved to {output_path}")
    
    @staticmethod
    def load_json(input_path):
        """Load data from JSON file"""
        try:
            with open(input_path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File not found: {input_path}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {input_path}")
            return None
