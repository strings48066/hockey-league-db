"""
Goalie Statistics Calculator
Extracts goalie data from schedule.json and calculates GP, W, L, T, SO, GA, GAA
"""
import json
from collections import defaultdict

def calculate_goalie_stats(schedule_data):
    """Calculate comprehensive goalie statistics from schedule data"""
    goalie_stats = defaultdict(lambda: {
        'name': '',
        'team': '',
        'gp': 0,
        'w': 0,
        'l': 0,
        't': 0,
        'so': 0,
        'ga': 0,
        'gaa': 0.0,
        'games': []
    })
    
    for game in schedule_data:
        if game.get('Played') != 'Y':
            continue
            
        game_id = game.get('id', '')
        home_team = game.get('Home', '')
        away_team = game.get('Away', '')
        home_score, away_score = parse_score(game.get('Score', ''))
        
        # Find goalies in lineups
        home_goalies = find_goalies_in_lineup(game.get('Lineups', {}).get('Home', []))
        away_goalies = find_goalies_in_lineup(game.get('Lineups', {}).get('Away', []))
        
        # Process home team goalies
        for goalie in home_goalies:
            key = f"{goalie['name']}_{home_team}"
            stats = goalie_stats[key]
            stats['name'] = goalie['name']
            stats['team'] = home_team
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
                'opponent': away_team,
                'ga_in_game': away_score,
                'result': 'W' if home_score > away_score else 'L' if home_score < away_score else 'T'
            })
        
        # Process away team goalies
        for goalie in away_goalies:
            key = f"{goalie['name']}_{away_team}"
            stats = goalie_stats[key]
            stats['name'] = goalie['name']
            stats['team'] = away_team
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
                'opponent': home_team,
                'ga_in_game': home_score,
                'result': 'W' if away_score > home_score else 'L' if away_score < home_score else 'T'
            })
    
    # Calculate GAA for each goalie
    for stats in goalie_stats.values():
        if stats['gp'] > 0:
            stats['gaa'] = round(stats['ga'] / stats['gp'], 2)
    
    return dict(goalie_stats)

def find_goalies_in_lineup(lineup):
    """Find all goalies in a team's lineup"""
    return [player for player in lineup if player.get('pos', '').upper() == 'G']

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

def format_goalie_stats(goalie_stats):
    """Format goalie stats for display"""
    formatted = []
    
    for key, stats in goalie_stats.items():
        if stats['gp'] > 0:  # Only include goalies who played
            formatted.append({
                'name': stats['name'],
                'team': stats['team'],
                'gp': stats['gp'],
                'w': stats['w'],
                'l': stats['l'],
                't': stats['t'],
                'so': stats['so'],
                'ga': stats['ga'],
                'gaa': stats['gaa'],
                'record': f"{stats['w']}-{stats['l']}-{stats['t']}"
            })
    
    # Sort by GAA (ascending) then by GP (descending)
    formatted.sort(key=lambda x: (x['gaa'], -x['gp']))
    
    return formatted

def main():
    """Load schedule.json and calculate goalie statistics"""
    try:
        with open('./output/schedule.json', 'r') as f:
            schedule_data = json.load(f)
        
        print("Calculating goalie statistics from schedule.json...")
        goalie_stats = calculate_goalie_stats(schedule_data)
        formatted_stats = format_goalie_stats(goalie_stats)
        
        print(f"\nFound {len(formatted_stats)} goalies with game appearances:\n")
        
        # Print header
        print(f"{'Name':<20} {'Team':<10} {'GP':<3} {'W':<3} {'L':<3} {'T':<3} {'SO':<3} {'GA':<3} {'GAA':<5} {'Record':<8}")
        print("-" * 80)
        
        # Print stats
        for stats in formatted_stats:
            print(f"{stats['name']:<20} {stats['team']:<10} {stats['gp']:<3} {stats['w']:<3} {stats['l']:<3} {stats['t']:<3} {stats['so']:<3} {stats['ga']:<3} {stats['gaa']:<5} {stats['record']:<8}")
        
        # Save to JSON file
        with open('./output/goalie_stats.json', 'w') as f:
            json.dump(formatted_stats, f, indent=2)
        
        print(f"\nGoalie statistics saved to ./output/goalie_stats.json")
        
        return formatted_stats
        
    except FileNotFoundError:
        print("Error: schedule.json not found in ./output/ directory")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON in schedule.json")
        return None

if __name__ == "__main__":
    main()
