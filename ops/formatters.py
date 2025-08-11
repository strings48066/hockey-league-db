"""
Data formatters for UHL operations.
Handles conversion from Google Sheets data to standardized JSON formats.
"""
import json
import pandas as pd

class GameFormatter:
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

    @staticmethod
    def format_all_games(df):
        """Format games schedule data from Google Sheets (handles TBD data during season startup)"""
        if df.empty:
            return {
                "message": "No games data found",
                "status": "no_data",
                "games": []
            }
        
        # Handle TBD/placeholder data during season startup
        try:
            # Expected columns from your structure
            expected_columns = ["SeasonId", "id", "Date", "Time", "Home", "Away", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore", "Ref1", "Ref2"]
            
            # If we have fewer columns than expected, it might be TBD data
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Found {len(df.columns)} columns, expected {len(expected_columns)}. Likely TBD data.")
                
                # Return empty schedule for TBD scenarios
                return {
                    "message": "Season not yet started - TBD data detected",
                    "status": "pending",
                    "games": []
                }
            
            df.columns = expected_columns
            
            # Filter out rows with TBD or empty essential data
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
            print(f"⚠️  Error processing games data (likely TBD content): {e}")
            return {
                "message": "Unable to process games data - season may not be started",
                "status": "error",
                "error": str(e),
                "games": []
            }
    
    @staticmethod
    def check_season_status(df):
        """Check if season is active, planning, or TBD"""
        if df.empty:
            return {"status": "no_data", "message": "No schedule data found", "ready_for_play": False}
        
        # Count TBD vs actual data
        tbd_count = 0
        valid_count = 0
        
        for _, row in df.iterrows():
            row_str = ' '.join(str(val) for val in row.values)
            if 'TBD' in row_str.upper() or pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                tbd_count += 1
            else:
                valid_count += 1
        
        if tbd_count > valid_count:
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
                "message": f"Season active ({valid_count} games scheduled, {tbd_count} TBD)",
                "ready_for_play": True,
                "tbd_count": tbd_count,
                "valid_count": valid_count
            }
    
    @staticmethod
    def format_game_events(df):
        """Format game events data from gameEvents sheet"""
        if df.empty:
            return []
        
        # Skip header row and set column names
        events_df = df.iloc[1:].copy()  # Skip header row
        events_df.columns = ["id", "gameId", "eventTime", "Team", "ScoredBy", "Asst1", "Asst2", "PenaltyPlayer", "Infraction", "PIM", "GWG"]
        
        # Convert to records for easier processing
        return events_df.to_dict(orient='records')
    
    @staticmethod
    def get_events_for_game(events_df, game_id):
        """Extract goals and penalties for a specific game"""
        goals = []
        penalties = []
        
        if events_df.empty:
            return {"goals": goals, "penalties": penalties}
        
        # Work with the raw dataframe without assuming column names
        # Skip header row if it exists
        data_rows = events_df.iloc[1:] if len(events_df) > 1 else events_df
        
        goal_id = 1
        penalty_id = 1
        
        for _, event_row in data_rows.iterrows():
            try:
                # Extract data by column position
                event_game_id = str(event_row.iloc[1]).strip() if len(event_row) > 1 and event_row.iloc[1] else None
                
                # Skip if not for this game
                if event_game_id != str(game_id):
                    continue
                
                event_time = str(event_row.iloc[2]).strip() if len(event_row) > 2 and event_row.iloc[2] else ""
                team = str(event_row.iloc[3]).strip() if len(event_row) > 3 and event_row.iloc[3] else ""
                scored_by = str(event_row.iloc[4]).strip() if len(event_row) > 4 and event_row.iloc[4] else ""
                asst1 = str(event_row.iloc[5]).strip() if len(event_row) > 5 and event_row.iloc[5] else ""
                asst2 = str(event_row.iloc[6]).strip() if len(event_row) > 6 and event_row.iloc[6] else ""
                penalty_player = str(event_row.iloc[7]).strip() if len(event_row) > 7 and event_row.iloc[7] else ""
                infraction = str(event_row.iloc[8]).strip() if len(event_row) > 8 and event_row.iloc[8] else ""
                pim = str(event_row.iloc[9]).strip() if len(event_row) > 9 and event_row.iloc[9] else ""
                
                # Check if this is a goal (has ScoredBy)
                if scored_by and scored_by.lower() not in ['nan', '', 'none']:
                    goal = {
                        "id": goal_id,
                        "Time": event_time,
                        "Team": team,
                        "ScoredBy": scored_by,
                        "Asst1": asst1 if asst1 and asst1.lower() not in ['nan', '', 'none'] else None,
                        "Asst2": asst2 if asst2 and asst2.lower() not in ['nan', '', 'none'] else None
                    }
                    goals.append(goal)
                    goal_id += 1
                
                # Check if this is a penalty (has PenaltyPlayer and Infraction)
                if (penalty_player and penalty_player.lower() not in ['nan', '', 'none'] and
                    infraction and infraction.lower() not in ['nan', '', 'none']):
                    
                    penalty = {
                        "id": penalty_id,
                        "Time": event_time,
                        "Team": team,
                        "Player": penalty_player,
                        "Infraction": infraction,
                        "Minutes": pim
                    }
                    penalties.append(penalty)
                    penalty_id += 1
                    
            except Exception as e:
                print(f"Error processing event row for game {game_id}: {e}")
                continue
        
        return {"goals": goals, "penalties": penalties}
    
    @staticmethod
    def extract_lineups_from_games_played(games_played_df):
        """Extract lineup data from gamesPlayed sheet organized by game ID"""
        if games_played_df.empty:
            return {}
        
        lineups_by_game = {}
        
        # Skip header row and process the actual data
        data_rows = games_played_df.iloc[1:] if len(games_played_df) > 1 else games_played_df
        
        # Group players by gameId and team
        for _, row in data_rows.iterrows():
            try:
                game_id = str(row.iloc[0]).strip() if len(row) > 0 and row.iloc[0] else None
                team = str(row.iloc[1]).strip() if len(row) > 1 and row.iloc[1] else None
                player_name = str(row.iloc[2]).strip() if len(row) > 2 and row.iloc[2] else None
                position = str(row.iloc[3]).strip() if len(row) > 3 and row.iloc[3] else ""
                jersey_number = str(row.iloc[4]).strip() if len(row) > 4 and row.iloc[4] else ""
                is_sub = str(row.iloc[5]).strip() if len(row) > 5 and row.iloc[5] else "0"
                
                # Skip invalid rows
                if not game_id or not team or not player_name or game_id == 'gameId':
                    continue
                
                # Initialize game if not exists
                if game_id not in lineups_by_game:
                    lineups_by_game[game_id] = {"Home": [], "Away": []}
                
                # Create player object
                player_obj = {
                    "id": len(lineups_by_game[game_id]["Home"]) + len(lineups_by_game[game_id]["Away"]) + 1,
                    "name": player_name,
                    "pos": position,
                    "no": jersey_number,
                    "status": "sub" if is_sub == "1" else "active",
                    "g": "0",   # Goals (would be calculated from events)
                    "a": "0",   # Assists (would be calculated from events)
                    "pts": "0", # Points (would be calculated from events)
                    "pim": "0"  # Penalty minutes (would be calculated from events)
                }
                
                # Add to appropriate team lineup
                # We need to determine if this team is Home or Away for this game
                # For now, we'll add all players to Home and determine later based on game data
                lineups_by_game[game_id]["Home"].append(player_obj)
                
            except Exception as e:
                print(f"Error processing lineup row: {e}")
                continue
        
        return lineups_by_game
    
    @staticmethod
    def build_complete_schedule(games_df, events_df, games_played_df=None):
        """Build complete schedule with games, events, and lineups"""
        complete_schedule = []
        
        # Get lineup data if available
        lineups_by_game = {}
        if games_played_df is not None and not games_played_df.empty:
            lineups_by_game = GameFormatter.extract_lineups_from_games_played(games_played_df)
        
        # Process each game
        for _, game_row in games_df.iterrows():
            try:
                # Based on debug output, the actual structure is:
                # [0]: Season ID, [1]: Game ID, [2]: Date, [3]: Time, [4]: Home Team ID, [5]: Away Team ID, 
                # [6]: Home Team Name, [7]: Away Team Name, [8]: Home Score, [9]: Away Score, [10]: Ref1, [11]: Ref2
                
                game_id = str(game_row.iloc[1])  # Game ID is in column 1, not 0
                date = str(game_row.iloc[2]) if len(game_row) > 2 else ""
                time = str(game_row.iloc[3]) if len(game_row) > 3 else ""
                home_team = str(game_row.iloc[6]) if len(game_row) > 6 else ""
                away_team = str(game_row.iloc[7]) if len(game_row) > 7 else ""
                home_score = str(game_row.iloc[8]) if len(game_row) > 8 else ""
                away_score = str(game_row.iloc[9]) if len(game_row) > 9 else ""
                ref1 = str(game_row.iloc[10]) if len(game_row) > 10 else ""
                ref2 = str(game_row.iloc[11]) if len(game_row) > 11 and game_row.iloc[11] else ""
                gamelink = str(game_row.iloc[14]) if len(game_row) > 14 else ""
                score = str(game_row.iloc[15]) if len(game_row) > 15 else ""
                played = str(game_row.iloc[16]) if len(game_row) > 16 else "N"  # Read actual Played field from sheet
                
                # If score field is empty, generate it from team names and scores
                if not score or score.strip() == '':
                    if home_score and away_score and home_score != '' and away_score != '':
                        score = f"{home_team} {home_score} - {away_score} {away_team}"
                    else:
                        score = f"{home_team}  -  {away_team}"
                
                # Get events for this game
                game_events = GameFormatter.get_events_for_game(events_df, game_id)
                
                # Get lineups for this game and organize by Home/Away
                home_lineup = []
                away_lineup = []
                
                # Process gamesPlayed data for this specific game
                if games_played_df is not None and not games_played_df.empty:
                    data_rows = games_played_df.iloc[1:] if len(games_played_df) > 1 else games_played_df
                    
                    for _, row in data_rows.iterrows():
                        try:
                            row_game_id = str(row.iloc[0]).strip() if len(row) > 0 and row.iloc[0] else None
                            team = str(row.iloc[1]).strip() if len(row) > 1 and row.iloc[1] else None
                            player_name = str(row.iloc[2]).strip() if len(row) > 2 and row.iloc[2] else None
                            position = str(row.iloc[3]).strip() if len(row) > 3 and row.iloc[3] else ""
                            jersey_number = str(row.iloc[4]).strip() if len(row) > 4 and row.iloc[4] else ""
                            is_sub = str(row.iloc[5]).strip() if len(row) > 5 and row.iloc[5] else "0"
                            
                            if row_game_id == game_id and player_name and team:
                                player_obj = {
                                    "id": len(home_lineup) + len(away_lineup) + 1,
                                    "name": player_name,
                                    "pos": position,
                                    "no": jersey_number,
                                    "status": "sub" if is_sub == "1" else "active",
                                    "g": "0",
                                    "a": "0", 
                                    "pts": "0",
                                    "pim": "0"
                                }
                                
                                # Assign to home or away based on team match
                                if team == home_team:
                                    home_lineup.append(player_obj)
                                elif team == away_team:
                                    away_lineup.append(player_obj)
                                    
                        except Exception as e:
                            continue
                
                # Create schedule entry with correct column mapping
                schedule_entry = {
                    "id": game_id,
                    "Date": date,
                    "Home": home_team,
                    "Away": away_team,
                    "Time": time,
                    "Ref1": ref1,
                    "Ref2": ref2,
                    "GameLink": gamelink if gamelink else f"/gameSummary/{int(game_id) - 1}",  # Use GameLink from sheet or calculate
                    "Score": score,
                    "Played": played,
                    "Lineups": {
                        "Home": home_lineup,
                        "Away": away_lineup
                    },
                    "Goals": game_events['goals'],
                    "Penalties": game_events['penalties']
                }
                
                complete_schedule.append(schedule_entry)
                
            except Exception as e:
                print(f"Error processing game: {e}")
                continue
        
        return complete_schedule
    
    @staticmethod
    def create_schedule_entry(game_info, home_lineup, away_lineup, goals, penalties):
        """Create a schedule entry in the format matching existing schedule.json"""
        if game_info.empty:
            raise ValueError("Game info is required")
        
        return {
            "id": str(game_info.iloc[0, 0]) if len(game_info.columns) > 0 else "",
            "Date": str(game_info.iloc[0, 1]) if len(game_info.columns) > 1 else "",
            "Home": str(game_info.iloc[0, 2]) if len(game_info.columns) > 2 else "",
            "Away": str(game_info.iloc[0, 3]) if len(game_info.columns) > 3 else "",
            "Time": str(game_info.iloc[0, 4]) if len(game_info.columns) > 4 else "",
            "Ref1": str(game_info.iloc[0, 5]) if len(game_info.columns) > 5 else "",
            "Ref2": str(game_info.iloc[0, 6]) if len(game_info.columns) > 6 else "",
            "GameLink": str(game_info.iloc[0, 7]) if len(game_info.columns) > 7 else "",
            "Score": str(game_info.iloc[0, 8]) if len(game_info.columns) > 8 else "",
            "Played": str(game_info.iloc[0, 9]) if len(game_info.columns) > 9 else "",
            "Lineups": {
                "Home": home_lineup,
                "Away": away_lineup
            },
            "Goals": goals,
            "Penalties": penalties
        }
    
    @staticmethod
    def format_penalties(df):
        """Format penalties data to match existing schedule.json structure"""
        if df.empty:
            return []
        
        penalties_df = df.iloc[:, :5].copy()  # Take first 5 columns
        if len(penalties_df.columns) == 5:
            penalties_df.columns = ["Time", "Team", "Player", "Infraction", "Minutes"]
            penalties_df.loc[:, "id"] = range(1, len(penalties_df) + 1)
            
            # Format to match existing structure with proper field names
            formatted_penalties = []
            for _, row in penalties_df.iterrows():
                penalty = {
                    "id": int(row["id"]),
                    "Time": str(row["Time"]),
                    "Team": str(row["Team"]), 
                    "Player": str(row["Player"]),
                    "Infraction": str(row["Infraction"]),
                    "Minutes": str(row["Minutes"])
                }
                formatted_penalties.append(penalty)
            return formatted_penalties
        else:
            raise ValueError(f"Expected 5 columns for penalties, but got {len(penalties_df.columns)} columns")
    
    @staticmethod
    def format_goals(df):
        """Format goals data to match existing schedule.json structure"""
        if df.empty:
            return []
        
        goals_df = df.iloc[:, :5].copy()  # Take first 5 columns
        if len(goals_df.columns) == 5:
            goals_df.columns = ["Time", "Team", "ScoredBy", "Asst1", "Asst2"]
            goals_df.loc[:, "id"] = range(1, len(goals_df) + 1)
            
            # Format to match existing structure 
            formatted_goals = []
            for _, row in goals_df.iterrows():
                goal = {
                    "id": int(row["id"]),
                    "Time": str(row["Time"]),
                    "Team": str(row["Team"]),
                    "ScoredBy": str(row["ScoredBy"]),
                    "Asst1": str(row["Asst1"]) if pd.notna(row["Asst1"]) and str(row["Asst1"]).strip() else None,
                    "Asst2": str(row["Asst2"]) if pd.notna(row["Asst2"]) and str(row["Asst2"]).strip() else None
                }
                formatted_goals.append(goal)
            return formatted_goals
        else:
            raise ValueError(f"Expected 5 columns for goals, but got {len(goals_df.columns)} columns")

