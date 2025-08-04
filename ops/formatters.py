"""
Data formatters for UHL operations.
Handles conversion from Google Sheets data to standardized JSON formats.
"""
import json
import pandas as pd

class GameFormatter:
    @staticmethod
    def format_lineups(df):
        """Format lineup data from Google Sheets"""
        if df.empty:
            return []
        
        if len(df.columns) == 8:
            df.columns = ["name", "pos", "no", "status", "g", "a", "pts", "pim"]
            df["id"] = range(1, len(df) + 1)
            return df[["id", "name", "pos", "no", "status", "g", "a", "pts", "pim"]].to_dict(orient='records')
        else:
            raise ValueError(f"Expected 8 columns for lineups, but got {len(df.columns)} columns")

    @staticmethod
    def format_all_games(df):
        """Format games schedule data from Google Sheets (simple list format)"""
        if df.empty:
            return []
        
        df.columns = ["SeasonId", "id", "Date", "Time", "Home", "Away", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", "Ref1", "Ref2"]
        return df.to_dict(orient='records')
    
    @staticmethod
    def format_game_events(df):
        """Format game events data from gameEvents sheet"""
        if df.empty:
            return []
        
        # Skip header row and set column names
        events_df = df.iloc[1:].copy()  # Skip header row
        events_df.columns = ["id", "gameId", "eventTime", "Team", "ScoredBy", "Asst1", "Asst2", "PenaltyPlayer", "Infraction", "PIM", "GWG"]
        
        # Convert to records for easier processing
        return events_df.to_dict(orient='records')
    
    @staticmethod
    def build_complete_schedule(games_df, events_df, players_df=None):
        """Build complete schedule.json format by combining games and events data"""
        if games_df.empty:
            return []
        
        # Format basic games data
        games = GameFormatter.format_all_games(games_df)
        
        # Format events data
        events = GameFormatter.format_game_events(events_df)
        
        # Group events by gameId
        events_by_game = {}
        for event in events:
            game_id = str(event['gameId'])
            if game_id not in events_by_game:
                events_by_game[game_id] = {'goals': [], 'penalties': []}
            
            # Check if this is a goal or penalty based on populated fields
            if event['ScoredBy'] and str(event['ScoredBy']).strip():
                # This is a goal
                goal = {
                    "id": len(events_by_game[game_id]['goals']) + 1,
                    "Time": str(event['eventTime']),
                    "Team": str(event['Team']),
                    "ScoredBy": str(event['ScoredBy']),
                    "Asst1": str(event['Asst1']) if event['Asst1'] and str(event['Asst1']).strip() else None,
                    "Asst2": str(event['Asst2']) if event['Asst2'] and str(event['Asst2']).strip() else None
                }
                events_by_game[game_id]['goals'].append(goal)
            
            elif event['PenaltyPlayer'] and str(event['PenaltyPlayer']).strip():
                # This is a penalty
                penalty = {
                    "id": len(events_by_game[game_id]['penalties']) + 1,
                    "Time": str(event['eventTime']),
                    "Team": str(event['Team']),
                    "Player": str(event['PenaltyPlayer']),
                    "Infraction": str(event['Infraction']),
                    "Minutes": str(event['PIM'])
                }
                events_by_game[game_id]['penalties'].append(penalty)
        
        # Build complete schedule entries
        complete_schedule = []
        for game in games:
            game_id = str(game['id'])
            
            # Get events for this game
            game_events = events_by_game.get(game_id, {'goals': [], 'penalties': []})
            
            # Create schedule entry matching existing format
            schedule_entry = {
                "id": str(game['id']),
                "Date": str(game['Date']),
                "Home": str(game['HomeTeam']),
                "Away": str(game['AwayTeam']),
                "Time": str(game['Time']).replace(' PM', '').replace(' AM', ''),  # Remove AM/PM
                "Ref1": str(game['Ref1']) if game['Ref1'] else "",
                "Ref2": str(game['Ref2']) if game['Ref2'] else "",
                "GameLink": f"/gameSummary/{int(game['id']) - 1}",  # Generate game link
                "Score": f"{game['HomeTeam']} {game['HomeScore']} - {game['AwayScore']} {game['AwayTeam']}",
                "Played": "Y" if game['HomeScore'] and game['AwayScore'] else "N",
                "Lineups": {
                    "Home": [],  # Would need roster data to populate
                    "Away": []   # Would need roster data to populate
                },
                "Goals": game_events['goals'],
                "Penalties": game_events['penalties']
            }
            
            complete_schedule.append(schedule_entry)
        
        return complete_schedule
    
    @staticmethod
    def create_schedule_entry(game_info, home_lineup, away_lineup, goals, penalties):
        """Create a schedule entry in the format matching existing schedule.json"""
        if game_info.empty:
            raise ValueError("Game info is required")
        
        return {
            "id": str(game_info.iloc[0, 0]) if len(game_info.columns) > 0 else "",
            "Date": str(game_info.iloc[0, 1]) if len(game_info.columns) > 1 else "",
            "Home": str(game_info.iloc[0, 2]) if len(game_info.columns) > 2 else "",
            "Away": str(game_info.iloc[0, 3]) if len(game_info.columns) > 3 else "",
            "Time": str(game_info.iloc[0, 4]) if len(game_info.columns) > 4 else "",
            "Ref1": str(game_info.iloc[0, 5]) if len(game_info.columns) > 5 else "",
            "Ref2": str(game_info.iloc[0, 6]) if len(game_info.columns) > 6 else "",
            "GameLink": str(game_info.iloc[0, 7]) if len(game_info.columns) > 7 else "",
            "Score": str(game_info.iloc[0, 8]) if len(game_info.columns) > 8 else "",
            "Played": str(game_info.iloc[0, 9]) if len(game_info.columns) > 9 else "",
            "Lineups": {
                "Home": home_lineup,
                "Away": away_lineup
            },
            "Goals": goals,
            "Penalties": penalties
        }
    
    @staticmethod
    def format_penalties(df):
        """Format penalties data to match existing schedule.json structure"""
        if df.empty:
            return []
        
        penalties_df = df.iloc[:, :5].copy()  # Take first 5 columns
        if len(penalties_df.columns) == 5:
            penalties_df.columns = ["Time", "Team", "Player", "Infraction", "Minutes"]
            penalties_df.loc[:, "id"] = range(1, len(penalties_df) + 1)
            
            # Format to match existing structure with proper field names
            formatted_penalties = []
            for _, row in penalties_df.iterrows():
                penalty = {
                    "id": int(row["id"]),
                    "Time": str(row["Time"]),
                    "Team": str(row["Team"]), 
                    "Player": str(row["Player"]),
                    "Infraction": str(row["Infraction"]),
                    "Minutes": str(row["Minutes"])
                }
                formatted_penalties.append(penalty)
            return formatted_penalties
        else:
            raise ValueError(f"Expected 5 columns for penalties, but got {len(penalties_df.columns)} columns")
    
    @staticmethod
    def format_goals(df):
        """Format goals data to match existing schedule.json structure"""
        if df.empty:
            return []
        
        goals_df = df.iloc[:, :5].copy()  # Take first 5 columns
        if len(goals_df.columns) == 5:
            goals_df.columns = ["Time", "Team", "ScoredBy", "Asst1", "Asst2"]
            goals_df.loc[:, "id"] = range(1, len(goals_df) + 1)
            
            # Format to match existing structure 
            formatted_goals = []
            for _, row in goals_df.iterrows():
                goal = {
                    "id": int(row["id"]),
                    "Time": str(row["Time"]),
                    "Team": str(row["Team"]),
                    "ScoredBy": str(row["ScoredBy"]),
                    "Asst1": str(row["Asst1"]) if pd.notna(row["Asst1"]) and str(row["Asst1"]).strip() else None,
                    "Asst2": str(row["Asst2"]) if pd.notna(row["Asst2"]) and str(row["Asst2"]).strip() else None
                }
                formatted_goals.append(goal)
            return formatted_goals
        else:
            raise ValueError(f"Expected 5 columns for goals, but got {len(goals_df.columns)} columns")

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
