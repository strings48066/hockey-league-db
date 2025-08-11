#!/bin/bash

# UHL Weekly Update Script
# This script performs the complete weekly game update process
# Run this after completing the Google Sheets manual steps

echo "🏒 Starting UHL Weekly Update Process..."
echo "======================================"

# Change to the ops directory (parent of scripts)
cd "$(dirname "$0")/.."

# Step 1: Clear output folder
echo "🗑️  Clearing output folder..."
rm -rf output/*
echo "✅ Output folder cleared"

# Step 2: Run schedule operation
echo ""
echo "📅 Step 1/4: Processing schedule..."
./run_uhl.sh schedule
if [ $? -ne 0 ]; then
    echo "❌ Schedule operation failed"
    exit 1
fi

# Step 3: Run players operation
echo ""
echo "👥 Step 2/4: Processing players..."
./run_uhl.sh players
if [ $? -ne 0 ]; then
    echo "❌ Players operation failed"
    exit 1
fi

# Step 4: Run standings operation
echo ""
echo "🏆 Step 3/4: Processing standings..."
./run_uhl.sh standings
if [ $? -ne 0 ]; then
    echo "❌ Standings operation failed"
    exit 1
fi

# Step 5: Run goalie stats operation
echo ""
echo "🥅 Step 4/4: Processing goalie stats..."
./run_uhl.sh goalie-stats
if [ $? -ne 0 ]; then
    echo "❌ Goalie stats operation failed"
    exit 1
fi

echo ""
echo "🎉 Weekly Update Process Complete!"
echo "=================================="
echo "All operations completed successfully."
echo "Check the output/ folder for updated JSON files:"
echo "  - schedule.json"
echo "  - players.json" 
echo "  - standings.json"
echo "  - goalie_stats.json"
