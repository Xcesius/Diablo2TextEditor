#!/usr/bin/env python3
"""Test the dynamic binding system."""

from file_bindings import get_binding_manager
from file_parser import detect_file_type
import os

def test_dynamic_binding():
    print("=== Testing Dynamic Binding System ===")
    
    # Get binding manager
    bm = get_binding_manager()
    print(f"1. Loaded {len(bm.get_all_bindings())} metadata files")
    
    # Test with CubeMain.txt if it exists
    if os.path.exists("CubeMain.txt"):
        print("\n2. Testing CubeMain.txt detection...")
        
        # Detect file type
        file_type, confidence, binding_key = detect_file_type("CubeMain.txt")
        print(f"   Detected: {file_type} (confidence: {confidence}, key: {binding_key})")
        
        # Try to create dynamic binding
        if binding_key:
            dynamic_binding = bm.create_dynamic_binding(binding_key, "CubeMain.txt")
            if dynamic_binding:
                print(f"   ✅ Dynamic binding created!")
                print(f"   Metadata: {dynamic_binding.get_description()[:100]}...")
                print(f"   Columns: {len(dynamic_binding.get_column_descriptions())} descriptions available")
            else:
                print(f"   ❌ Failed to create dynamic binding")
        else:
            print(f"   ❌ No binding key returned")
    else:
        print("\n2. CubeMain.txt not found, skipping test")
    
    print("\n3. Available metadata files:")
    for key in sorted(bm.get_all_bindings().keys())[:10]:
        print(f"   {key}")
    if len(bm.get_all_bindings()) > 10:
        print(f"   ... and {len(bm.get_all_bindings()) - 10} more")

if __name__ == "__main__":
    test_dynamic_binding() 