class PlayerFormatter:
    @staticmethod
    def format_players(df):
        """Format basic player info with TBD handling"""
        if df.empty:
            return []
        
        try:
            if len(df.columns) < 3:
                print(f"⚠️  Warning: Expected 3 columns for players, got {len(df.columns)}. Likely TBD data.")
                return []
            
            df.columns = ["id", "FirstName", "Lastname"]
            return df[["id", "FirstName", "Lastname"]].to_dict(orient='records')
        except Exception as e:
            print(f"⚠️  Error processing players data: {e}")
            return []
    
    @staticmethod
    def format_season_stats(df):
        """Format player season statistics with TBD handling"""
        if df.empty:
            return []
        
        try:
            expected_columns = ["Team", "JerseyNumber", "Position", "GP", "G", "A", "PTS", "PIM", "GWG"]
            
            if len(df.columns) < len(expected_columns):
                print(f"⚠️  Warning: Expected {len(expected_columns)} columns for season stats, got {len(df.columns)}. Likely TBD data.")
                return []
            
            df.columns = expected_columns + (df.columns[len(expected_columns):].tolist() if len(df.columns) > len(expected_columns) else [])
            df["id"] = "1"
            return df[expected_columns + ["id"]].to_dict(orient='records')
            
        except Exception as e:
            print(f"⚠️  Error processing season stats: {e}")
            return []
    
    @staticmethod
    def combine_player_data(players, seasons):
        """Combine player info with season stats"""
        combined_data = []
        for i, player in enumerate(players):
            player_record = {
                "id": player["id"],
                "firstName": player["FirstName"],
                "lastName": player["Lastname"],
                "seasons": [seasons[i]] if i < len(seasons) else []
            }
            combined_data.append(player_record)
        return combined_data

