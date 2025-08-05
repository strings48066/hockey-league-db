## UHL Hockey League Database Operations Guide

This workspace contains a consolidated UHL operations system in the `/ops` directory. All operations use the unified `uhl_ops.py` system with Google Sheets integration.

### Core Operations Workflow

**Primary Commands (run from `/ops` directory):**
```bash
# Main operations - process everything
./run_uhl.sh all                              # Process players + standings + games
python uhl_ops.py all                         # Alternative command line

# Individual operations
./run_uhl.sh players                          # Process players data → players.json
./run_uhl.sh standings                        # Process standings → standings.json  
./run_uhl.sh schedule                         # Generate complete schedule → schedule.json
./run_uhl.sh goalie-stats                     # Calculate goalie statistics → goalie_stats.json

# Games operations
./run_uhl.sh all-games                        # Process all games schedule
./run_uhl.sh single-game <player_id> <game_id>  # Process specific game
```

### Operations Details

**1. Players Operations (`/ops`)**
- **Command:** `python uhl_ops.py players` or `./run_uhl.sh players`
- **Output:** `output/players.json`
- **Process:** Fetches player data + season statistics, combines into unified format
- **Upstash:** Copy `players.json` content to Upstash database
- **Status:** ✅ Fully functional

**2. Standings Operations (`/ops`)**  
- **Command:** `python uhl_ops.py standings` or `./run_uhl.sh standings`
- **Output:** `output/standings.json`
- **Process:** Processes team standings with wins/losses/points
- **Upstash:** Copy `standings.json` content to Upstash database
- **Status:** ✅ Fully functional

**3. Schedule Operations (`/ops`)**
- **Command:** `python uhl_ops.py schedule` or `./run_uhl.sh schedule`  
- **Output:** `output/schedule.json`
- **Process:** Builds complete schedule with games, events, and full team lineups
- **Features:** Proper field alignment, full rosters (10+ players per team), game events
- **Upstash:** Copy `schedule.json` content to Upstash database
- **Status:** ✅ Fully functional

**4. Goalie Statistics (`/ops`) - WIP Feature**
- **Command:** `python uhl_ops.py goalie-stats` or `./run_uhl.sh goalie-stats`
- **Output:** `output/goalie_stats.json`
- **Process:** Calculates GP, W, L, T, SO, GA, GAA from schedule.json data
- **Features:** Comprehensive goalie analytics, team tracking, performance metrics
- **Status:** ⚠️ Functional but marked incomplete - needs further validation
- **Note:** Requires `schedule.json` to exist first

### Legacy Operations (Deprecated)

**Old individual directories** (use consolidated `/ops` instead):
- `games/ops/single_game.py` → Use `python uhl_ops.py single-game`
- `players/ops/players.py` → Use `python uhl_ops.py players`  
- `standings/ops/standings.py` → Use `python uhl_ops.py standings`

### System Architecture

**Configuration:**
- Google Sheets integration with service account authentication
- Spreadsheet IDs configured in `/ops/.env`
- Multi-spreadsheet support for player and game data
- Sheet ranges defined in `/ops/config.py`

**Output Management:**
- All outputs saved to `/ops/output/` directory
- JSON format for easy Upstash integration
- Standardized data formatting across operations

**Authentication:**
- Service account: `uhl-sheets-reader@crucial-matter-330121.iam.gserviceaccount.com`
- Key file: `/ops/service-account-key.json`
- Read-only access to Google Sheets

### Development Workflow

**Setup Environment:**
```bash
cd /ops
source venv/bin/activate  # Activate Python environment
```

**Common Issues:**
- Field misalignment: Fixed in consolidated system with proper column mapping
- Missing lineups: Enhanced extraction from gamesPlayed sheet (1000+ rows)
- Goalie stats: New comprehensive calculation system available

**Git Operations:**
- Stage files: `git add .`
- Unstage files: `git reset HEAD` (preserves working directory)
- Commit: `git commit -m "message"`
- Push: `git push`

### Quick Reference

**When asked to "run operations":**
1. Navigate to `/ops` directory
2. Run `./run_uhl.sh all` for complete processing
3. Check `output/` directory for generated JSON files
4. Copy JSON content to Upstash database as needed

**For specific operations:**
- Players only: `./run_uhl.sh players`
- Standings only: `./run_uhl.sh standings`  
- Schedule only: `./run_uhl.sh schedule`
- Goalie stats: `./run_uhl.sh goalie-stats` (after schedule generation)