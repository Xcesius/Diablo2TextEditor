#!/usr/bin/env python3
"""
Test script to verify that the fixed save function works correctly.
"""
import pandas as pd
from file_parser import save_txt_file

def test_save_fix():
    """Test that the save function now produces correct format without unnecessary quotes."""
    
    # Create test data that matches the CubeMain structure
    data = {
        'description': ['MAPS', 't1 map upgrade mag to rare', 'Staff of Kings + Viper amulet -> Horadric Staff'],
        'enabled': [None, '1', '1'],
        'ladder': [None, '4', None],
        'version': [None, '100', '0'],
        'op': [None, '18', '28'],
        'param': [None, '361', None],
        'value': [None, '0', None],
        'numinputs': [None, '4', '2'],
        'input 1': [None, 't1me,mag', 'msf'],
        'input 2': [None, 'runs,qty=1', 'vip'],
        'input 3': [None, 'gg4z,qty=1', None],
        'output': [None, 'usetype,rar', 'hst'],
        'lvl': [None, None, None],
        'plvl': [None, '100', None],
        '*eol': ['0', '0', '0']
    }
    
    df = pd.DataFrame(data)
    
    print("Test DataFrame:")
    print(df.to_string())
    
    # Save to test file
    test_file = "test_fix.txt"
    print(f"\nSaving to {test_file}...")
    success = save_txt_file(df, test_file)
    
    if success:
        print("Save successful!")
        
        # Read and display the saved file
        print("\nSaved file content:")
        with open(test_file, 'r', encoding='windows-1252') as f:
            content = f.read()
            print(content)
        
        # Check specific values
        print("\nChecking specific values:")
        lines = content.strip().split('\n')
        if len(lines) >= 3:
            line2_fields = lines[1].split('\t')  # Second data line
            line3_fields = lines[2].split('\t')  # Third data line
            
            print(f"Line 2 'input 1': {repr(line2_fields[8])}")  # Should be: t1me,mag (no quotes)
            print(f"Line 2 'input 2': {repr(line2_fields[9])}")  # Should be: runs,qty=1 (no quotes)
            print(f"Line 2 'output': {repr(line2_fields[11])}")  # Should be: usetype,rar (no quotes)
            
            print(f"Line 3 'input 1': {repr(line3_fields[8])}")  # Should be: msf (no quotes)
            print(f"Line 3 'input 2': {repr(line3_fields[9])}")  # Should be: vip (no quotes)
            print(f"Line 3 'output': {repr(line3_fields[11])}")  # Should be: hst (no quotes)
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_save_fix() 