class StandingsFormatter:
    @staticmethod
    def format_standings(df):
        """Format standings data from Google Sheets"""
        standings_data = []
        
        for index, row in df.iterrows():
            data = {
                'id': row[0],
                'Team': row[1],
                'W': row[2],
                'L': row[3],
                'T': row[4],
                'P': row[5] if len(row) > 5 else '',
                'GF': row[6] if len(row) > 6 else '',
                'GA': row[7] if len(row) > 7 else '',
                'PIM': row[8] if len(row) > 8 else '',
                'Home': row[9] if len(row) > 9 else '',
                'Away': row[10] if len(row) > 10 else '',
                'Streak': row[11] if len(row) > 11 else ''
            }
            standings_data.append(data)
        
        return standings_data

class GoalieStatsFormatter:
    @staticmethod
    def calculate_goalie_stats_from_schedule(schedule_data):
        """Calculate comprehensive goalie statistics from schedule data with deduplication"""
        from collections import defaultdict
        
        # Track all stats for each goalie across all teams
        all_goalie_data = defaultdict(lambda: defaultdict(lambda: {
            'gp': 0,
            'w': 0,
            'l': 0,
            't': 0,
            'so': 0,
            'ga': 0,
            'games': []
        }))
        
        for game in schedule_data:
            if game.get('Played', '').lower() != 'y':
                continue
                
            game_id = game.get('id', '')
            home_team = game.get('Home', '')
            away_team = game.get('Away', '')
            home_score, away_score = GoalieStatsFormatter.parse_score(game.get('Score', ''))
            
            # Find goalies in lineups
            home_goalies = GoalieStatsFormatter.find_goalies_in_lineup(game.get('Lineups', {}).get('Home', []))
            away_goalies = GoalieStatsFormatter.find_goalies_in_lineup(game.get('Lineups', {}).get('Away', []))
            
            # Process home team goalies
            for goalie in home_goalies:
                goalie_name = goalie['name']
                stats = all_goalie_data[goalie_name][home_team]
                stats['gp'] += 1
                stats['ga'] += away_score
                
                # Determine W/L/T
                if home_score > away_score:
                    stats['w'] += 1
                elif home_score < away_score:
                    stats['l'] += 1
                else:
                    stats['t'] += 1
                
                # Check for shutout
                if away_score == 0:
                    stats['so'] += 1
                    
                stats['games'].append({
                    'game_id': game_id,
                    'team': home_team,
                    'opponent': away_team,
                    'ga_in_game': away_score,
                    'result': 'W' if home_score > away_score else 'L' if home_score < away_score else 'T'
                })
            
            # Process away team goalies
            for goalie in away_goalies:
                goalie_name = goalie['name']
                stats = all_goalie_data[goalie_name][away_team]
                stats['gp'] += 1
                stats['ga'] += home_score
                
                # Determine W/L/T
                if away_score > home_score:
                    stats['w'] += 1
                elif away_score < home_score:
                    stats['l'] += 1
                else:
                    stats['t'] += 1
                
                # Check for shutout
                if home_score == 0:
                    stats['so'] += 1
                    
                stats['games'].append({
                    'game_id': game_id,
                    'team': away_team,
                    'opponent': home_team,
                    'ga_in_game': home_score,
                    'result': 'W' if away_score > home_score else 'L' if away_score < home_score else 'T'
                })
        
        # Now deduplicate: combine all stats for each goalie under their primary team
        deduplicated_stats = {}
        
        for goalie_name, team_stats in all_goalie_data.items():
            # Find primary team (team with most games played)
            primary_team = max(team_stats.keys(), key=lambda team: team_stats[team]['gp'])
            
            # Combine all stats across all teams
            combined_stats = {
                'name': goalie_name,
                'team': primary_team,
                'gp': 0,
                'w': 0,
                'l': 0,
                't': 0,
                'so': 0,
                'ga': 0,
                'gaa': 0.0,
                'games': []
            }
            
            # Sum up stats from all teams
            for team, stats in team_stats.items():
                combined_stats['gp'] += stats['gp']
                combined_stats['w'] += stats['w']
                combined_stats['l'] += stats['l']
                combined_stats['t'] += stats['t']
                combined_stats['so'] += stats['so']
                combined_stats['ga'] += stats['ga']
                combined_stats['games'].extend(stats['games'])
            
            # Calculate GAA
            if combined_stats['gp'] > 0:
                combined_stats['gaa'] = round(combined_stats['ga'] / combined_stats['gp'], 2)
            
            deduplicated_stats[goalie_name] = combined_stats
        
        return deduplicated_stats
    
    @staticmethod
    def find_goalies_in_lineup(lineup):
        """Find all goalies in a team's lineup"""
        return [player for player in lineup if player.get('pos', '').upper() == 'G']
    
    @staticmethod
    def parse_score(score_string):
        """Parse score string like 'Chicago 2 - 1 Detroit' to get home and away scores"""
        if not score_string or ' - ' not in score_string:
            return 0, 0
        
        try:
            # Split on ' - ' and extract the numbers
            parts = score_string.split(' - ')
            home_part = parts[0].strip()
            away_part = parts[1].strip()
            
            # Extract numbers from each part
            home_score = int(''.join(filter(str.isdigit, home_part.split()[-1])))
            away_score = int(''.join(filter(str.isdigit, away_part.split()[0])))
            
            return home_score, away_score
        except (ValueError, IndexError):
            return 0, 0
    
    @staticmethod
    def format_goalie_stats(goalie_stats):
        """Format deduplicated goalie stats to match player schema with seasons"""
        formatted = []
        
        # Sort goalies by GAA (ascending) then by GP (descending)
        sorted_goalies = sorted(
            [(name, stats) for name, stats in goalie_stats.items() if stats['gp'] > 0],
            key=lambda x: (x[1]['gaa'], -x[1]['gp'])
        )
        
        for i, (goalie_name, stats) in enumerate(sorted_goalies, 1):
            # Split name into first and last name
            name_parts = goalie_name.split(' ', 1)
            first_name = name_parts[0] if len(name_parts) > 0 else goalie_name
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Map team name to team ID
            team_id_map = {
                "New York": "1",
                "Detroit": "2", 
                "Chicago": "3",
                "Boston": "4"
            }
            team_id = team_id_map.get(stats['team'], "1")
            
            goalie_record = {
                "id": str(i),
                "firstName": first_name,
                "lastName": last_name,
                "seasons": [
                    {
                        "id": "1",
                        "Team": team_id,
                        "Position": "G",
                        "GP": str(stats['gp']),
                        "GS": str(stats['gp']),  # Games Started = Games Played for goalies
                        "W": str(stats['w']),
                        "L": str(stats['l']),
                        "T": str(stats['t']),
                        "SO": str(stats['so']),
                        "GA": str(stats['ga']),
                        "GAA": f"{stats['gaa']:.2f}"
                    }
                ]
            }
            
            formatted.append(goalie_record)
        
        return formatted

class OutputManager:
    @staticmethod
    def save_json(data, output_path, indent=4):
        """Save data to JSON file"""
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=indent)
        print(f"Data saved to {output_path}")
    
    @staticmethod
    def load_json(input_path):
        """Load data from JSON file"""
        try:
            with open(input_path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File not found: {input_path}")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {input_path}")
            return None
