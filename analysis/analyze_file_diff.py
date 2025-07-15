#!/usr/bin/env python3
"""
Analyze the differences between CubeMain.txt and CubeMainWorking.txt
"""

def analyze_files():
    file1 = 'CubeMain.txt'
    file2 = 'CubeMainWorking.txt'
    
    # Read raw bytes
    with open(file1, 'rb') as f:
        data1 = f.read()
    
    with open(file2, 'rb') as f:
        data2 = f.read()
    
    print(f"File sizes:")
    print(f"  {file1}: {len(data1)} bytes")
    print(f"  {file2}: {len(data2)} bytes")
    print(f"  Difference: {len(data2) - len(data1)} bytes")
    
    # Look at first 200 bytes of each file
    print(f"\nFirst 200 bytes of {file1}:")
    print(repr(data1[:200]))
    
    print(f"\nFirst 200 bytes of {file2}:")
    print(repr(data2[:200]))
    
    # Count line endings
    print(f"\nLine ending analysis:")
    print(f"  {file1}: \\r\\n count: {data1.count(b'\\r\\n')}, \\n count: {data1.count(b'\\n')}, \\r count: {data1.count(b'\\r')}")
    print(f"  {file2}: \\r\\n count: {data2.count(b'\\r\\n')}, \\n count: {data2.count(b'\\n')}, \\r count: {data2.count(b'\\r')}")
    
    # Look for BOM or other encoding markers
    print(f"\nEncoding analysis:")
    print(f"  {file1} starts with BOM: {data1.startswith(b'\\xef\\xbb\\xbf')}")
    print(f"  {file2} starts with BOM: {data2.startswith(b'\\xef\\xbb\\xbf')}")
    
    # Count tabs vs spaces
    print(f"\nWhitespace analysis:")
    print(f"  {file1}: tabs: {data1.count(b'\\t')}, spaces: {data1.count(b' ')}")
    print(f"  {file2}: tabs: {data2.count(b'\\t')}, spaces: {data2.count(b' ')}")
    
    # Find first difference
    min_len = min(len(data1), len(data2))
    first_diff = None
    for i in range(min_len):
        if data1[i] != data2[i]:
            first_diff = i
            break
    
    if first_diff is not None:
        print(f"\nFirst difference at byte {first_diff}:")
        start = max(0, first_diff - 20)
        end = min(len(data1), first_diff + 20)
        
        print(f"  {file1}[{start}:{end}]: {repr(data1[start:end])}")
        print(f"  {file2}[{start}:{end}]: {repr(data2[start:end])}")
    else:
        print(f"\nNo differences found in first {min_len} bytes")
        if len(data1) != len(data2):
            print(f"But files have different lengths: {len(data1)} vs {len(data2)}")

if __name__ == "__main__":
    analyze_files() 