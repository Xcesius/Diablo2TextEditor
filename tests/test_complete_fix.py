#!/usr/bin/env python3
"""
Comprehensive test to verify all quoting rules work correctly.
"""
import pandas as pd
from file_parser import save_txt_file

def test_complete_fix():
    """Test various quoting scenarios to ensure the fix works comprehensively."""
    
    # Create test data with various quoting scenarios
    data = {
        'description': [
            'MAPS',
            't1 map upgrade mag to rare',
            'Staff of Kings + Viper amulet -> Horadric Staff',
            'relic of the false prophet -> replica'
        ],
        'enabled': ['', '1', '1', '1'],
        'ladder': ['', '4', '', '2'],
        'version': ['', '100', '0', '100'],
        'op': ['', '18', '28', '16'],
        'param': ['', '361', '', '509'],
        'value': ['', '0', '', '111'],
        'numinputs': ['', '4', '2', '1'],
        'input 1': ['', 't1me,mag', 'msf', 'rofp'],
        'input 2': ['', 'runs,qty=1', 'vip', ''],
        'input 3': ['', 'gg4z,qty=1', '', ''],
        'output': ['', 'usetype,rar', 'hst', 'Replica Arm of King Leoric'],
        'lvl': ['', '', '', '120'],
        '*eol': ['0', '0', '0', '']
    }
    
    df = pd.DataFrame(data)
    
    print("Test DataFrame:")
    print(df.to_string())
    
    # Save to test file
    test_file = "test_complete_fix.txt"
    print(f"\nSaving to {test_file}...")
    success = save_txt_file(df, test_file)
    
    if success:
        print("Save successful!")
        
        # Read and display the saved file
        print("\nSaved file content:")
        with open(test_file, 'r', encoding='windows-1252') as f:
            content = f.read()
            print(content)
        
        # Test specific quoting rules
        lines = content.strip().split('\n')
        if len(lines) >= 5:
            print("\nTesting quoting rules:")
            
            # Line 2: t1 map upgrade
            line2 = lines[1].split('\t')
            print(f"Line 2 description: {repr(line2[0])} (should be unquoted)")
            print(f"Line 2 input 1: {repr(line2[8])} (should be quoted: 't1me,mag')")
            print(f"Line 2 input 2: {repr(line2[9])} (should be quoted: 'runs,qty=1')")
            print(f"Line 2 output: {repr(line2[11])} (should be quoted: 'usetype,rar')")
            
            # Line 3: Staff of Kings
            line3 = lines[2].split('\t')
            print(f"Line 3 description: {repr(line3[0])} (should be unquoted)")
            print(f"Line 3 input 1: {repr(line3[8])} (should be unquoted: 'msf')")
            print(f"Line 3 input 2: {repr(line3[9])} (should be unquoted: 'vip')")
            print(f"Line 3 output: {repr(line3[11])} (should be unquoted: 'hst')")
            
            # Line 4: relic of the false prophet
            line4 = lines[3].split('\t')
            print(f"Line 4 description: {repr(line4[0])} (should be unquoted)")
            print(f"Line 4 input 1: {repr(line4[8])} (should be quoted: 'rofp')")
            print(f"Line 4 output: {repr(line4[11])} (should be unquoted)")
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_complete_fix() 