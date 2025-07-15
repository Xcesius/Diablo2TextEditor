#!/usr/bin/env python3
"""
Test script for the enhanced file type detection with column-based fingerprinting.
"""

import os
import shutil
from file_parser import detect_file_type

def test_enhanced_detection():
    """Test the enhanced detection system with various scenarios."""
    
    print("=== Enhanced File Type Detection Test ===\n")
    
    # Test 1: Create a test file with renamed filename to test column detection
    print("TEST 1: Column-based detection with renamed file")
    print("-" * 50)
    
    # Copy CubeMainWorking.txt to a different name
    original_file = "CubeMainWorking.txt"
    test_file = "unknown_test_file.txt"
    
    if os.path.exists(original_file):
        # Copy the file with a different name
        shutil.copy2(original_file, test_file)
        
        print(f"Testing file: {test_file} (copied from {original_file})")
        
        # Test detection
        file_type, confidence, binding_key = detect_file_type(test_file)
        
        print(f"Detection result:")
        print(f"  File type: {file_type}")
        print(f"  Confidence: {confidence}")
        print(f"  Binding key: {binding_key}")
        print(f"  Expected: cubemain (should detect CubeMain structure)")
        
        # Clean up
        os.remove(test_file)
        print(f"  ✅ Test file cleaned up")
    else:
        print(f"  ❌ Original file {original_file} not found")
    
    print("\n" + "=" * 70)
    
    # Test 2: Normal filename detection (should still work)
    print("TEST 2: Normal filename detection")
    print("-" * 50)
    
    test_files = [
        "CubeMainWorking.txt",
        "excel/Armor.txt", 
        "excel/Weapons.txt",
        "excel/Skills.txt"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nTesting: {test_file}")
            file_type, confidence, binding_key = detect_file_type(test_file)
            print(f"  Type: {file_type}, Confidence: {confidence}, Binding: {binding_key}")
        else:
            print(f"  ❌ File not found: {test_file}")
    
    print("\n" + "=" * 70)
    
    # Test 3: Create a custom test file with known columns
    print("TEST 3: Custom test file with known column patterns")
    print("-" * 50)
    
    # Test with a simple Skills.txt pattern
    skills_test_content = "skill\tcharclass\tskilldesc\tsrvstfunc\tprogressive\tfinishing\n" + \
                         "testskill\tama\tTest Skill\t0\t0\t0\n"
    
    custom_test_file = "custom_skills_test.txt"
    
    try:
        with open(custom_test_file, 'w', encoding='windows-1252') as f:
            f.write(skills_test_content)
        
        print(f"Created custom test file: {custom_test_file}")
        print("Content preview:")
        print("  skill\tcharclass\tskilldesc\tsrvstfunc\tprogressive\tfinishing")
        
        file_type, confidence, binding_key = detect_file_type(custom_test_file)
        print(f"\nDetection result:")
        print(f"  File type: {file_type}")
        print(f"  Confidence: {confidence}")
        print(f"  Binding key: {binding_key}")
        print(f"  Expected: skills (should detect Skills.txt structure)")
        
        # Clean up
        os.remove(custom_test_file)
        print(f"  ✅ Custom test file cleaned up")
        
    except Exception as e:
        print(f"  ❌ Error creating custom test file: {e}")
    
    print("\n" + "=" * 70)
    
    # Test 4: Test gems.txt pattern detection
    print("TEST 4: Custom gems.txt pattern test")
    print("-" * 50)
    
    gems_test_content = "name\tletter\ttransform\tcode\tweaponMod1Code\thelmMod1Code\tshieldMod1Code\n" + \
                       "testgem\tr01\t0\tgem1\tres-fire\tres-fire\tres-fire\n"
    
    custom_gems_file = "custom_gems_test.txt"
    
    try:
        with open(custom_gems_file, 'w', encoding='windows-1252') as f:
            f.write(gems_test_content)
        
        print(f"Created custom gems test file: {custom_gems_file}")
        print("Content preview:")
        print("  name\tletter\ttransform\tcode\tweaponMod1Code\thelmMod1Code\tshieldMod1Code")
        
        file_type, confidence, binding_key = detect_file_type(custom_gems_file)
        print(f"\nDetection result:")
        print(f"  File type: {file_type}")
        print(f"  Confidence: {confidence}")
        print(f"  Binding key: {binding_key}")
        print(f"  Expected: gems (should detect Gems.txt structure)")
        
        # Clean up
        os.remove(custom_gems_file)
        print(f"  ✅ Custom gems test file cleaned up")
        
    except Exception as e:
        print(f"  ❌ Error creating custom gems test file: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 Enhanced detection testing complete!")
    print("\nThe enhanced detection should now:")
    print("1. ✅ Try filename detection first (highest priority)")
    print("2. ✅ Fall back to column fingerprint analysis")
    print("3. ✅ Use unique columns for high confidence detection")
    print("4. ✅ Use distinctive combinations for medium confidence")
    print("5. ✅ Fall back to general pattern detection")

if __name__ == "__main__":
    test_enhanced_detection() 