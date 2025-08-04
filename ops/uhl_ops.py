"""
Unified UHL Operations Manager
Consolidates games, players, and standings operations into a single interface.
"""
import os
import sys
from sheets_client import SheetsClient
from formatters import PlayerFormatter, StandingsFormatter, OutputManager

class UHLOpsManager:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.player_formatter = PlayerFormatter()
        self.standings_formatter = StandingsFormatter()
        self.output_manager = OutputManager()
    
    def process_players(self, output_dir="./output"):
        """Process all players data"""
        print("Processing players data...")
        
        # Fetch player data (skip header row)
        range_players = "players!A2:C53"
        range_season = "players!D2:O53"
        
        df_players = self.sheets_client.get_range(range_players)
        df_season = self.sheets_client.get_range(range_season)
        
        if df_players.empty:
            print("No players data found")
            return
        
        # Format data
        players = self.player_formatter.format_players(df_players)
        seasons = self.player_formatter.format_season_stats(df_season) if not df_season.empty else []
        
        # Combine data
        combined_data = self.player_formatter.combine_player_data(players, seasons)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save output
        output_path = os.path.join(output_dir, "players.json")
        self.output_manager.save_json(combined_data, output_path)
        
        return combined_data
    
    def process_standings(self, output_dir="./output"):
        """Process standings data"""
        print("Processing standings data...")
        
        # Fetch standings data
        range_standings = "standings!A2:L5"
        df_standings = self.sheets_client.get_range(range_standings)
        
        if df_standings.empty:
            print("No standings data found")
            return
        
        # Format standings
        standings_data = self.standings_formatter.format_standings(df_standings)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save output
        output_path = os.path.join(output_dir, "standings.json")
        self.output_manager.save_json(standings_data, output_path)
        
        return standings_data
    
    def process_all(self):
        """Process all data types"""
        print("=== UHL Operations - Processing All Data ===")
        
        results = {}
        
        try:
            results['players'] = self.process_players()
            results['standings'] = self.process_standings()
            
            print("\n=== Processing Complete ===")
            print(f"Players processed: {len(results['players']) if results['players'] else 0}")
            print(f"Teams in standings: {len(results['standings']) if results['standings'] else 0}")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            return None
        
        return results

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python uhl_ops.py [players|standings|all]")
        return
    
    operation = sys.argv[1].lower()
    
    try:
        manager = UHLOpsManager()
        
        if operation == "players":
            manager.process_players()
        elif operation == "standings":
            manager.process_standings()
        elif operation == "all":
            manager.process_all()
        else:
            print("Invalid operation. Use: players, standings, or all")
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Set your Google Sheet ID: export SPREADSHEET_ID='your_sheet_id_here'")
        print("2. Make sure google-creds.json is in the ops directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
