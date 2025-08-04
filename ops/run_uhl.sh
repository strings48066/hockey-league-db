#!/bin/bash

# UHL Operations Runner
# Activates virtual environment and runs the UHL operations

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the UHL operations
python uhl_ops.py "$@"
