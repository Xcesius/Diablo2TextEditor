
def compare_files(file1_path, file2_path):
    print(f"Comparing {file1_path} and {file2_path}")
    try:
        with open(file1_path, 'r', encoding='windows-1252', errors='surrogateescape') as f1, \
             open(file2_path, 'r', encoding='windows-1252', errors='surrogateescape') as f2:
            
            f1_lines = f1.readlines()
            f2_lines = f2.readlines()

            if len(f1_lines) != len(f2_lines):
                print(f"Files have different number of lines: {len(f1_lines)} vs {len(f2_lines)}")
                # Continue comparison up to the shorter file's length

            for i, (line1, line2) in enumerate(zip(f1_lines, f2_lines)):
                if line1 != line2:
                    print(f"Files differ at line {i+1}:")
                    print(f"<{file1_path}>: {line1.rstrip()}")
                    print(f"<{file2_path}>: {line2.rstrip()}")
                    
                    fields1 = line1.rstrip().split('\t')
                    fields2 = line2.rstrip().split('\t')

                    if len(fields1) != len(fields2):
                        print(f"  - Different number of fields: {len(fields1)} vs {len(fields2)}")
                    else:
                        print("  - Field differences:")
                        for j, (field1, field2) in enumerate(zip(fields1, fields2)):
                            if field1 != field2:
                                print(f"    - Field {j+1}: <{field1}> vs <{field2}>")
                    return # Stop after first difference
            
            if len(f1_lines) == len(f2_lines):
                print("✅ Files are identical.")
            else:
                print("Partial comparison complete. No differences found in the overlapping part.")


    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")


compare_files("CubeMain.txt", "CubeMainNotWorking.txt") 