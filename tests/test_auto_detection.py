#!/usr/bin/env python3
"""
Test script to demonstrate the auto-detection functionality.
"""

import os
from file_parser import detect_file_type, auto_detect_encoding, check_for_working_version

def test_auto_detection():
    """Test auto-detection on various files in the project."""
    
    print("=== Diablo 2 Text Editor Auto-Detection Test ===\n")
    
    # Test files to check
    test_files = [
        'CubeMain.txt',
        'CubeMainWorking.txt',
        'Levels.txt',
        'excel/CubeMain.txt',
        'excel/Armor.txt',
        'excel/Weapons.txt',
        'excel/Skills.txt',
        'excel/Levels.txt',
        'excel/MonStats.txt',
        'excel/ItemStatCost.txt',
        'excel/TreasureClassEx.txt',
        'excel/UniqueItems.txt',
    ]
    
    print("Testing file auto-detection:\n")
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"📁 File: {file_path}")
            
            # Test file type detection
            file_type, confidence, binding_key = detect_file_type(file_path)
            print(f"   Type: {file_type}")
            print(f"   Confidence: {confidence}")
            print(f"   Binding Key: {binding_key}")
            
            # Test encoding detection
            encoding = auto_detect_encoding(file_path)
            print(f"   Encoding: {encoding}")
            
            # Test working version check
            should_use_alt, alt_path, alt_msg = check_for_working_version(file_path)
            if should_use_alt:
                print(f"   ⚠️  Working version available: {alt_path}")
                print(f"   📝 Message: {alt_msg}")
            else:
                print(f"   ✅ No alternative version needed")
            
            print()
        else:
            print(f"❌ File not found: {file_path}")
            print()

def test_binding_integration():
    """Test integration with the binding system."""
    
    print("=== Testing Binding Integration ===\n")
    
    try:
        from file_bindings import get_binding_manager
        
        binding_manager = get_binding_manager()
        all_bindings = binding_manager.get_all_bindings()
        
        print(f"Available bindings: {len(all_bindings)}")
        
        # Test a few specific bindings
        test_bindings = ['cubemain', 'armor', 'weapons', 'skills']
        
        for binding_name in test_bindings:
            binding = binding_manager.get_binding(binding_name)
            if binding:
                print(f"✅ {binding_name}: {binding.txt_path}")
                print(f"   Description: {binding.get_description()[:100]}...")
            else:
                print(f"❌ {binding_name}: No binding found")
            print()
            
    except Exception as e:
        print(f"Error testing bindings: {e}")

if __name__ == "__main__":
    test_auto_detection()
    test_binding_integration() 