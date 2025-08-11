"""
Player data formatters.
"""
import pandas as pd
from .base import BaseFormatter


class PlayerFormatter(BaseFormatter):
    """Handles formatting of player data and statistics."""
    
    @classmethod
    def format_players(cls, df):
        """Format players data from Google Sheets."""
        empty_check = cls.handle_empty_data(df, "players")
        if empty_check:
            return empty_check.get("data", [])
        
        try:
            # Check for TBD content
            if cls.check_tbd_content(df):
                print("⚠️  Warning: Player data contains TBD content")
                return []
            
            expected_columns = ["id", "firstName", "lastName"]
            
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Found {len(df.columns)} columns, expected at least {len(expected_columns)}")
                return []
            
            # Use only the first 3 columns for basic player info
            df_players = df.iloc[:, :3].copy()
            df_players.columns = expected_columns
            
            # Remove any rows with missing essential data
            df_players = df_players.dropna(subset=['firstName', 'lastName'])
            
            return df_players.to_dict(orient='records')
            
        except Exception as e:
            print(f"⚠️  Error processing players data: {e}")
            return []
    
    @classmethod 
    def format_season_stats(cls, df):
        """Format player season statistics from Google Sheets."""
        if df.empty:
            return []
        
        try:
            # Check for TBD content
            if cls.check_tbd_content(df):
                print("⚠️  Warning: Season stats contain TBD content")
                return []
            
            expected_columns = ["Team", "JerseyNumber", "Position", "GP", "G", "A", "PTS", "PIM", "GWG", "id"]
            
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Found {len(df.columns)} columns for season stats, expected {len(expected_columns)}")
                return []
            
            df_stats = df.iloc[:, :len(expected_columns)].copy()
            df_stats.columns = expected_columns
            
            # Remove rows with missing essential data
            df_stats = df_stats.dropna(subset=['Team', 'Position'])
            
            return df_stats.to_dict(orient='records')
            
        except Exception as e:
            print(f"⚠️  Error processing season stats: {e}")
            return []
    
    @staticmethod
    def combine_player_data(players, seasons):
        """Combine player data with their season statistics."""
        if not players:
            return []
        
        # Group seasons by player id
        seasons_by_player = {}
        for season in seasons:
            player_id = str(season.get('id', ''))
            if player_id not in seasons_by_player:
                seasons_by_player[player_id] = []
            seasons_by_player[player_id].append(season)
        
        # Combine with player data
        combined = []
        for player in players:
            player_id = str(player.get('id', ''))
            player_seasons = seasons_by_player.get(player_id, [])
            
            combined_player = {
                **player,
                "seasons": player_seasons
            }
            combined.append(combined_player)
        
        return combined
