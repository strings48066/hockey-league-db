# UHL Auto-Commit System

A reusable Python-based automation system for git workflows in the UHL hockey league database.

## Features

- **Smart commit detection**: Automatically detects gameday updates, ops changes, or general features
- **Intelligent commit messages**: Generates contextual commit messages based on file changes
- **Automated versioning**: Handles semantic versioning (patch/minor/major) with git tags
- **GitHub integration**: Creates releases automatically if GitHub CLI is available
- **Multiple modes**: Interactive, quick gameday, quick ops, and dry-run modes
- **Colorized output**: Clear visual feedback throughout the process

## Usage

### Interactive Mode (Recommended)
```bash
cd ops/scripts
python3 auto_commit.py
```
This will guide you through the complete workflow with smart defaults.

### Quick Modes
```bash
# Quick gameday commit (after running ./run_uhl.sh all)
python3 auto_commit.py --quick-gameday

# Quick ops/automation commit
python3 auto_commit.py --quick-ops

# Dry run to see what would happen
python3 auto_commit.py --dry-run
```

### Convenience Wrapper
```bash
cd ops/scripts
python3 commit.py
```

## How It Works

### 1. Smart Analysis
The script analyzes your changes to determine the commit type:
- **Gameday**: If `schedule.json`, `players.json`, `standings.json`, and `goalie_stats.json` exist
- **Ops**: If changes are detected in the `ops/scripts` directory
- **Feat**: General feature updates

### 2. Commit Message Generation
Based on the analysis, it generates appropriate commit messages:
- Gameday: `"gameday: Update UHL data - 54 games, 52 players, 2 goalies"`
- Ops: `"ops: Improve UHL operations and automation"`
- General: `"feat: Update hockey league system"`

### 3. Versioning
- **Patch** (default): Bug fixes, data updates (1.0.1 → 1.0.2)
- **Minor**: New features, improvements (1.0.1 → 1.1.0)  
- **Major**: Breaking changes (1.0.1 → 2.0.0)
- **Skip**: Just commit and push without creating a release

### 4. Release Notes
Automatically generates detailed release notes based on the commit type:

**Gameday Release Notes:**
```
🏒 Gameday Update v1.2.3

## Data Updates
- Updated schedule with 54 games
- Processed 52 player records  
- Calculated statistics for 2 goalies

## Files Updated
- `schedule.json` - Complete game schedule with lineups
- `players.json` - Player data and season statistics
- `standings.json` - Team standings and records
- `goalie_stats.json` - Goalie performance metrics
```

## Class Structure

### `GitAutoCommit`
Main automation class with methods:
- `interactive_commit()`: Full interactive workflow
- `quick_gameday_commit()`: One-click gameday automation
- `quick_ops_commit()`: One-click ops automation
- `analyze_changes()`: Smart change detection
- `generate_commit_message()`: Context-aware messages
- `bump_version()`: Semantic versioning

### `Colors`
Terminal color constants for better UX

## Requirements

- Python 3.6+
- Git repository
- Optional: GitHub CLI (`gh`) for automated releases

## Integration with UHL Workflow

This replaces the bash-based `auto_commit.sh` and integrates with the existing UHL operations:

```bash
# Complete gameday workflow
cd ops
./run_uhl.sh all          # Process all UHL data
cd scripts
python3 auto_commit.py --quick-gameday  # Commit everything
```

## Customization

The script is designed to be reusable and can be easily extended:
- Add new commit types in `analyze_changes()`
- Customize commit message formats in `generate_commit_message()`
- Modify release note templates in `generate_release_notes()`
- Add new quick-commit modes as needed

## Error Handling

- Validates git repository before proceeding
- Provides clear error messages for failures
- Graceful handling of missing GitHub CLI
- Safe defaults throughout the workflow
