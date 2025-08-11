"""
Goalie statistics formatters.
"""
import json
from .base import BaseFormatter


class GoalieStatsFormatter(BaseFormatter):
    """Handles formatting and calculation of goalie statistics."""
    
    @classmethod
    def calculate_goalie_stats_from_schedule(cls, schedule_file_path):
        """Calculate goalie statistics from schedule.json file."""
        try:
            with open(schedule_file_path, 'r') as f:
                schedule_data = json.load(f)
            
            goalie_stats = {}
            
            for game in schedule_data:
                # Only process played games
                if game.get('Played', '').lower() != 'y':
                    continue
                
                home_team = game.get('Home', '')
                away_team = game.get('Away', '')
                home_lineup = game.get('Lineups', {}).get('Home', [])
                away_lineup = game.get('Lineups', {}).get('Away', [])
                goals = game.get('Goals', [])
                
                # Find goalies in lineups
                home_goalie = cls._find_goalie_in_lineup(home_lineup)
                away_goalie = cls._find_goalie_in_lineup(away_lineup)
                
                if not home_goalie and not away_goalie:
                    continue
                
                # Calculate goals against for each team
                home_goals_against = len([g for g in goals if g.get('Team') != home_team])
                away_goals_against = len([g for g in goals if g.get('Team') != away_team])
                
                # Determine winner
                home_goals_for = len([g for g in goals if g.get('Team') == home_team])
                away_goals_for = len([g for g in goals if g.get('Team') == away_team])
                
                # Process home goalie
                if home_goalie:
                    cls._update_goalie_stats(
                        goalie_stats, home_goalie, home_team,
                        home_goals_for, away_goals_for, home_goals_against
                    )
                
                # Process away goalie
                if away_goalie:
                    cls._update_goalie_stats(
                        goalie_stats, away_goalie, away_team,
                        away_goals_for, home_goals_for, away_goals_against
                    )
            
            # Convert to list format
            stats_list = []
            for goalie_name, stats in goalie_stats.items():
                stats_list.append({
                    "name": goalie_name,
                    "team": stats["team"],
                    "GP": stats["GP"],
                    "GS": stats["GS"],
                    "W": stats["W"],
                    "L": stats["L"],
                    "T": stats["T"],
                    "SO": stats["SO"],
                    "GA": stats["GA"],
                    "GAA": round(stats["GA"] / max(stats["GP"], 1), 2)
                })
            
            return stats_list
            
        except Exception as e:
            print(f"Error calculating goalie stats: {e}")
            return []
    
    @staticmethod
    def _find_goalie_in_lineup(lineup):
        """Find the goalie in a team lineup."""
        for player in lineup:
            if player.get('pos') == 'G':
                return player.get('name')
        return None
    
    @staticmethod
    def _update_goalie_stats(goalie_stats, goalie_name, team, goals_for, goals_against_team, goals_against):
        """Update statistics for a specific goalie."""
        if goalie_name not in goalie_stats:
            goalie_stats[goalie_name] = {
                "team": team,
                "GP": 0,
                "GS": 0,
                "W": 0,
                "L": 0,
                "T": 0,
                "SO": 0,
                "GA": 0
            }
        
        stats = goalie_stats[goalie_name]
        stats["GP"] += 1
        stats["GS"] += 1
        stats["GA"] += goals_against
        
        # Determine game result
        if goals_for > goals_against_team:
            stats["W"] += 1
        elif goals_for < goals_against_team:
            stats["L"] += 1
        else:
            stats["T"] += 1
        
        # Check for shutout
        if goals_against == 0:
            stats["SO"] += 1


class StandingsFormatter(BaseFormatter):
    """Handles formatting of team standings data."""
    
    @classmethod
    def format_standings(cls, df):
        """Format standings data from Google Sheets."""
        empty_check = cls.handle_empty_data(df, "standings")
        if empty_check:
            return empty_check.get("data", [])
        
        try:
            # Check for TBD content
            if cls.check_tbd_content(df):
                print("⚠️  Warning: Standings data contains TBD content")
                return []
            
            expected_columns = ["id", "Team", "W", "L", "T", "P", "GF", "GA", "PIM", "Home", "Away", "Streak"]
            
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Found {len(df.columns)} columns for standings, expected {len(expected_columns)}")
                return []
            
            df_standings = df.iloc[:, :len(expected_columns)].copy()
            df_standings.columns = expected_columns
            
            # Remove rows with missing essential data
            df_standings = df_standings.dropna(subset=['Team'])
            
            return df_standings.to_dict(orient='records')
            
        except Exception as e:
            print(f"⚠️  Error processing standings data: {e}")
            return []
