"""
Unified UHL Operations Manager
Consolidates games, players, and standings operations into a single interface.
"""
import os
import sys
from sheets_client import SheetsClient
from formatters import GameFormatter, PlayerFormatter, StandingsFormatter, GoalieStatsFormatter, OutputManager
from config import settings as config

class UHLOpsManager:
    def __init__(self, player_spreadsheet_id=None, game_spreadsheet_id=None):
        self.sheets_client = SheetsClient(player_spreadsheet_id, game_spreadsheet_id)
        self.game_formatter = GameFormatter()
        self.player_formatter = PlayerFormatter()
        self.standings_formatter = StandingsFormatter()
        self.goalie_stats_formatter = GoalieStatsFormatter()
        self.output_manager = OutputManager()
    
    def process_players(self, output_dir="./output"):
        """Process all players data with TBD handling"""
        print("👥 Processing players data...")
        
        try:
            # Fetch player data using config ranges
            df_players = self.sheets_client.get_range(config.PLAYERS_RANGE)
            df_season = self.sheets_client.get_range(config.PLAYERS_SEASON_RANGE)
            
            if df_players.empty:
                print("❌ No players data found")
                return None
            
            # Format data (handles TBD gracefully)
            players = self.player_formatter.format_players(df_players)
            seasons = self.player_formatter.format_season_stats(df_season) if not df_season.empty else []
            
            # Check if we got valid data
            if not players:
                print("⚠️  No valid player data found - likely TBD content")
                # Save status for TBD scenarios
                status_data = {
                    "message": "No valid player data found - season may be in planning phase",
                    "status": "planning",
                    "players": []
                }
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "players_status.json")
                self.output_manager.save_json(status_data, output_path)
                print(f"💾 Player status saved to {output_path}")
                return status_data
            
            # Combine data
            combined_data = self.player_formatter.combine_player_data(players, seasons)
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save output
            output_path = os.path.join(output_dir, "players.json")
            self.output_manager.save_json(combined_data, output_path)
            print(f"✅ {len(combined_data)} players saved to {output_path}")
            
            return combined_data
            
        except Exception as e:
            print(f"❌ Error processing players: {e}")
            # Save error status
            error_status = {
                "status": "error",
                "message": "Failed to process players data - likely TBD content or data structure mismatch",
                "error": str(e),
                "players": []
            }
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "players_status.json")
            self.output_manager.save_json(error_status, output_path)
            print(f"💾 Error status saved to {output_path}")
            return error_status
    
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
        """Process all games from player spreadsheet with TBD handling"""
        print("🏒 Processing games schedule...")
        
        try:
            # Fetch games data from player spreadsheet using config range
            df_games = self.sheets_client.get_range(config.GAMES_RANGE)
            
            if df_games.empty:
                print("❌ No games data found")
                return None
            
            # Check season status first
            season_status = GameFormatter.check_season_status(df_games)
            print(f"📊 Season Status: {season_status['message']}")
            
            # Format games data (handles TBD gracefully)
            games_data = self.game_formatter.format_all_games(df_games)
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save output with status information
            if games_data.get('status') in ['pending', 'planning', 'error']:
                # Save status for TBD scenarios
                output_path = os.path.join(output_dir, "games_status.json")
                self.output_manager.save_json(games_data, output_path)
                print(f"💾 Season status saved to {output_path}")
                print(f"ℹ️  Status: {games_data['status']} - {games_data['message']}")
            else:
                # Save normal games data
                output_path = os.path.join(output_dir, "all_games.json")
                self.output_manager.save_json(games_data, output_path)
                game_count = len(games_data.get('games', []))
                print(f"✅ {game_count} games saved to {output_path}")
            
            return games_data
            
        except Exception as e:
            print(f"❌ Error processing games: {e}")
            # Save error status
            error_status = {
                "status": "error",
                "message": "Failed to process games data - likely TBD content or data structure mismatch",
                "error": str(e),
                "ready_for_play": False
            }
            
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "games_status.json")
            self.output_manager.save_json(error_status, output_path)
            print(f"💾 Error status saved to {output_path}")
            return error_status
    
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
            print("No game events data found - schedule will be created with empty goals/penalties")
            # Create empty dataframe for events processing
            import pandas as pd
            df_events = pd.DataFrame()
        
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
    
    def create_initial_schedule(self, output_dir="./output"):
        """Create initial schedule.json from Google Sheets games data matching existing format"""
        print("📅 Creating initial schedule from Google Sheets games data...")
        
        try:
            import pandas as pd
            
            # Read from Google Sheets games range instead of CSV
            df_games = self.sheets_client.get_range(config.GAMES_RANGE)
            
            if df_games.empty:
                print("❌ No games data found in Google Sheets")
                return None
            
            print(f"📊 Loaded {len(df_games)} games from Google Sheets")
            print(f"📋 Columns found: {len(df_games.columns)}")
            print(f"🔍 Column headers: {list(df_games.columns)}")
            print(f"🔍 First row data: {df_games.iloc[0].tolist() if not df_games.empty else 'No data'}")
            
            # Map the actual column structure based on what we found
            if len(df_games.columns) == 8:
                # Basic structure: [SeasonID?, GameID, Date, Time, HomeTeamID, AwayTeamID, Home, Away]
                df_games.columns = ["SeasonID", "id", "Date", "Time", "HomeTeamID", "AwayTeamID", "Home", "Away"]
                # Add missing columns with defaults
                df_games["Played"] = "N"  # Default for new season
                df_games["Ref1"] = "TBD"
                df_games["Ref2"] = ""
                df_games["Score"] = ""
            elif len(df_games.columns) == 17:
                # Structure with Played column at the end
                df_games.columns = ["SeasonID", "id", "Date", "Time", "HomeTeamID", "AwayTeamID", "Home", "Away"] + [f"Col{i}" for i in range(8, 16)] + ["Played"]
                # Add missing columns
                df_games["Ref1"] = "TBD"
                df_games["Ref2"] = ""
                df_games["Score"] = ""
            elif len(df_games.columns) == 21:
                # Full structure with all game data
                df_games.columns = [
                    "SeasonID", "id", "Date", "Time", "HomeTeamID", "AwayTeamID", "Home", "Away",
                    "HomeScore", "AwayScore", "Ref1", "Ref2", "Col12", "Col13", "GameLink", "Score", "Played",
                    "Col17", "Col18", "Col19", "Col20"
                ]
            elif len(df_games.columns) >= 9:
                # Try to map with Played column if it exists
                df_games.columns = ["SeasonID", "id", "Date", "Time", "HomeTeamID", "AwayTeamID", "Home", "Away", "Played"] + [f"Col{i}" for i in range(9, len(df_games.columns))]
                # Add missing columns
                if "Ref1" not in df_games.columns:
                    df_games["Ref1"] = "TBD"
                if "Ref2" not in df_games.columns:
                    df_games["Ref2"] = ""
                if "Score" not in df_games.columns:
                    df_games["Score"] = ""
            else:
                print(f"⚠️  Unexpected column count: {len(df_games.columns)}")
                # Fallback to CSV method
                return self._create_schedule_from_csv(output_dir)
            
            # Convert to schedule.json format matching existing structure
            schedule_games = []
            
            for _, row in df_games.iterrows():
                # Skip empty or invalid rows
                if pd.isna(row.get('id')) or str(row.get('id')).strip() == '':
                    continue
                
                # Debug output for first few games
                if len(schedule_games) < 3:
                    print(f"🔍 Processing game {row['id']}: Ref1={row.get('Ref1')}, Score={row.get('Score')}, Played={row.get('Played')}")
                
                # Create schedule entry matching your exact format
                game_entry = {
                    "id": str(row['id']),           # String ID like existing format
                    "Date": str(row['Date']),       # Date from sheet
                    "Home": str(row['Home']),       # Home team from sheet
                    "Away": str(row['Away']),       # Away team from sheet  
                    "Time": str(row['Time']),       # Time from sheet
                    "Ref1": str(row.get('Ref1', 'TBD')),     # Ref1 from sheet or TBD
                    "Ref2": str(row.get('Ref2', '')),        # Ref2 from sheet or empty
                    "GameLink": str(row.get('GameLink', f"/gameSummary/{int(float(str(row['id']))) - 1}")),  # GameLink from sheet or calculated
                    "Score": str(row.get('Score', '')),      # Score from sheet or empty
                    "Played": str(row.get('Played', 'N')),   # Played status from sheet (preserve case)
                    # Empty structures for future game data
                    "Lineups": {
                        "Home": [],
                        "Away": []
                    },
                    "Goals": [],
                    "Penalties": []
                }
                schedule_games.append(game_entry)
            
            if not schedule_games:
                print("❌ No valid games found after processing")
                return None
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as schedule.json (simple array format like existing)
            output_path = os.path.join(output_dir, "schedule.json")
            self.output_manager.save_json(schedule_games, output_path)
            print(f"✅ Initial schedule created: {output_path}")
            print(f"📋 Format: Array of {len(schedule_games)} games")
            print(f"📅 Date range: {schedule_games[0]['Date']} to {schedule_games[-1]['Date']}")
            
            # Show Played status summary
            played_count = sum(1 for game in schedule_games if game.get('Played', 'N') == 'Y')
            scheduled_count = len(schedule_games) - played_count
            print(f"🎮 Games played: {played_count}, Scheduled: {scheduled_count}")
            
            return schedule_games
            
        except Exception as e:
            print(f"❌ Error creating initial schedule: {e}")
            print("💡 Fallback: Using generated CSV data...")
            
            # Fallback to CSV method
            return self._create_schedule_from_csv(output_dir)
    
    def _create_schedule_from_csv(self, output_dir="./output"):
        """Fallback method to create schedule from CSV when Google Sheets fails"""
        try:
            import pandas as pd
            
            # Read the generated CSV schedule
            csv_path = os.path.join(output_dir, "2025_2026_schedule.csv")
            
            if not os.path.exists(csv_path):
                print(f"❌ Generated schedule CSV not found at {csv_path}")
                return None
            
            # Load CSV data
            df = pd.read_csv(csv_path)
            print(f"📊 Loaded {len(df)} games from generated schedule CSV")
            
            # Convert to schedule.json format matching existing structure
            schedule_games = []
            
            for _, row in df.iterrows():
                game_entry = {
                    "id": str(row['id']),
                    "Date": row['Date'],
                    "Home": row['Home'],
                    "Away": row['Away'],
                    "Time": row['Time'],
                    "Ref1": "TBD",
                    "Ref2": "",
                    "GameLink": f"/gameSummary/{row['id'] - 1}",
                    "Score": "",
                    "Played": "N",  # Default for new season
                    "Lineups": {"Home": [], "Away": []},
                    "Goals": [],
                    "Penalties": []
                }
                schedule_games.append(game_entry)
            
            return schedule_games
            
        except Exception as e:
            print(f"❌ CSV fallback also failed: {e}")
            return None
    
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
        
        # Team ID to name mapping
        team_names = {
            "1": "New York",
            "2": "Detroit", 
            "3": "Chicago",
            "4": "Boston"
        }
        
        for stats in formatted_stats[:10]:  # Show top 10
            full_name = f"{stats['firstName']} {stats['lastName']}"
            season = stats['seasons'][0] if stats['seasons'] else {}
            team_name = team_names.get(season.get('Team', ''), 'Unknown')
            gp = season.get('GP', '0')
            w = season.get('W', '0')
            l = season.get('L', '0')
            t = season.get('T', '0')
            so = season.get('SO', '0')
            ga = season.get('GA', '0')
            gaa = season.get('GAA', '0.00')
            record = f"{w}-{l}-{t}"
            
            print(f"{full_name:<20} {team_name:<10} {gp:<3} {w:<3} {l:<3} {t:<3} {so:<3} {ga:<3} {gaa:<5} {record:<8}")
        
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
        print("Usage: python uhl_ops.py [players|standings|games|single-game|all-games|game-events|schedule|create-schedule|goalie-stats|all] [player_sheet_id] [game_sheet_id]")
        print("Examples:")
        print("  python uhl_ops.py players")
        print("  python uhl_ops.py schedule              # Generate complete schedule.json")
        print("  python uhl_ops.py create-schedule       # Create initial schedule.json from generated CSV")
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
        elif operation == "create-schedule" or operation == "initial-schedule":
            manager.create_initial_schedule()
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
