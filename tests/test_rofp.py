#!/usr/bin/env python3
"""
Test specifically for the 'rofp' case to verify quoting.
"""
import pandas as pd
from file_parser import save_txt_file

def test_rofp():
    """Test the save function with rofp and other values."""
    
    # Create test data similar to the relic lines
    data = {
        'description': ['add relic factor'],
        'enabled': ['1'],
        'ladder': ['2'],
        'version': ['100'],
        'op': ['18'],
        'param': ['509'],
        'value': ['0'],
        'numinputs': ['1'],
        'input 1': ['rofp'],
        'output': ['useitem'],
        'mod 1': ['awakennum'],
        'mod 1 chance': ['100'],
        'mod 1 min': ['1'],
        'mod 1 max': ['112']
    }
    
    df = pd.DataFrame(data)
    
    print("DataFrame contents:")
    print(df.to_string())
    print("\nSpecific values to test:")
    print(f"  rofp: '{df['input 1'].iloc[0]}'")
    print(f"  useitem: '{df['output'].iloc[0]}'")
    print(f"  awakennum: '{df['mod 1'].iloc[0]}'")
    
    # Save to test file
    print("\nSaving to test_rofp.txt...")
    success = save_txt_file(df, "test_rofp.txt")
    
    if success:
        print("Save successful!")
        
        # Read and display the saved file
        with open("test_rofp.txt", 'r', encoding='windows-1252') as f:
            content = f.read()
            print("\nSaved file content:")
            print(content)
    else:
        print("Save failed!")

if __name__ == "__main__":
    test_rofp() 