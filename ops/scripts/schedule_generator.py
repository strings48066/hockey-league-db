#!/usr/bin/env python3
"""
UHL Schedule Generator for 2025-2026 Season
Generates schedule starting weekend after Labor Day through second Sunday in March
"""

import json
import datetime
from datetime import timedelta
import csv

class ScheduleGenerator:
    def __init__(self):
        # Team mappings from your existing data
        self.teams = {
            "1": "New York",
            "2": "Detroit", 
            "3": "Chicago",
            "4": "Boston"
        }
        self.team_ids = ["1", "2", "3", "4"]
        self.time_slots = ["7:45 PM", "8:45 PM"]
        
    def get_season_dates(self, year=2025):
        """Calculate season start and end dates"""
        # Labor Day is first Monday in September
        labor_day = self.get_labor_day(year)
        
        # Start weekend after Labor Day (first Sunday)
        start_date = labor_day + timedelta(days=6)  # Sunday after Labor Day
        
        # End on second Sunday in March of next year
        march_first = datetime.date(year + 1, 3, 1)
        # Find first Sunday in March
        days_to_sunday = (6 - march_first.weekday()) % 7
        first_sunday = march_first + timedelta(days=days_to_sunday)
        # Second Sunday is 7 days later
        end_date = first_sunday + timedelta(days=7)
        
        return start_date, end_date
    
    def get_labor_day(self, year):
        """Get Labor Day date (first Monday in September)"""
        sept_first = datetime.date(year, 9, 1)
        # Find first Monday
        days_to_monday = (7 - sept_first.weekday()) % 7
        if days_to_monday == 0:  # If Sept 1 is Monday
            return sept_first
        else:
            return sept_first + timedelta(days=days_to_monday)
    
    def generate_game_dates(self, start_date, end_date):
        """Generate all game dates (Sundays only, based on your current schedule)"""
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            # Only add Sundays (weekday 6)
            if current_date.weekday() == 6:
                dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def generate_balanced_matchups(self):
        """Generate balanced schedule ensuring fair home/away distribution"""
        matchups = []
        
        # Create a more balanced approach
        # Each team should play each other team approximately the same number of times
        # With 4 teams and 54 games, each team plays ~13-14 games
        
        teams = self.team_ids.copy()
        
        # Generate multiple rounds to get 54 games
        for round_num in range(15):  # 15 rounds should give us plenty
            for i, home_team in enumerate(teams):
                for j, away_team in enumerate(teams):
                    if home_team != away_team:
                        # Rotate who's home/away to ensure balance
                        if (round_num + i + j) % 2 == 0:
                            matchups.append((home_team, away_team))
                        else:
                            matchups.append((away_team, home_team))
        
        # Take first 54 games
        return matchups[:54]
    
    def generate_google_sheets_data(self):
        """Generate data for Google Sheets with initial fields only"""
        start_date, end_date = self.get_season_dates(2025)
        game_dates = self.generate_game_dates(start_date, end_date)
        matchups = self.generate_balanced_matchups()
        
        # Basic headers for initial Google Sheets setup
        headers = ["id", "Date", "Time", "HomeTeamID", "AwayTeamID", "Home", "Away"]
        
        rows = [headers]  # Start with headers
        game_id = 1
        
        print(f"Season dates: {start_date} to {end_date}")
        print(f"Game dates available: {len(game_dates)}")
        print(f"Need to schedule: 54 games")
        
        # Generate 2 games per date (27 dates × 2 games = 54 games)
        date_idx = 0
        while game_id <= 54 and date_idx < len(game_dates):
            game_date = game_dates[date_idx]
            
            for time_slot in self.time_slots:
                if game_id > 54:
                    break
                    
                if game_id - 1 < len(matchups):
                    home_team_id, away_team_id = matchups[game_id - 1]
                    home_team = self.teams[home_team_id]
                    away_team = self.teams[away_team_id]
                    
                    row = [
                        str(game_id),  # id
                        game_date.strftime("%m-%d-%Y"),  # Date
                        time_slot,  # Time
                        home_team_id,  # HomeTeamID
                        away_team_id,  # AwayTeamID
                        home_team,  # Home
                        away_team   # Away
                    ]
                    
                    rows.append(row)
                    game_id += 1
            
            date_idx += 1
        
        return rows
    
    def save_csv_schedule(self, filename="2025_2026_schedule.csv"):
        """Generate and save schedule as CSV for Google Sheets import"""
        rows = self.generate_google_sheets_data()
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"\n=== Schedule Generation Complete ===")
        print(f"Generated {len(rows)-1} games for the 2025-2026 season")
        print(f"Season runs from {rows[1][1]} to {rows[-1][1]}")
        print(f"CSV saved to: {filename}")
        print(f"\nTo import to Google Sheets:")
        print(f"1. Open Google Sheets")
        print(f"2. File > Import > Upload > {filename}")
        print(f"3. Choose 'Replace spreadsheet' or 'Insert new sheet'")
        
        # Print first few games for verification
        print(f"\nFirst 5 games:")
        print("ID | Date       | Time     | Home vs Away")
        print("-" * 45)
        for i in range(1, min(6, len(rows))):
            row = rows[i]
            print(f"{row[0]:<2} | {row[1]:<10} | {row[2]:<8} | {row[5]} vs {row[6]}")
        
        return rows
    
    def print_season_summary(self):
        """Print summary of the season schedule"""
        start_date, end_date = self.get_season_dates(2025)
        game_dates = self.generate_game_dates(start_date, end_date)
        matchups = self.generate_balanced_matchups()
        
        print(f"\n=== 2025-2026 UHL Season Summary ===")
        print(f"Labor Day 2025: {self.get_labor_day(2025)}")
        print(f"Season Start: {start_date} (Sunday after Labor Day)")
        print(f"Season End: {end_date} (Second Sunday in March)")
        print(f"Total Sundays: {len(game_dates)}")
        print(f"Total Games: 54 (2 games per Sunday)")
        print(f"Teams: {', '.join(self.teams.values())}")
        
        # Count games per team
        home_games = {team_id: 0 for team_id in self.team_ids}
        away_games = {team_id: 0 for team_id in self.team_ids}
        
        for home_id, away_id in matchups:
            home_games[home_id] += 1
            away_games[away_id] += 1
        
        print(f"\nGames per team:")
        for team_id in self.team_ids:
            team_name = self.teams[team_id]
            total = home_games[team_id] + away_games[team_id]
            print(f"  {team_name}: {total} games ({home_games[team_id]} home, {away_games[team_id]} away)")

def main():
    generator = ScheduleGenerator()
    
    # Print season summary
    generator.print_season_summary()
    
    # Generate CSV for Google Sheets
    filename = "/Users/strings48066/git/github/hockey-league-db/ops/output/2025_2026_schedule.csv"
    generator.save_csv_schedule(filename)

if __name__ == "__main__":
    main()
