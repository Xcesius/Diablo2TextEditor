#!/usr/bin/env python3
"""
Test to verify that our fix produces files with the correct size.
"""
import os
from file_parser import open_txt_file, save_txt_file

def test_file_size_fix():
    """Test that saving CubeMain.txt now produces the same size as CubeMainWorking.txt."""
    
    print("=== Testing file size fix ===")
    
    # Get original file sizes
    original_size = os.path.getsize("CubeMain.txt")
    working_size = os.path.getsize("CubeMainWorking.txt")
    
    print(f"Original CubeMain.txt size: {original_size} bytes")
    print(f"CubeMainWorking.txt size: {working_size} bytes")
    print(f"Difference: {working_size - original_size} bytes")
    
    # Load and save CubeMain.txt with our fixed function
    print("\nLoading CubeMain.txt...")
    df = open_txt_file("CubeMain.txt")
    
    if df is None:
        print("Failed to load CubeMain.txt!")
        return
    
    test_file = "CubeMain_size_test.txt"
    print(f"Saving with fixed function to {test_file}...")
    success = save_txt_file(df, test_file)
    
    if not success:
        print("Failed to save!")
        return
    
    # Check the new file size
    new_size = os.path.getsize(test_file)
    print(f"New saved file size: {new_size} bytes")
    
    # Compare with working file
    print(f"\nSize comparison:")
    print(f"  CubeMainWorking.txt: {working_size} bytes")
    print(f"  New saved file:      {new_size} bytes")
    print(f"  Difference:          {new_size - working_size} bytes")
    
    if new_size == working_size:
        print("✅ SUCCESS: File sizes now match!")
    else:
        print("❌ FAILURE: File sizes still don't match")
        
    # Clean up
    os.remove(test_file)
    print(f"Cleaned up {test_file}")

if __name__ == "__main__":
    test_file_size_fix() 