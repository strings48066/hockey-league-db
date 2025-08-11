"""
UHL Configuration Management
Centralized configuration loading with environment support.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"
OUTPUT_DIR = BASE_DIR / "output"

def load_environment():
    """Load environment variables from config/environment.env"""
    env_file = CONFIG_DIR / "environment.env"
    env_data = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_data[key] = value
                        os.environ[key] = value
    return env_data

# Load environment on import
load_environment()

## Google Sheets Configuration
DEFAULT_PLAYER_SPREADSHEET_ID = os.getenv(
    "PLAYER_SPREADSHEET_ID", 
    "16sG5OBgkP4no3dIt2-h8G8uSsK7S-o7-5gWDtHuPG6k"
)
DEFAULT_GAME_SPREADSHEET_ID = os.getenv(
    "GAME_SPREADSHEET_ID",
    "1XUoZxS4rbOJzv47grAqhEOpGcZui7okWJcfaLt7R67Q"
)

## Sheet Ranges
GAMES_RANGE = "games!A2:Z55"
PLAYERS_RANGE = "players!A2:C53"
PLAYERS_SEASON_RANGE = "players!D2:O53"
STANDINGS_RANGE = "standings!A2:L5"
GAMES_PLAYED_RANGE = "gamesPlayed!A1:Z1000"

# Game sheet ranges (for individual game processing)
GAME_RANGES = {
    "team1_lineup": "scoresheet!A3:H14",
    "team2_lineup": "scoresheet!K3:R14", 
    "game_info": "GameInfo!A2:J2",
    "goals": "scoresheet!A18:E34",
    "penalties": "scoresheet!F18:J34"
}

# Game events range
GAME_EVENTS_RANGE = "gameEvents!A1:P100"

## File Paths
SERVICE_ACCOUNT_FILE = str(CREDENTIALS_DIR / "service-account-key.json")
GOOGLE_CREDS_FILE = str(CREDENTIALS_DIR / "google-creds.json")
TOKEN_FILE = str(CREDENTIALS_DIR / "token.json")

## Team Mappings
TEAM_NAMES = {
    1: "New York",
    2: "Detroit", 
    3: "Chicago",
    4: "Boston"
}

## Directories
DIRECTORIES = {
    "output": OUTPUT_DIR,
    "config": CONFIG_DIR,
    "credentials": CREDENTIALS_DIR,
    "base": BASE_DIR
}
