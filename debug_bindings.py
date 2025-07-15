#!/usr/bin/env python3
"""Debug script to test binding system after moving JSON files to specs."""

from file_bindings import reset_binding_manager, get_binding_manager

def test_bindings():
    print("=== Testing File Binding System ===")
    
    # Reset the global binding manager to force re-discovery
    print("1. Resetting binding manager...")
    reset_binding_manager()
    
    # Get fresh binding manager
    print("2. Creating fresh binding manager...")
    bm = get_binding_manager()
    
    print(f"3. Bindings loaded: {len(bm.get_all_bindings())}")
    print(f"   JSON dir: {bm.json_dir}")
    print(f"   TXT dir: {bm.txt_dir}")
    
    # Test specific CubeMain binding
    print("4. Testing CubeMain binding...")
    cubemain = bm.get_binding('cubemain')
    print(f"   CubeMain binding found: {cubemain is not None}")
    
    if cubemain:
        print(f"   Base name: {cubemain.base_name}")
        print(f"   JSON path: {cubemain.json_path}")
        print(f"   TXT path: {cubemain.txt_path}")
    
    # List first few bindings
    print("5. Available bindings:")
    for i, (key, binding) in enumerate(bm.get_all_bindings().items()):
        if i < 5:  # Show first 5
            print(f"   {key} -> {binding.txt_path}")
        elif i == 5:
            print(f"   ... and {len(bm.get_all_bindings()) - 5} more")
            break

if __name__ == "__main__":
    test_bindings() 