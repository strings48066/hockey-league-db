"""
Base formatter class with common functionality.
"""
import json
import pandas as pd
import os


class BaseFormatter:
    """Base class for all data formatters."""
    
    @staticmethod
    def handle_empty_data(df, data_type="data"):
        """Handle empty DataFrame scenarios."""
        if df.empty:
            return {
                "message": f"No {data_type} found",
                "status": "no_data",
                "data": []
            }
        return None
    
    @staticmethod
    def check_tbd_content(df):
        """Check if DataFrame contains TBD placeholder content."""
        if df.empty:
            return True
            
        # Count TBD vs actual data
        tbd_count = 0
        valid_count = 0
        
        for _, row in df.iterrows():
            row_str = ' '.join(str(val) for val in row.values)
            if 'TBD' in row_str.upper() or pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                tbd_count += 1
            else:
                valid_count += 1
        
        return tbd_count > valid_count
    
    @staticmethod
    def safe_column_assignment(df, expected_columns):
        """Safely assign column names with validation."""
        if len(df.columns) != len(expected_columns):
            raise ValueError(f"Expected {len(expected_columns)} columns, got {len(df.columns)}")
        
        df.columns = expected_columns
        return df


class OutputManager:
    """Handles saving data to various output formats."""
    
    @staticmethod
    def save_json(data, filepath):
        """Save data as JSON file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    @staticmethod
    def save_pretty_json(data, filepath):
        """Save data as pretty-formatted JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
