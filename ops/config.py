# UHL Operations Configuration

## Google Sheets
DEFAULT_PLAYER_SPREADSHEET_ID = "16sG5OBgkP4no3dIt2-h8G8uSsK7S-o7-5gWDtHuPG6k"
DEFAULT_GAME_SPREADSHEET_ID = ""  # To be provided when processing games

## Sheet Ranges
GAMES_RANGE = "games!A2:L55"
PLAYERS_RANGE = "players!A2:C53"  # Fixed to skip header
PLAYERS_SEASON_RANGE = "players!D2:O53"  # Fixed to skip header
STANDINGS_RANGE = "standings!A2:L5"
GAMES_PLAYED_RANGE = "gamesPlayed!A1:Z1000"  # Games with lineups

# Game sheet ranges (for individual game processing)
GAME_RANGES = {
    "team1_lineup": "scoresheet!A3:H14",
    "team2_lineup": "scoresheet!K3:R14", 
    "game_info": "GameInfo!A2:J2",
    "goals": "scoresheet!A18:E34",
    "penalties": "scoresheet!F18:J34"
}

# Game events range (from main spreadsheet)
GAME_EVENTS_RANGE = "gameEvents!A1:P100"

## File Paths
SERVICE_ACCOUNT_FILE = "service-account-key.json"

## Output Directories
OUTPUT_DIR = "./output"

## Team Mappings
TEAM_NAMES = {
    1: "New York",
    2: "Detroit", 
    3: "Chicago",
    4: "Boston"
}
