#!/usr/bin/env python3
"""
Test script to verify the file binding system works correctly.
"""

from file_bindings import get_binding_manager, get_file_binding, get_all_file_bindings
import os

def test_bindings():
    """Test the file binding system."""
    print("Testing Diablo II File Binding System")
    print("=" * 50)
    
    # Get the binding manager
    binding_manager = get_binding_manager()
    
    # Test basic functionality
    print(f"Total bindings found: {len(binding_manager.get_all_bindings())}")
    
    # Test specific bindings
    test_files = ["cubemain", "levels", "armor", "weapons", "skills"]
    
    for file_key in test_files:
        print(f"\nTesting binding for '{file_key}':")
        binding = get_file_binding(file_key)
        
        if binding:
            print(f"  ✓ Found binding")
            print(f"  ✓ JSON path: {binding.json_path}")
            print(f"  ✓ TXT path: {binding.txt_path}")
            print(f"  ✓ Base name: {binding.base_name}")
            
            # Test metadata loading
            description = binding.get_description()
            print(f"  ✓ Description: {description[:100]}..." if len(description) > 100 else f"  ✓ Description: {description}")
            
            # Test column descriptions
            column_descriptions = binding.get_column_descriptions()
            print(f"  ✓ Column descriptions: {len(column_descriptions)} columns")
            
            # Show first few columns
            if column_descriptions:
                print("  ✓ Sample columns:")
                for i, (col_name, col_desc) in enumerate(list(column_descriptions.items())[:3]):
                    print(f"    - {col_name}: {col_desc[:50]}..." if len(col_desc) > 50 else f"    - {col_name}: {col_desc}")
            
            # Test data loading
            try:
                data = binding.load_data()
                if data is not None:
                    print(f"  ✓ Data loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")
                else:
                    print("  ❌ Failed to load data")
            except Exception as e:
                print(f"  ❌ Error loading data: {e}")
        else:
            print(f"  ❌ No binding found")
    
    # Test case variations
    print(f"\nTesting case variations:")
    case_tests = [
        ("CubeMain", "cubemain"),
        ("LEVELS", "levels"),
        ("Armor", "armor"),
        ("weapons", "weapons")
    ]
    
    for upper_case, lower_case in case_tests:
        binding1 = get_file_binding(upper_case)
        binding2 = get_file_binding(lower_case)
        
        if binding1 and binding2 and binding1.base_name == binding2.base_name:
            print(f"  ✓ Case insensitive matching works for {upper_case}")
        else:
            print(f"  ❌ Case insensitive matching failed for {upper_case}")
    
    # List all available bindings
    print(f"\nAll available bindings:")
    all_bindings = get_all_file_bindings()
    for key, binding in sorted(all_bindings.items()):
        print(f"  {key} -> {os.path.basename(binding.txt_path)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_bindings() 