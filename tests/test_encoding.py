#!/usr/bin/env python3
"""
Test to examine character encoding differences between files.
"""

def check_encoding_differences():
    """Check for character encoding differences between the two files."""
    
    print("Checking character encoding differences...")
    
    # Read both files and compare the problematic line
    with open("CubeMain.txt", 'r', encoding='windows-1252') as f1:
        lines1 = f1.readlines()
    
    with open("CubeMainWorking.txt", 'r', encoding='windows-1252') as f2:
        lines2 = f2.readlines()
    
    # Check line 2481 (index 2480)
    if len(lines1) > 2480 and len(lines2) > 2480:
        line1 = lines1[2480].strip()
        line2 = lines2[2480].strip()
        
        print(f"Line 2481 from CubeMain.txt: {repr(line1[:80])}")
        print(f"Line 2481 from CubeMainWorking.txt: {repr(line2[:80])}")
        
        # Find the difference
        for i, (c1, c2) in enumerate(zip(line1, line2)):
            if c1 != c2:
                print(f"First difference at position {i}:")
                print(f"  CubeMain.txt: {repr(c1)} (ord: {ord(c1)})")
                print(f"  CubeMainWorking.txt: {repr(c2)} (ord: {ord(c2)})")
                break
    
    # Also try reading with different encodings
    print("\nTrying different encodings...")
    
    encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open("CubeMain.txt", 'r', encoding=encoding) as f:
                lines = f.readlines()
                if len(lines) > 2480:
                    line = lines[2480].strip()
                    if 'Rasha' in line:
                        print(f"  {encoding}: {repr(line[line.find('Rasha')-5:line.find('Rasha')+10])}")
        except Exception as e:
            print(f"  {encoding}: Error - {e}")

if __name__ == "__main__":
    check_encoding_differences() 