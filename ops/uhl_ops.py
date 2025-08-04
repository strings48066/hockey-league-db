"""
Unified UHL Operations Manager
Consolidates games, players, and standings operations into a single interface.
"""
import os
import sys
from sheets_client import SheetsClient
from formatters import GameFormatter, PlayerFormatter, StandingsFormatter, GoalieStatsFormatter, OutputManager
import config

class UHLOpsManager:
    def __init__(self, player_spreadsheet_id=None, game_spreadsheet_id=None):
        self.sheets_client = SheetsClient(player_spreadsheet_id, game_spreadsheet_id)
        self.game_formatter = GameFormatter()
        self.player_formatter = PlayerFormatter()
        self.standings_formatter = StandingsFormatter()
        self.goalie_stats_formatter = GoalieStatsFormatter()
        self.output_manager = OutputManager()
    
    def process_players(self, output_dir="./output"):
        """Process all players data"""
        print("Processing players data...")
        
        # Fetch player data using config ranges
        df_players = self.sheets_client.get_range(config.PLAYERS_RANGE)
        df_season = self.sheets_client.get_range(config.PLAYERS_SEASON_RANGE)
        
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
        
        # Fetch standings data using config range
        df_standings = self.sheets_client.get_range(config.STANDINGS_RANGE)
        
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
    
    def process_single_game(self, output_dir="./output"):
        """Process a single game from game spreadsheet"""
        print("Processing single game data...")
        
        if not self.sheets_client.game_spreadsheet_id:
            print("❌ Game spreadsheet ID not provided")
            return None
        
        try:
            # Fetch game data using config ranges from game spreadsheet
            game_info = self.sheets_client.get_range(config.GAME_RANGES["game_info"], 'game')
            team1_lineup = self.sheets_client.get_range(config.GAME_RANGES["team1_lineup"], 'game')
            team2_lineup = self.sheets_client.get_range(config.GAME_RANGES["team2_lineup"], 'game')
            goals_data = self.sheets_client.get_range(config.GAME_RANGES["goals"], 'game')
            penalties_data = self.sheets_client.get_range(config.GAME_RANGES["penalties"], 'game')
            
            if game_info.empty:
                print("No game info found")
                return None
            
            # Format data
            home_lineup = self.game_formatter.format_lineups(team1_lineup)
            away_lineup = self.game_formatter.format_lineups(team2_lineup)
            goals = self.game_formatter.format_goals(goals_data)
            penalties = self.game_formatter.format_penalties(penalties_data)
            
            # Create complete game structure
            game_data = self.game_formatter.create_schedule_entry(
                game_info, home_lineup, away_lineup, goals, penalties
            )
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save output
            output_path = os.path.join(output_dir, "game_output.json")
            self.output_manager.save_json(game_data, output_path)
            
            return game_data
            
        except Exception as e:
            print(f"Error processing game: {e}")
            return None
    
    def process_all_games(self, output_dir="./output"):
        """Process all games from player spreadsheet"""
        print("Processing all games data...")
        
        # Fetch games data from player spreadsheet using config range
        df_games = self.sheets_client.get_range(config.GAMES_RANGE)
        
        if df_games.empty:
            print("No games data found")
            return None
        
        # Format games data
        games_data = self.game_formatter.format_all_games(df_games)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save output
        output_path = os.path.join(output_dir, "all_games.json")
        self.output_manager.save_json(games_data, output_path)
        
        return games_data
    
    def analyze_game_events(self, output_dir="./output"):
        """Analyze game events data from main spreadsheet"""
        print("Analyzing game events data...")
        
        # Fetch game events data from player spreadsheet using config range
        df_events = self.sheets_client.get_range(config.GAME_EVENTS_RANGE)
        
        if df_events.empty:
            print("No game events data found")
            return None
        
        print(f"Game events data shape: {df_events.shape}")
        print(f"Columns: {len(df_events.columns)}")
        
        # Show first few rows for analysis
        print("\nFirst 5 rows of game events data:")
        for i in range(min(5, len(df_events))):
            row_data = []
            for j in range(min(10, len(df_events.columns))):  # Show first 10 columns
                try:
                    val = df_events.iloc[i, j]
                    row_data.append(str(val)[:15] if val is not None else "None")
                except:
                    row_data.append("ERROR")
            print(f"Row {i}: {row_data}")
        
        # Save raw data for analysis
        raw_data = df_events.to_dict(orient='records')
        output_path = os.path.join(output_dir, "game_events_raw.json")
        os.makedirs(output_dir, exist_ok=True)
        self.output_manager.save_json(raw_data, output_path)
        
        return raw_data
    
    def build_complete_schedule(self, output_dir="./output"):
        """Build complete schedule.json matching the existing format"""
        print("Building complete schedule with games, events, and lineups...")
        
        # Fetch games data
        df_games = self.sheets_client.get_range(config.GAMES_RANGE)
        if df_games.empty:
            print("No games data found")
            return None
        
        # Fetch game events data  
        df_events = self.sheets_client.get_range(config.GAME_EVENTS_RANGE)
        if df_events.empty:
            print("No game events data found")
            return None
        
        # Fetch gamesPlayed data for lineups
        df_games_played = None
        try:
            df_games_played = self.sheets_client.get_range(config.GAMES_PLAYED_RANGE)
            if df_games_played.empty:
                print("⚠️  No gamesPlayed data found - lineups will be empty")
            else:
                print(f"Found gamesPlayed data with {len(df_games_played)} rows")
        except Exception as e:
            print(f"⚠️  Could not fetch gamesPlayed data: {e} - lineups will be empty")
        
        print(f"Processing {len(df_games)} games and {len(df_events)-1} events...")
        
        # Build complete schedule with lineup data
        schedule_data = self.game_formatter.build_complete_schedule(df_games, df_events, df_games_played)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save output
        output_path = os.path.join(output_dir, "schedule.json")
        self.output_manager.save_json(schedule_data, output_path)
        
        print(f"Generated complete schedule with {len(schedule_data)} games")
        return schedule_data
    
    def calculate_goalie_stats(self, output_dir="./output"):
        """Calculate goalie statistics from existing schedule.json"""
        print("Calculating goalie statistics from schedule.json...")
        
        # Load schedule data
        schedule_path = os.path.join(output_dir, "schedule.json")
        schedule_data = self.output_manager.load_json(schedule_path)
        
        if not schedule_data:
            print("No schedule data found. Please generate schedule first.")
            return None
        
        # Calculate goalie stats
        goalie_stats = self.goalie_stats_formatter.calculate_goalie_stats_from_schedule(schedule_data)
        formatted_stats = self.goalie_stats_formatter.format_goalie_stats(goalie_stats)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save output
        output_path = os.path.join(output_dir, "goalie_stats.json")
        self.output_manager.save_json(formatted_stats, output_path)
        
        # Print summary
        print(f"\nCalculated statistics for {len(formatted_stats)} goalies:")
        print(f"{'Name':<20} {'Team':<10} {'GP':<3} {'W':<3} {'L':<3} {'T':<3} {'SO':<3} {'GA':<3} {'GAA':<5} {'Record':<8}")
        print("-" * 80)
        
        for stats in formatted_stats[:10]:  # Show top 10
            print(f"{stats['name']:<20} {stats['team']:<10} {stats['gp']:<3} {stats['w']:<3} {stats['l']:<3} {stats['t']:<3} {stats['so']:<3} {stats['ga']:<3} {stats['gaa']:<5} {stats['record']:<8}")
        
        if len(formatted_stats) > 10:
            print(f"... and {len(formatted_stats) - 10} more goalies")
        
        return formatted_stats

    def process_all(self, include_games=False):
        """Process all data types"""
        print("=== UHL Operations - Processing All Data ===")
        
        results = {}
        
        try:
            results['players'] = self.process_players()
            results['standings'] = self.process_standings()
            
            if include_games:
                results['all_games'] = self.process_all_games()
                if self.sheets_client.game_spreadsheet_id:
                    results['single_game'] = self.process_single_game()
            
            print("\n=== Processing Complete ===")
            print(f"Players processed: {len(results['players']) if results['players'] else 0}")
            print(f"Teams in standings: {len(results['standings']) if results['standings'] else 0}")
            if include_games:
                print(f"All games processed: {len(results['all_games']) if results.get('all_games') else 0}")
                print(f"Single game processed: {'Yes' if results.get('single_game') else 'No'}")
            
        except Exception as e:
            print(f"Error during processing: {e}")
            return None
        
        return results

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python uhl_ops.py [players|standings|games|single-game|all-games|game-events|schedule|goalie-stats|all] [player_sheet_id] [game_sheet_id]")
        print("Examples:")
        print("  python uhl_ops.py players")
        print("  python uhl_ops.py schedule              # Generate complete schedule.json")
        print("  python uhl_ops.py goalie-stats          # Calculate goalie statistics from schedule.json")
        print("  python uhl_ops.py game-events")
        print("  python uhl_ops.py single-game <player_sheet_id> <game_sheet_id>") 
        print("  python uhl_ops.py all <player_sheet_id>")
        return
    
    operation = sys.argv[1].lower()
    
    # Get optional spreadsheet IDs from command line
    player_sheet_id = sys.argv[2] if len(sys.argv) > 2 else None
    game_sheet_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        manager = UHLOpsManager(player_sheet_id, game_sheet_id)
        
        if operation == "players":
            manager.process_players()
        elif operation == "standings":
            manager.process_standings()
        elif operation == "games" or operation == "all-games":
            manager.process_all_games()
        elif operation == "game-events":
            manager.analyze_game_events()
        elif operation == "schedule":
            manager.build_complete_schedule()
        elif operation == "goalie-stats" or operation == "goalies":
            manager.calculate_goalie_stats()
        elif operation == "single-game":
            if not game_sheet_id:
                print("❌ Game spreadsheet ID required for single-game processing")
                print("Usage: python uhl_ops.py single-game <player_sheet_id> <game_sheet_id>")
                return
            manager.process_single_game()
        elif operation == "all":
            manager.process_all(include_games=True)
        else:
            print("Invalid operation. Use: players, standings, games, single-game, all-games, game-events, schedule, goalie-stats, or all")
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nTo fix this:")
        print("1. Set your Google Sheet IDs via command line arguments or .env file")
        print("2. Make sure service-account-key.json is in the ops directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
