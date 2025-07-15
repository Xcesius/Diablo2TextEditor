#!/usr/bin/env python3
"""
Test script to verify the fixed save function works correctly with the rofp example.
"""
import pandas as pd
from file_parser import save_txt_file

def test_rofp_fix():
    """Test the exact example provided by the user."""
    
    # Create test data matching the user's example
    data = {
        'description': ['relic of the false prophet -> replica'],
        'enabled': ['1'],
        'ladder': ['2'],
        'min diff': [''],
        'version': ['100'],
        'op': ['16'],
        'param': ['509'],
        'value': ['111'],
        'class': [''],
        'numinputs': ['1'],
        'input 1': ['rofp'],
        'input 2': [''],
        'input 3': [''],
        'input 4': [''],
        'input 5': [''],
        'input 6': [''],
        'input 7': [''],
        'output': ['Replica Arm of King Leoric'],
        'lvl': ['120'],
        'plvl': [''],
        'ilvl': [''],
        '*eol': ['']
    }
    
    df = pd.DataFrame(data)
    
    print("Test DataFrame:")
    print(df.to_string())
    
    # Save to test file
    test_file = "test_rofp_fix.txt"
    print(f"\nSaving to {test_file}...")
    success = save_txt_file(df, test_file)
    
    if success:
        print("Save successful!")
        
        # Read and display the saved file
        print("\nSaved file content:")
        with open(test_file, 'r', encoding='windows-1252') as f:
            content = f.read()
            print(content)
        
        # Check the specific values
        lines = content.strip().split('\n')
        if len(lines) >= 2:
            data_line = lines[1]  # Skip header
            fields = data_line.split('\t')
            
            print("\nChecking specific values:")
            print(f"Description: {repr(fields[0])}")  # Should be: relic of the false prophet -> replica (no quotes)
            print(f"Input 1: {repr(fields[10])}")     # Should be: "rofp" (with quotes)
            print(f"Output: {repr(fields[17])}")      # Should be: Replica Arm of King Leoric (no quotes)
            
            # Verify the expected format
            expected_description = "relic of the false prophet -> replica"
            expected_input1 = '"rofp"'
            expected_output = "Replica Arm of King Leoric"
            
            print(f"\nExpected vs Actual:")
            print(f"Description - Expected: {repr(expected_description)}, Actual: {repr(fields[0])}, Match: {fields[0] == expected_description}")
            print(f"Input 1 - Expected: {repr(expected_input1)}, Actual: {repr(fields[10])}, Match: {fields[10] == expected_input1}")
            print(f"Output - Expected: {repr(expected_output)}, Actual: {repr(fields[17])}, Match: {fields[17] == expected_output}")
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_rofp_fix() 