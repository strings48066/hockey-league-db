# UHL Consolidated Operations

This directory contains the **standalone** consolidated operations system for the UHL database. Everything needed to run operations is contained within this folder with proper service account authentication, now including support for games processing.

## 🎯 Quick Start

**Run operations with different data types:**
```bash
./run_uhl.sh all                              # Process everything (players + standings + games)
./run_uhl.sh players                          # Process players only  
./run_uhl.sh standings                        # Process standings only
./run_uhl.sh all-games                        # Process games schedule
./run_uhl.sh single-game <player_id> <game_id>  # Process detailed game data
```

## 📁 Files Structure

```
ops/
├── uhl_ops.py              # Main operations manager (supports games!)
├── sheets_client.py        # Google Sheets client with multi-spreadsheet support
├── formatters.py           # Data formatting utilities (includes GameFormatter)
├── config.py              # Configuration settings for all data types
├── run_uhl.sh             # Easy run script
├── .env                   # Spreadsheet IDs (local secret)
├── service-account-key.json # Service account credentials (local secret)
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment
├── output/                # Generated JSON files
│   ├── players.json       # Players + season stats
│   ├── standings.json     # Team standings
│   ├── all_games.json     # Games schedule
│   └── game_output.json   # Detailed game data
└── README.md             # This file
```

## 🔧 Setup (One-time)

**1. Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Authentication (already configured):**
- ✅ Service account created: `uhl-sheets-reader@crucial-matter-330121.iam.gserviceaccount.com`
- ✅ Google Sheets shared with read-only access
- ✅ Service account key stored locally

**3. Configure Spreadsheet IDs:**
Edit `.env` file with your spreadsheet IDs:
```properties
PLAYER_SPREADSHEET_ID=your_main_spreadsheet_id
GAME_SPREADSHEET_ID=your_game_specific_spreadsheet_id
```

## 📊 Data Types & Output

### Players Data
- **Input**: Main spreadsheet, ranges `players!A2:C53` + `players!D2:O53`
- **Output**: `./output/players.json` - Player roster with season statistics

### Standings Data  
- **Input**: Main spreadsheet, range `standings!A2:L5`
- **Output**: `./output/standings.json` - Team standings with W/L/T, goals, penalties

### Games Data

#### All Games (Schedule)
- **Input**: Main spreadsheet, range `games!A2:L55`  
- **Output**: `./output/all_games.json` - Complete games schedule

#### Single Game (Detailed)
- **Input**: Game-specific spreadsheet with multiple ranges:
  - `GameInfo!A2:J2` - Game metadata
  - `scoresheet!A3:H14` - Home team lineup
  - `scoresheet!K3:R14` - Away team lineup  
  - `scoresheet!A18:E34` - Goals scored
  - `scoresheet!F18:J34` - Penalties taken
- **Output**: `./output/game_output.json` - Complete game with lineups, goals, penalties

## 🚀 Usage Examples

```bash
# Process just players from main spreadsheet
./run_uhl.sh players

# Process all games schedule from main spreadsheet  
./run_uhl.sh all-games

# Process detailed single game (requires both spreadsheet IDs)
./run_uhl.sh single-game 16sG5OBgkP4no3dIt2-h8G8uSsK7S-o7-5gWDtHuPG6k 1ABC123xyz

# Process everything available
./run_uhl.sh all
```

## 🔐 Security

- **Service Account Authentication** - No user interaction required
- **Read-only Permissions** - Service account can only read sheets
- **Multiple Spreadsheets** - Support for main data + individual game sheets
- **Local Secrets** - Credentials stored locally, not in version control
- **Virtual Environment** - Isolated Python dependencies

## 🚀 Benefits vs Original Scripts

- ✅ **Consolidated Games** - Now includes `games/ops/` functionality  
- ✅ **Multi-Spreadsheet** - Handle both main data and game-specific sheets
- ✅ **Standalone** - No external dependencies or relative paths
- ✅ **Service Account** - Production-ready authentication
- ✅ **DRY Principle** - No duplicate Google Sheets code across ops folders
- ✅ **Virtual Environment** - Clean dependency management
- ✅ **Easy to Run** - Single script for all operations
- ✅ **Secure** - Proper secrets management

## 🔧 Manual Usage

If you prefer to run manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Run different operations
python uhl_ops.py players
python uhl_ops.py standings  
python uhl_ops.py all-games
python uhl_ops.py single-game <player_sheet_id> <game_sheet_id>
python uhl_ops.py all
```

## 🔄 Migration Complete

This consolidated system now **completely replaces**:
- ✅ `players/ops/` - Player data processing
- ✅ `standings/ops/` - Standings data processing  
- ✅ `games/ops/` - Game data processing (both schedule and detailed games)

All with better security, maintainability, and no code duplication!
