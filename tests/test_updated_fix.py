#!/usr/bin/env python3
"""
Test the updated quoting rules to see if they match the working file format.
"""
import pandas as pd
from file_parser import save_txt_file

def test_updated_quoting():
    """Test the updated quoting rules with problematic values."""
    
    # Test values that were different in the comparison
    data = {
        'description': [
            '3 t1-> new t2',
            '3 t2-> new t3', 
            'r33 + weapon -> repair + recharge',
            'relic of the false prophet -> replica'
        ],
        'enabled': ['1', '1', '1', '1'],
        'ladder': ['4', '4', '', '2'],
        'numinputs': ['3', '4', '3', '1'],
        'input 1': ['t1me,qty=2', 't2me,qty=1', 'weap', 'rofp'],
        'input 2': ['t1me', 't2me', 'r33g,qty=1', ''],
        'input 3': ['upmp,qty=1', 't2me', 'gg4z,qty=1', ''],
        'output': ['t2me,nor', 't3me,nor', 'useitem,rep,rch,qty=255', 'Replica Arm of King Leoric'],
        '*eol': ['0', '0', '0', '']
    }
    
    df = pd.DataFrame(data)
    
    print("Test DataFrame:")
    print(df.to_string())
    
    # Save to test file
    test_file = "test_updated_fix.txt"
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
        lines = content.strip().split('\n')
        if len(lines) >= 5:
            print("\nChecking quoting rules:")
            
            # Line 2: t1me standalone
            line2 = lines[1].split('\t')
            print(f"Line 2 input 2: {repr(line2[5])} (should be quoted: 't1me')")
            
            # Line 3: t2me standalone
            line3 = lines[2].split('\t')  
            print(f"Line 3 input 2: {repr(line3[5])} (should be quoted: 't2me')")
            print(f"Line 3 input 3: {repr(line3[6])} (should be quoted: 't2me')")
            
            # Line 4: weap
            line4 = lines[3].split('\t')
            print(f"Line 4 input 1: {repr(line4[4])} (should be quoted: 'weap')")
            
            # Line 5: rofp
            line5 = lines[4].split('\t')
            print(f"Line 5 input 1: {repr(line5[4])} (should be quoted: 'rofp')")
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_updated_quoting() 