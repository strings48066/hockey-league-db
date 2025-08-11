"""
Schedule and game data formatters.
"""
import pandas as pd
from .base import BaseFormatter


class GameFormatter(BaseFormatter):
    """Handles formatting of game and schedule data."""
    
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

    @classmethod
    def format_all_games(cls, df):
        """Format games schedule data from Google Sheets."""
        empty_check = cls.handle_empty_data(df, "games")
        if empty_check:
            return empty_check
        
        try:
            expected_columns = ["SeasonId", "id", "Date", "Time", "Home", "Away", 
                              "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", "Ref1", "Ref2"]
            
            # Check for TBD data during season startup
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Found {len(df.columns)} columns, expected {len(expected_columns)}. Likely TBD data.")
                return {
                    "message": "Season not yet started - TBD data detected",
                    "status": "pending",
                    "games": []
                }
            
            df = cls.safe_column_assignment(df, expected_columns)
            
            # Filter out TBD or empty data
            df_clean = df.dropna(subset=['Date', 'Home', 'Away'])
            df_clean = df_clean[~df_clean['Date'].astype(str).str.contains('TBD|tbd', case=False, na=False)]
            
            if df_clean.empty:
                return {
                    "message": "No valid games found - season appears to be in planning phase",
                    "status": "planning", 
                    "games": []
                }
                
            return {
                "message": f"Successfully processed {len(df_clean)} games",
                "status": "active",
                "games": df_clean.to_dict(orient='records')
            }
            
        except Exception as e:
            print(f"⚠️  Error processing games data: {e}")
            return {
                "message": "Unable to process games data",
                "status": "error",
                "error": str(e),
                "games": []
            }
    
    @classmethod
    def check_season_status(cls, df):
        """Check if season is active, planning, or TBD"""
        if df.empty:
            return {"status": "no_data", "message": "No schedule data found", "ready_for_play": False}
        
        is_tbd = cls.check_tbd_content(df)
        tbd_count = sum(1 for _, row in df.iterrows() if cls._row_is_tbd(row))
        valid_count = len(df) - tbd_count
        
        if is_tbd:
            return {
                "status": "planning",
                "message": f"Season in planning phase ({tbd_count} TBD, {valid_count} scheduled)",
                "ready_for_play": False,
                "tbd_count": tbd_count,
                "valid_count": valid_count
            }
        else:
            return {
                "status": "active", 
                "message": f"Season active ({valid_count} games scheduled)",
                "ready_for_play": True,
                "tbd_count": tbd_count,
                "valid_count": valid_count
            }
    
    @staticmethod
    def _row_is_tbd(row):
        """Check if a row contains TBD data."""
        row_str = ' '.join(str(val) for val in row.values)
        return 'TBD' in row_str.upper() or pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == ''


class ScheduleFormatter(BaseFormatter):
    """Handles complete schedule formatting with games, events, and lineups."""
    
    @classmethod
    def format_complete_schedule(cls, games_data, events_data, lineups_data):
        """Format complete schedule combining games, events, and lineups."""
        try:
            schedule = []
            
            for game in games_data:
                game_id = str(game.get('id', ''))
                
                # Get events for this game
                game_events = [event for event in events_data if str(event.get('gameId', '')) == game_id]
                
                # Get lineups for this game
                game_lineups = lineups_data.get(game_id, {"Home": [], "Away": []})
                
                # Build complete game object
                complete_game = {
                    **game,
                    "Lineups": game_lineups,
                    "Goals": cls._extract_goals(game_events),
                    "Penalties": cls._extract_penalties(game_events)
                }
                
                schedule.append(complete_game)
                
            return schedule
            
        except Exception as e:
            print(f"Error formatting complete schedule: {e}")
            return []
    
    @staticmethod
    def _extract_goals(events):
        """Extract goal events from game events."""
        goals = []
        for event in events:
            if event.get('ScoredBy'):  # Goal event
                goals.append({
                    "id": len(goals) + 1,
                    "Time": event.get('eventTime', ''),
                    "Team": event.get('Team', ''),
                    "ScoredBy": event.get('ScoredBy', ''),
                    "Asst1": event.get('Asst1') or None,
                    "Asst2": event.get('Asst2') or None
                })
        return goals
    
    @staticmethod
    def _extract_penalties(events):
        """Extract penalty events from game events."""
        penalties = []
        for event in events:
            if event.get('PenaltyPlayer'):  # Penalty event
                penalties.append({
                    "id": len(penalties) + 1,
                    "Time": event.get('eventTime', ''),
                    "Team": event.get('Team', ''),
                    "Player": event.get('PenaltyPlayer', ''),
                    "Infraction": event.get('Infraction', ''),
                    "Minutes": event.get('PIM', '')
                })
        return penalties
