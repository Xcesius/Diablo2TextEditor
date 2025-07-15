#!/usr/bin/env python3
"""
Test script to verify that the fixed save function works correctly with CubeMain.txt.
"""
from file_parser import open_txt_file, save_txt_file

def test_cubemain_fix():
    """Test that the save function now produces correct format for CubeMain.txt."""
    
    # Load the current CubeMain.txt file
    print("Loading CubeMain.txt...")
    df = open_txt_file("CubeMain.txt")
    
    if df is None:
        print("Failed to load CubeMain.txt!")
        return
    
    # Save to a test file
    test_file = "CubeMain_fixed.txt"
    print(f"Saving to {test_file}...")
    success = save_txt_file(df, test_file)
    
    if success:
        print("Save successful!")
        
        # Read and compare the first few lines
        print("\nFirst 5 lines of the fixed file:")
        with open(test_file, 'r', encoding='windows-1252') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:5]):
                print(f"Line {i+1}: {repr(line.rstrip())}")
        
        # Check specific problematic lines
        print("\nChecking specific values that were previously quoted incorrectly:")
        if len(lines) > 32:
            # Line 33: Staff of Kings + Viper amulet -> Horadric Staff
            line33_fields = lines[32].rstrip().split('\t')
            print(f"Line 33 'input 1': {repr(line33_fields[10])}")  # Should be: msf (no quotes)
            print(f"Line 33 'input 2': {repr(line33_fields[11])}")  # Should be: vip (no quotes)
            print(f"Line 33 'output': {repr(line33_fields[17])}")   # Should be: hst (no quotes)
        
        if len(lines) > 33:
            # Line 34: Wirt's leg + town portal book -> cow portal
            line34_fields = lines[33].rstrip().split('\t')
            print(f"Line 34 'input 1': {repr(line34_fields[10])}")  # Should be: leg (no quotes)
            print(f"Line 34 'input 2': {repr(line34_fields[11])}")  # Should be: tbk (no quotes)
        
        # Show that descriptions with spaces are still quoted
        print("\nDescriptions with spaces should still be quoted:")
        for i, line in enumerate(lines[1:6]):  # Skip header
            fields = line.rstrip().split('\t')
            if fields[0]:  # If description exists
                print(f"Line {i+2} description: {repr(fields[0])}")
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_cubemain_fix() 