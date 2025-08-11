#!/usr/bin/env python3

# UHL Commit Convenience Script
# Simple wrapper for the Python auto-commit tool

import sys
import os
from pathlib import Path

# Change to the ops/scripts directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Import and run the auto-commit module
from auto_commit import main

if __name__ == '__main__':
    main()
