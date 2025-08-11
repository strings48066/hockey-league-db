"""
Schedule operations module.
Handles all schedule and game-related business logic.
"""
import os
import pandas as pd
from src.data.sheets_client import SheetsClient
from src.formatters.schedule import GameFormatter, ScheduleFormatter
from src.formatters.base import OutputManager
from src.utils import config


class ScheduleOperations:
    """Handles schedule and game operations."""
    
    def __init__(self, sheets_client=None):
        self.sheets_client = sheets_client or SheetsClient()
        self.game_formatter = GameFormatter()
        self.schedule_formatter = ScheduleFormatter()
        self.output_manager = OutputManager()
    
    def build_complete_schedule(self, output_dir="./output"):
        """Build complete schedule with games, events, and lineups."""
        print("Building complete schedule with games, events, and lineups...")
        
        try:
            # Get all required data
            schedule_data = self._get_schedule_data()
            events_data = self._get_events_data() 
            lineups_data = self._get_lineups_data()
            
            if not schedule_data:
                print("❌ No schedule data available")
                return []
            
            print(f"Processing {len(schedule_data)} games and {len(events_data)} events...")
            
            # Build complete schedule
            complete_schedule = self.schedule_formatter.format_complete_schedule(
                schedule_data, events_data, lineups_data
            )
            
            # Save to output
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "schedule.json")
            self.output_manager.save_json(complete_schedule, output_path)
            
            print(f"Generated complete schedule with {len(complete_schedule)} games")
            return complete_schedule
            
        except Exception as e:
            print(f"❌ Error building schedule: {e}")
            return []
    
    def _get_schedule_data(self):
        """Get basic schedule/games data."""
        try:
            # Get games data
            df_games = self.sheets_client.get_range(config.GAMES_RANGE)
            if df_games.empty:
                return []
            
            # Expected columns for games
            expected_columns = ["id", "Date", "Home", "Away", "Time", "Ref1", "Ref2", 
                              "GameLink", "Score", "Played"]
            
            if len(df_games.columns) >= len(expected_columns):
                df_games = df_games.iloc[:, :len(expected_columns)]
                df_games.columns = expected_columns
                return df_games.to_dict(orient='records')
            else:
                print(f"⚠️  Games data has {len(df_games.columns)} columns, expected {len(expected_columns)}")
                return []
                
        except Exception as e:
            print(f"Error getting schedule data: {e}")
            return []
    
    def _get_events_data(self):
        """Get game events data."""
        try:
            df_events = self.sheets_client.get_range(config.GAME_EVENTS_RANGE)
            if df_events.empty:
                return []
            
            # Expected columns for events
            expected_columns = ["id", "gameId", "eventTime", "Team", "ScoredBy", "Asst1", 
                              "Asst2", "PenaltyPlayer", "Infraction", "PIM"]
            
            if len(df_events.columns) >= len(expected_columns):
                df_events = df_events.iloc[:, :len(expected_columns)]
                df_events.columns = expected_columns
                return df_events.to_dict(orient='records')
            else:
                print(f"⚠️  Events data has {len(df_events.columns)} columns, expected {len(expected_columns)}")
                return []
                
        except Exception as e:
            print(f"Error getting events data: {e}")
            return []
    
    def _get_lineups_data(self):
        """Get lineups data for all games."""
        try:
            # Get games played data which contains lineups
            df_lineups = self.sheets_client.get_range(config.GAMES_PLAYED_RANGE)
            if df_lineups.empty:
                return {}
            
            print(f"Found gamesPlayed data with {len(df_lineups)} rows")
            
            # Process lineups by game
            lineups_by_game = {}
            
            # Group by game and team
            for _, row in df_lineups.iterrows():
                if len(row) < 12:  # Need at least basic lineup data
                    continue
                
                game_id = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                team = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
                
                if not game_id or not team:
                    continue
                
                if game_id not in lineups_by_game:
                    lineups_by_game[game_id] = {"Home": [], "Away": []}
                
                # Create player record
                player = {
                    "id": int(row.iloc[0]) if pd.notna(row.iloc[0]) else 0,
                    "name": str(row.iloc[3]) if pd.notna(row.iloc[3]) else "",
                    "pos": str(row.iloc[4]) if pd.notna(row.iloc[4]) else "",
                    "no": str(row.iloc[5]) if pd.notna(row.iloc[5]) else "",
                    "status": str(row.iloc[6]) if pd.notna(row.iloc[6]) else "active",
                    "g": str(row.iloc[7]) if pd.notna(row.iloc[7]) else "0",
                    "a": str(row.iloc[8]) if pd.notna(row.iloc[8]) else "0",
                    "pts": str(row.iloc[9]) if pd.notna(row.iloc[9]) else "0",
                    "pim": str(row.iloc[10]) if pd.notna(row.iloc[10]) else "0"
                }
                
                # Determine if home or away (this logic may need adjustment based on your data)
                home_away = str(row.iloc[11]) if len(row) > 11 and pd.notna(row.iloc[11]) else "Home"
                
                if home_away.lower() in ["away", "a"]:
                    lineups_by_game[game_id]["Away"].append(player)
                else:
                    lineups_by_game[game_id]["Home"].append(player)
            
            return lineups_by_game
            
        except Exception as e:
            print(f"Error getting lineups data: {e}")
            return {}
