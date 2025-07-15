#!/usr/bin/env python3
"""
Comprehensive test to compare CubeMain.txt and CubeMainWorking.txt files.
This will help verify that our fixed saving logic produces the correct format.
"""
import pandas as pd
from file_parser import open_txt_file, save_txt_file
import os

def compare_files_line_by_line(file1, file2):
    """Compare two files line by line and show differences."""
    print(f"\n=== Line-by-line comparison: {file1} vs {file2} ===")
    
    try:
        with open(file1, 'r', encoding='windows-1252') as f1, \
             open(file2, 'r', encoding='windows-1252') as f2:
            
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            
            max_lines = max(len(lines1), len(lines2))
            differences = 0
            
            for i in range(max_lines):
                line1 = lines1[i].rstrip() if i < len(lines1) else "<MISSING>"
                line2 = lines2[i].rstrip() if i < len(lines2) else "<MISSING>"
                
                if line1 != line2:
                    differences += 1
                    print(f"\nLine {i+1} differs:")
                    print(f"  {file1}: {repr(line1)}")
                    print(f"  {file2}: {repr(line2)}")
                    
                    # Show field-by-field differences for data lines
                    if i > 0 and line1 != "<MISSING>" and line2 != "<MISSING>":
                        fields1 = line1.split('\t')
                        fields2 = line2.split('\t')
                        max_fields = max(len(fields1), len(fields2))
                        
                        for j in range(max_fields):
                            field1 = fields1[j] if j < len(fields1) else "<MISSING>"
                            field2 = fields2[j] if j < len(fields2) else "<MISSING>"
                            
                            if field1 != field2:
                                print(f"    Field {j+1}: {repr(field1)} vs {repr(field2)}")
                    
                    # Stop after showing first 10 differences to avoid spam
                    if differences >= 10:
                        print(f"\n... (showing only first 10 differences)")
                        break
            
            print(f"\nTotal differences found: {differences}")
            return differences == 0
            
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

def compare_dataframes(df1, df2, name1, name2):
    """Compare two dataframes and show differences."""
    print(f"\n=== DataFrame comparison: {name1} vs {name2} ===")
    
    if df1.shape != df2.shape:
        print(f"Shape difference: {name1}={df1.shape}, {name2}={df2.shape}")
        return False
    
    if not df1.columns.equals(df2.columns):
        print(f"Column difference:")
        print(f"  {name1} columns: {list(df1.columns)}")
        print(f"  {name2} columns: {list(df2.columns)}")
        return False
    
    # Compare values
    differences = 0
    for i in range(len(df1)):
        for j, col in enumerate(df1.columns):
            val1 = df1.iloc[i, j]
            val2 = df2.iloc[i, j]
            
            # Handle NaN comparisons
            if pd.isna(val1) and pd.isna(val2):
                continue
            if pd.isna(val1) or pd.isna(val2):
                differences += 1
                print(f"Row {i+1}, Col {j+1} ({col}): {repr(val1)} vs {repr(val2)}")
                continue
            
            # Convert to strings for comparison
            str_val1 = str(val1)
            str_val2 = str(val2)
            
            if str_val1 != str_val2:
                differences += 1
                print(f"Row {i+1}, Col {j+1} ({col}): {repr(str_val1)} vs {repr(str_val2)}")
                
                # Stop after 20 differences to avoid spam
                if differences >= 20:
                    print(f"\n... (showing only first 20 differences)")
                    return False
    
    print(f"DataFrame comparison complete. Differences: {differences}")
    return differences == 0

def test_save_and_compare():
    """Test saving CubeMain.txt with our fixed function and compare with working file."""
    print("=== Testing save function and comparing with working file ===")
    
    # Load the original CubeMain.txt
    print("Loading CubeMain.txt...")
    df_original = open_txt_file("CubeMain.txt")
    if df_original is None:
        print("Failed to load CubeMain.txt!")
        return False
    
    # Save it with our fixed function
    test_output = "CubeMain_test_output.txt"
    print(f"Saving with fixed function to {test_output}...")
    success = save_txt_file(df_original, test_output)
    if not success:
        print("Failed to save with fixed function!")
        return False
    
    # Compare the test output with the working file
    print(f"Comparing {test_output} with CubeMainWorking.txt...")
    files_match = compare_files_line_by_line(test_output, "CubeMainWorking.txt")
    
    # Clean up
    if os.path.exists(test_output):
        os.remove(test_output)
        print(f"Cleaned up {test_output}")
    
    return files_match

def test_compare_cubemain():
    """Main test function to compare CubeMain files."""
    
    print("DIABLO 2 CUBEMAIN FILE COMPARISON TEST")
    print("="*50)
    
    # Check if files exist
    files_to_check = ["CubeMain.txt", "CubeMainWorking.txt"]
    for file in files_to_check:
        if not os.path.exists(file):
            print(f"ERROR: {file} not found!")
            return False
    
    # Load both files as DataFrames
    print("Loading files...")
    df_current = open_txt_file("CubeMain.txt")
    df_working = open_txt_file("CubeMainWorking.txt")
    
    if df_current is None or df_working is None:
        print("Failed to load one or both files!")
        return False
    
    print(f"CubeMain.txt: {df_current.shape[0]} rows, {df_current.shape[1]} columns")
    print(f"CubeMainWorking.txt: {df_working.shape[0]} rows, {df_working.shape[1]} columns")
    
    # Compare DataFrames
    dataframes_match = compare_dataframes(df_current, df_working, "CubeMain.txt", "CubeMainWorking.txt")
    
    # Compare raw files line by line
    files_match = compare_files_line_by_line("CubeMain.txt", "CubeMainWorking.txt")
    
    # Test our save function
    save_test_passed = test_save_and_compare()
    
    # Summary
    print("\n" + "="*50)
    print("COMPARISON SUMMARY:")
    print("="*50)
    print(f"DataFrames match: {dataframes_match}")
    print(f"Raw files match: {files_match}")
    print(f"Save function test passed: {save_test_passed}")
    
    if dataframes_match and files_match and save_test_passed:
        print("\n✅ SUCCESS: All tests passed! Files are identical and save function works correctly.")
    else:
        print("\n❌ DIFFERENCES FOUND: Files don't match or save function needs adjustment.")
        
        if not files_match:
            print("   - Raw file format differences detected")
        if not dataframes_match:
            print("   - Data content differences detected")
        if not save_test_passed:
            print("   - Save function output doesn't match working file")
    
    return dataframes_match and files_match and save_test_passed

if __name__ == "__main__":
    test_compare_cubemain() 