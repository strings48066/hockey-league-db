"""
Standings operations module.
Handles team standings business logic.
"""
import os
from src.data.sheets_client import SheetsClient
from src.formatters.goalie_stats import StandingsFormatter, GoalieStatsFormatter
from src.formatters.base import OutputManager
from src.utils import config


class StandingsOperations:
    """Handles standings operations."""
    
    def __init__(self, sheets_client=None):
        self.sheets_client = sheets_client or SheetsClient()
        self.formatter = StandingsFormatter()
        self.output_manager = OutputManager()
    
    def process_standings(self, output_dir="./output"):
        """Process team standings data."""
        print("Processing standings data...")
        
        try:
            # Fetch standings data
            df_standings = self.sheets_client.get_range(config.STANDINGS_RANGE)
            
            if df_standings.empty:
                print("❌ No standings data found")
                return []
            
            # Format standings data
            standings = self.formatter.format_standings(df_standings)
            
            if not standings:
                print("⚠️  No valid standings data found")
                return []
            
            # Save to output
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "standings.json")
            self.output_manager.save_json(standings, output_path)
            
            print(f"✅ Standings data saved to {output_path}")
            return standings
            
        except Exception as e:
            print(f"❌ Error processing standings: {e}")
            return []


class GoalieStatsOperations:
    """Handles goalie statistics operations."""
    
    def __init__(self):
        self.formatter = GoalieStatsFormatter()
        self.output_manager = OutputManager()
    
    def calculate_goalie_stats(self, schedule_file_path="./output/schedule.json", output_dir="./output"):
        """Calculate goalie statistics from schedule data."""
        print("Calculating goalie statistics from schedule.json...")
        
        try:
            if not os.path.exists(schedule_file_path):
                print(f"❌ Schedule file not found: {schedule_file_path}")
                return []
            
            # Calculate stats
            goalie_stats = self.formatter.calculate_goalie_stats_from_schedule(schedule_file_path)
            
            if not goalie_stats:
                print("⚠️  No goalie statistics calculated")
                return []
            
            # Save to output
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "goalie_stats.json")
            self.output_manager.save_json(goalie_stats, output_path)
            
            # Print summary
            print(f"\nCalculated statistics for {len(goalie_stats)} goalies:")
            print("Name                 Team       GP  W   L   T   SO  GA  GAA   Record  ")
            print("-" * 80)
            
            for goalie in goalie_stats:
                record = f"{goalie['W']}-{goalie['L']}-{goalie['T']}"
                print(f"{goalie['name']:<20} {goalie['team']:<10} {goalie['GP']:<3} {goalie['W']:<3} "
                      f"{goalie['L']:<3} {goalie['T']:<3} {goalie['SO']:<3} {goalie['GA']:<3} "
                      f"{goalie['GAA']:<5.2f} {record:<7}")
            
            return goalie_stats
            
        except Exception as e:
            print(f"❌ Error calculating goalie stats: {e}")
            return []
