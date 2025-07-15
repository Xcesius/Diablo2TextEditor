#!/usr/bin/env python3
"""
Analyze all JSON files in specs to create a database of unique column fingerprints
for improved file type detection.
"""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

def load_all_json_metadata() -> Dict[str, Dict]:
    """Load all JSON metadata files and return them as a dictionary."""
    metadata = {}
    json_dir = "specs"
    
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} not found!")
        return {}
    
    for file_path in Path(json_dir).glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_key = file_path.stem.lower()
                metadata[file_key] = {
                    'data': data,
                    'filename': data.get('filename', f"{file_path.stem}.txt")
                }
                print(f"Loaded: {file_path.name}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return metadata

def extract_columns_from_metadata(metadata: Dict[str, Dict]) -> Dict[str, Set[str]]:
    """Extract column names from each file's metadata."""
    file_columns = {}
    
    for file_key, info in metadata.items():
        columns = set()
        data_fields = info['data'].get('data_fields', [])
        
        for field in data_fields:
            if 'name' in field:
                column_name = field['name'].lower()
                columns.add(column_name)
                
                # Handle range fields like "weaponMod1Code (to weaponMod3Code)"
                if '(to ' in column_name:
                    base_part = column_name.split(' (to ')[0]
                    end_part = column_name.split(' (to ')[1].rstrip(')')
                    
                    # Extract the numeric pattern
                    import re
                    base_match = re.search(r'(.+?)(\d+)(.+)', base_part)
                    end_match = re.search(r'(.+?)(\d+)(.+)', end_part)
                    
                    if base_match and end_match:
                        prefix = base_match.group(1)
                        start_num = int(base_match.group(2))
                        middle = base_match.group(3)
                        end_num = int(end_match.group(2))
                        suffix = end_match.group(3)
                        
                        # Generate all columns in the range
                        for i in range(start_num, end_num + 1):
                            range_column = f"{prefix}{i}{middle}{suffix}"
                            columns.add(range_column)
                    
        file_columns[file_key] = columns
    
    return file_columns

def find_unique_columns(file_columns: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find columns that are unique to each file type."""
    # Count how many files each column appears in
    column_counts = Counter()
    for columns in file_columns.values():
        for column in columns:
            column_counts[column] += 1
    
    # Find unique columns (appear in only one file)
    unique_columns = {}
    for file_key, columns in file_columns.items():
        unique_to_file = []
        for column in columns:
            if column_counts[column] == 1:  # Only appears in this file
                unique_to_file.append(column)
        unique_columns[file_key] = unique_to_file
    
    return unique_columns

def find_distinctive_combinations(file_columns: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find combinations of columns that are distinctive to each file type."""
    distinctive_combinations = {}
    
    for file_key, columns in file_columns.items():
        # Look for combinations of 2-3 columns that together identify the file
        combinations = []
        
        # Try pairs of columns
        column_list = list(columns)
        for i in range(len(column_list)):
            for j in range(i + 1, len(column_list)):
                combo = {column_list[i], column_list[j]}
                
                # Check if this combination appears in any other file
                is_unique = True
                for other_key, other_columns in file_columns.items():
                    if other_key != file_key and combo.issubset(other_columns):
                        is_unique = False
                        break
                
                if is_unique:
                    combinations.append(list(combo))
        
        # Store the best combinations (prefer shorter ones)
        if combinations:
            combinations.sort(key=len)
            distinctive_combinations[file_key] = combinations[:3]  # Top 3 combinations
    
    return distinctive_combinations

def generate_fingerprint_database() -> Dict[str, Dict]:
    """Generate a comprehensive fingerprint database for file detection."""
    print("Loading JSON metadata files...")
    metadata = load_all_json_metadata()
    
    print(f"\nFound {len(metadata)} JSON files")
    
    print("\nExtracting column information...")
    file_columns = extract_columns_from_metadata(metadata)
    
    print("\nFinding unique columns...")
    unique_columns = find_unique_columns(file_columns)
    
    print("\nFinding distinctive column combinations...")
    distinctive_combinations = find_distinctive_combinations(file_columns)
    
    # Build the fingerprint database
    fingerprint_db = {}
    
    for file_key in file_columns:
        fingerprint_db[file_key] = {
            'filename': metadata[file_key]['filename'],
            'all_columns': list(file_columns[file_key]),
            'unique_columns': unique_columns.get(file_key, []),
            'distinctive_combinations': distinctive_combinations.get(file_key, []),
            'total_columns': len(file_columns[file_key])
        }
    
    return fingerprint_db

def print_fingerprint_report(fingerprint_db: Dict[str, Dict]):
    """Print a detailed report of the fingerprint analysis."""
    print("\n" + "="*80)
    print("DIABLO 2 FILE TYPE FINGERPRINT ANALYSIS")
    print("="*80)
    
    for file_key, info in sorted(fingerprint_db.items()):
        print(f"\n📁 {info['filename']} ({file_key})")
        print(f"   Total columns: {info['total_columns']}")
        
        if info['unique_columns']:
            print(f"   Unique columns ({len(info['unique_columns'])}): {', '.join(info['unique_columns'][:5])}")
            if len(info['unique_columns']) > 5:
                print(f"      ... and {len(info['unique_columns']) - 5} more")
        else:
            print("   No unique columns found")
        
        if info['distinctive_combinations']:
            print(f"   Distinctive combinations: {info['distinctive_combinations'][0]}")
        else:
            print("   No distinctive combinations found")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_files = len(fingerprint_db)
    files_with_unique = sum(1 for info in fingerprint_db.values() if info['unique_columns'])
    files_with_combinations = sum(1 for info in fingerprint_db.values() if info['distinctive_combinations'])
    
    print(f"Total files analyzed: {total_files}")
    print(f"Files with unique columns: {files_with_unique}")
    print(f"Files with distinctive combinations: {files_with_combinations}")
    print(f"Detection coverage: {max(files_with_unique, files_with_combinations)}/{total_files} files")

def save_fingerprint_database(fingerprint_db: Dict[str, Dict], output_file: str = "file_type_fingerprints.json"):
    """Save the fingerprint database to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprint_db, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Fingerprint database saved to: {output_file}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving fingerprint database: {e}")
        return False

def main():
    """Main function to run the analysis."""
    print("Starting Diablo 2 file type fingerprint analysis...")
    
    # Generate the fingerprint database
    fingerprint_db = generate_fingerprint_database()
    
    if not fingerprint_db:
        print("No data to analyze!")
        return
    
    # Print the analysis report
    print_fingerprint_report(fingerprint_db)
    
    # Save the database
    save_fingerprint_database(fingerprint_db)
    
    print("\n🎯 Analysis complete!")
    print("You can now use this fingerprint database to enhance the detect_file_type function.")

if __name__ == "__main__":
    main() 