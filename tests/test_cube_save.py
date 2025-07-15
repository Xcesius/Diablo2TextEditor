#!/usr/bin/env python3
"""
Test to save and reload the CubeMain.txt file to see if quotes are preserved.
"""
import os
from file_parser import open_txt_file, save_txt_file

def test_cube_save():
    """Test saving and reloading CubeMain.txt."""
    
    # Load the original file
    print("Loading CubeMain.txt...")
    df = open_txt_file("CubeMain.txt")
    
    if df is None:
        print("Failed to load file!")
        return
    
    # Save to a test file
    test_file = "CubeMain_test.txt"
    print(f"Saving to {test_file}...")
    
    success = save_txt_file(df, test_file)
    if not success:
        print("Save failed!")
        return
    
    # Read the first few lines and check for quotes
    print("\nFirst 5 lines of saved file:")
    with open(test_file, 'r', encoding='windows-1252') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:5]):
            print(f"Line {i+1}: {repr(line.rstrip())}")
    
    # Check specifically line 3 for comma values
    print("\nLine 3 split by tabs:")
    if len(lines) > 2:
        fields = lines[2].rstrip().split('\t')
        for i, field in enumerate(fields):
            if ',' in field:
                print(f"  Field {i+1}: {repr(field)}")
    
    # Clean up
    os.remove(test_file)
    print(f"\nCleaned up {test_file}")

if __name__ == "__main__":
    test_cube_save() 