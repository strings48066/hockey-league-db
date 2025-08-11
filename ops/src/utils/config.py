# UHL Operations Configuration

## Google Sheets
DEFAULT_PLAYER_SPREADSHEET_ID = "16sG5OBgkP4no3dIt2-h8G8uSsK7S-o7-5gWDtHuPG6k"
DEFAULT_GAME_SPREADSHEET_ID = "1XUoZxS4rbOJzv47grAqhEOpGcZui7okWJcfaLt7R67Q"  # New game sheet for single game processing

## Sheet Ranges
GAMES_RANGE = "games!A2:Z55"  # Expanded to get all possible columns
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

## File Paths (use the parent config)
from config.settings import SERVICE_ACCOUNT_FILE, GOOGLE_CREDS_FILE, TOKEN_FILE

## Output Directories
OUTPUT_DIR = "./output"

## Team Mappings
TEAM_NAMES = {
    1: "New York",
    2: "Detroit", 
    3: "Chicago",
    4: "Boston"
}
