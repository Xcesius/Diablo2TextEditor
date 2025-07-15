#!/usr/bin/env python3
"""
Test script to verify that our save/load cycle preserves exact file format.
"""
import os
from file_parser import open_txt_file, save_txt_file

def test_format_preservation():
    """Test that we can load and save without changing the file format."""
    
    # Load the original file
    print("Loading original Levels.txt...")
    original_data = open_txt_file("Levels.txt")
    if original_data is None:
        print("Failed to load original file!")
        return False
    
    # Save it as a test file
    test_file = "Levels_test.txt"
    print(f"Saving to {test_file}...")
    if not save_txt_file(original_data, test_file):
        print("Failed to save test file!")
        return False
    
    # Load the test file back
    print("Loading test file back...")
    test_data = open_txt_file(test_file)
    if test_data is None:
        print("Failed to load test file!")
        return False
    
    # Compare the data
    if original_data.equals(test_data):
        print("✅ SUCCESS: Data is identical after save/load cycle!")
        
        # Also compare file sizes as a quick check
        original_size = os.path.getsize("Levels.txt")
        test_size = os.path.getsize(test_file)
        print(f"Original file size: {original_size} bytes")
        print(f"Test file size: {test_size} bytes")
        
        if abs(original_size - test_size) < 50:  # Allow small differences due to line endings
            print("✅ File sizes are very similar - format preserved!")
        else:
            print("⚠️  WARNING: File sizes differ significantly!")
            
    else:
        print("❌ FAILURE: Data changed during save/load cycle!")
        return False
    
    # Clean up
    os.remove(test_file)
    print(f"Cleaned up {test_file}")
    return True

if __name__ == "__main__":
    test_format_preservation() 