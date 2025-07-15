#!/usr/bin/env python3
"""
Minimal test to verify the save function works correctly.
"""
import pandas as pd
from file_parser import save_txt_file

def test_minimal_save():
    """Test the save function with minimal data."""
    
    # Create a minimal DataFrame with comma values
    data = {
        'description': ['test recipe'],
        'enabled': ['1'],
        'input 1': ['t1me,mag'],
        'input 2': ['runs,qty=1'],
        'output': ['usetype,rar']
    }
    
    df = pd.DataFrame(data)
    
    print("DataFrame contents:")
    print(df)
    print("\nColumn values:")
    for col in df.columns:
        print(f"  {col}: '{df[col].iloc[0]}'")
    
    # Save to test file
    print("\nSaving to test_minimal.txt...")
    success = save_txt_file(df, "test_minimal.txt")
    
    if success:
        print("Save successful!")
        
        # Read and display the saved file
        print("\nContent of saved file:")
        with open("test_minimal.txt", 'r', encoding='windows-1252') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                print(f"Line {i+1}: {repr(line.rstrip())}")
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_minimal_save() 