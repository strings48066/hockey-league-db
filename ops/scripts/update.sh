#!/bin/bash
# Convenience wrapper for weekly update script
# Allows running from scripts directory: scripts/update.sh

# Change to parent directory to run weekly_update.sh
cd "$(dirname "$0")"
exec ./weekly_update.sh
