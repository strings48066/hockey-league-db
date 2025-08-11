"""
Player operations module.
Handles all player-related business logic.
"""
import os
from src.data.sheets_client import SheetsClient
from src.formatters.players import PlayerFormatter
from src.formatters.base import OutputManager
from src.utils import config


class PlayerOperations:
    """Handles player data operations."""
    
    def __init__(self, sheets_client=None):
        self.sheets_client = sheets_client or SheetsClient()
        self.formatter = PlayerFormatter()
        self.output_manager = OutputManager()
    
    def process_players(self, output_dir="./output"):
        """Process all players data."""
        print("👥 Processing players data...")
        
        try:
            # Fetch player data using config ranges
            df_players = self.sheets_client.get_range(config.PLAYERS_RANGE)
            df_season = self.sheets_client.get_range(config.PLAYERS_SEASON_RANGE)
            
            if df_players.empty:
                print("❌ No players data found")
                return self._save_status("No players data found", "no_data", output_dir)
            
            # Format data
            players = self.formatter.format_players(df_players)
            seasons = self.formatter.format_season_stats(df_season) if not df_season.empty else []
            
            if not players:
                print("⚠️  No valid player data found - likely TBD content")
                return self._save_status("No valid player data found - season may be in planning phase", 
                                       "planning", output_dir)
            
            # Combine player data with seasons
            combined_data = self.formatter.combine_player_data(players, seasons)
            
            # Save to output
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "players.json")
            self.output_manager.save_json(combined_data, output_path)
            
            print(f"✅ {len(combined_data)} players saved to {output_path}")
            return combined_data
            
        except Exception as e:
            print(f"❌ Error processing players: {e}")
            return self._save_status(f"Error processing players: {e}", "error", output_dir)
    
    def _save_status(self, message, status, output_dir):
        """Save status information for error/planning scenarios."""
        status_data = {
            "message": message,
            "status": status,
            "players": []
        }
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "players_status.json")
        self.output_manager.save_json(status_data, output_path)
        print(f"💾 Player status saved to {output_path}")
        return status_data
