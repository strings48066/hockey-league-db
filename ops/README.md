# UHL Consolidated Operations

This directory contains the **standalone** consolidated operations system for the UHL database. Everything needed to run the operations is contained within this folder with proper service account authentication.

## 🎯 Quick Start

**Just run the operations:**
```bash
./run_uhl.sh all         # Process everything
./run_uhl.sh players     # Process players only  
./run_uhl.sh standings   # Process standings only
```

## 📁 Files Structure

```
ops/
├── uhl_ops.py              # Main operations manager
├── sheets_client.py        # Google Sheets client with service account auth
├── formatters.py           # Data formatting utilities  
├── config.py              # Configuration settings
├── run_uhl.sh             # Easy run script
├── .env                   # Spreadsheet ID (local secret)
├── service-account-key.json # Service account credentials (local secret)
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment
├── output/                # Generated JSON files
│   ├── players.json       # Players + season stats
│   └── standings.json     # Team standings
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
- ✅ Google Sheet shared with read-only access
- ✅ Service account key stored locally

## 📊 Output

All operations create JSON files in `./output/`:
- **`players.json`** - Player roster with season statistics
- **`standings.json`** - Team standings with W/L/T, goals, penalties

## 🔐 Security

- **Service Account Authentication** - No user interaction required
- **Read-only Permissions** - Service account can only read the sheet
- **Local Secrets** - Credentials stored locally, not in version control
- **Virtual Environment** - Isolated Python dependencies

## 🚀 Benefits vs Original Scripts

- ✅ **Standalone** - No external dependencies or relative paths
- ✅ **Service Account** - Production-ready authentication
- ✅ **DRY Principle** - No duplicate Google Sheets code
- ✅ **Virtual Environment** - Clean dependency management
- ✅ **Easy to Run** - Single script for all operations
- ✅ **Secure** - Proper secrets management

## 🔧 Manual Usage

If you prefer to run manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Run operations
python uhl_ops.py players
python uhl_ops.py standings
python uhl_ops.py all
```

This consolidated system completely replaces the need for the individual scripts in `players/ops/`, `standings/ops/` while providing better security and maintainability.
