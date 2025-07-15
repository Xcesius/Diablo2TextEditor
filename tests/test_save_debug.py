#!/usr/bin/env python3
"""
Debug script to understand what's happening in the save function.
"""
import pandas as pd
from file_parser import open_txt_file, save_txt_file

def debug_save():
    """Debug the save function to see what's happening."""
    
    # Load the file
    print("Loading CubeMain.txt...")
    df = open_txt_file("CubeMain.txt")
    
    if df is None:
        print("Failed to load file!")
        return
    
    # Check what's in the DataFrame for line 3 (which has the comma values)
    print(f"Row 2 (3rd line) contains:")
    for i, col in enumerate(df.columns):
        value = df.iat[2, i]
        print(f"  Column {i+1} ({col}): [{value}] (type: {type(value).__name__})")
    
    # Test the format_value function directly
    def format_value(value):
        """Format a single value with proper quoting rules."""
        # Handle empty/null values
        if pd.isna(value) or value == '':
            return ''
        
        str_value = str(value)
        # Quote if contains comma, but not if it's just a number or simple string
        if ',' in str_value:
            return f'"{str_value}"'
        return str_value
    
    print("\nTesting format_value function:")
    test_values = ["t1me,mag", "runs,qty=1", "gg4z,qty=1", "upma,qty=1", "usetype,rar"]
    for val in test_values:
        formatted = format_value(val)
        print(f"  '{val}' -> '{formatted}'")

if __name__ == "__main__":
    debug_save() 