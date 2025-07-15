#!/usr/bin/env python3
"""
Diablo II PDF Data Browser

Helper script to browse and search through the extracted PDF data.
Makes it easier to find specific information in the large text file.
"""

import json
import re
from pathlib import Path
import argparse
from typing import List, Dict, Any

def load_extracted_data(json_file: str) -> Dict[str, Any]:
    """Load the extracted JSON data."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {json_file}: {e}")
        return {}

def search_text(data: Dict[str, Any], search_term: str, case_sensitive: bool = False) -> List[Dict]:
    """Search for a term across all pages."""
    results = []
    
    if 'pages' not in data:
        return results
    
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(search_term), flags)
    
    for page in data['pages']:
        page_num = page.get('page_number', 0)
        page_text = page.get('text', '')
        
        matches = list(pattern.finditer(page_text))
        if matches:
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(page_text), match.end() + 100)
                context = page_text[start:end]
                
                results.append({
                    'page': page_num,
                    'match_position': match.start(),
                    'context': context,
                    'full_page_text': page_text
                })
    
    return results

def search_patterns(data: Dict[str, Any], patterns: List[str]) -> Dict[str, List]:
    """Search for multiple regex patterns."""
    results = {}
    
    if 'pages' not in data:
        return results
    
    for pattern_str in patterns:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = []
        
        for page in data['pages']:
            page_num = page.get('page_number', 0)
            page_text = page.get('text', '')
            
            for match in pattern.finditer(page_text):
                start = max(0, match.start() - 50)
                end = min(len(page_text), match.end() + 50)
                context = page_text[start:end]
                
                matches.append({
                    'page': page_num,
                    'match': match.group(),
                    'context': context
                })
        
        results[pattern_str] = matches
    
    return results

def extract_tables_from_text(data: Dict[str, Any]) -> List[Dict]:
    """Try to find table-like structures in the text."""
    tables = []
    
    if 'pages' not in data:
        return tables
    
    # Patterns that might indicate tables
    table_patterns = [
        r'^\s*\|.*\|.*\|',  # Pipe-separated
        r'^\s*\+[-=]+\+',   # ASCII table borders
        r'^\s*[A-Za-z\s]+\t+[A-Za-z0-9\s]+\t+',  # Tab-separated
        r'^\s*[A-Za-z\s]+\s{3,}[A-Za-z0-9\s]+\s{3,}',  # Space-separated columns
    ]
    
    for page in data['pages']:
        page_num = page.get('page_number', 0)
        page_text = page.get('text', '')
        
        lines = page_text.split('\n')
        current_table = []
        
        for i, line in enumerate(lines):
            is_table_line = any(re.match(pattern, line) for pattern in table_patterns)
            
            if is_table_line:
                current_table.append(line.strip())
            else:
                if len(current_table) >= 3:  # At least 3 lines for a table
                    tables.append({
                        'page': page_num,
                        'line_start': i - len(current_table),
                        'line_end': i,
                        'content': current_table,
                        'type': 'detected_table'
                    })
                current_table = []
        
        # Check for table at end of page
        if len(current_table) >= 3:
            tables.append({
                'page': page_num,
                'line_start': len(lines) - len(current_table),
                'line_end': len(lines),
                'content': current_table,
                'type': 'detected_table'
            })
    
    return tables

def show_page(data: Dict[str, Any], page_num: int) -> None:
    """Display a specific page."""
    if 'pages' not in data:
        print("No pages found in data")
        return
    
    for page in data['pages']:
        if page.get('page_number') == page_num:
            print(f"\n{'='*60}")
            print(f"PAGE {page_num}")
            print(f"{'='*60}")
            print(page.get('text', 'No text found'))
            return
    
    print(f"Page {page_num} not found")

def find_diablo_data(data: Dict[str, Any]) -> Dict[str, List]:
    """Search for common Diablo II data types."""
    diablo_patterns = {
        'items': [
            r'[A-Za-z\s]+\s+\d+\s+\d+\s+\d+',  # Item stats
            r'(Unique|Set|Rare|Magic|Normal)\s+[A-Za-z\s]+',
            r'(Armor|Weapon|Shield|Helm|Boot|Glove|Belt|Ring|Amulet)',
        ],
        'skills': [
            r'(Skill|Spell|Ability):\s*[A-Za-z\s]+',
            r'Level\s+\d+:\s+[A-Za-z\s]+',
            r'(Mana|Stamina|Life)\s+Cost:\s*\d+',
        ],
        'monsters': [
            r'(Monster|Enemy|Boss):\s*[A-Za-z\s]+',
            r'(HP|Health|Life):\s*\d+',
            r'(Attack|Damage):\s*\d+',
        ],
        'areas': [
            r'(Area|Zone|Level|Act)\s+\d+',
            r'(Wilderness|Dungeon|Town|Cave)',
        ]
    }
    
    results = {}
    for category, patterns in diablo_patterns.items():
        results[category] = search_patterns(data, patterns)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Browse extracted Diablo II PDF data')
    parser.add_argument('--file', '-f', help='JSON file to browse (default: latest)')
    parser.add_argument('--search', '-s', help='Search for a term')
    parser.add_argument('--page', '-p', type=int, help='Show specific page')
    parser.add_argument('--patterns', action='store_true', help='Search for Diablo II patterns')
    parser.add_argument('--tables', action='store_true', help='Find table-like structures')
    parser.add_argument('--case-sensitive', action='store_true', help='Case sensitive search')
    
    args = parser.parse_args()
    
    # Find the latest text extraction file if not specified
    if not args.file:
        extracted_dir = Path('extracted_data')
        if not extracted_dir.exists():
            print("No extracted_data directory found. Run pdf_extractor.py first.")
            return
        
        text_files = list(extracted_dir.glob('*_text_*.json'))
        if not text_files:
            print("No text extraction files found.")
            return
        
        # Get the latest file
        args.file = max(text_files, key=lambda f: f.stat().st_mtime)
        print(f"Using latest file: {args.file}")
    
    # Load data
    data = load_extracted_data(args.file)
    if not data:
        return
    
    print(f"Loaded data from {data.get('total_pages', 0)} pages")
    
    # Execute requested action
    if args.search:
        results = search_text(data, args.search, args.case_sensitive)
        print(f"\nFound {len(results)} matches for '{args.search}':")
        for i, result in enumerate(results[:10]):  # Show first 10
            print(f"\n{i+1}. Page {result['page']}:")
            print(f"   {result['context'][:200]}...")
    
    elif args.page:
        show_page(data, args.page)
    
    elif args.patterns:
        print("Searching for Diablo II data patterns...")
        results = find_diablo_data(data)
        for category, patterns in results.items():
            total_matches = sum(len(matches) for matches in patterns.values())
            if total_matches > 0:
                print(f"\n{category.upper()}: {total_matches} matches")
                for pattern, matches in patterns.items():
                    if matches:
                        print(f"  Pattern '{pattern}': {len(matches)} matches")
                        for match in matches[:3]:  # Show first 3
                            print(f"    Page {match['page']}: {match['context'][:100]}...")
    
    elif args.tables:
        print("Looking for table structures...")
        tables = extract_tables_from_text(data)
        print(f"Found {len(tables)} potential tables:")
        for i, table in enumerate(tables[:5]):  # Show first 5
            print(f"\n{i+1}. Page {table['page']}, lines {table['line_start']}-{table['line_end']}:")
            for line in table['content'][:5]:  # Show first 5 lines
                print(f"   {line}")
            if len(table['content']) > 5:
                print(f"   ... ({len(table['content']) - 5} more lines)")
    
    else:
        # Interactive mode
        print("\nInteractive mode. Try these commands:")
        print("  --search 'term'      - Search for text")
        print("  --page N             - Show page N")
        print("  --patterns           - Find Diablo II data")
        print("  --tables             - Find table structures")

if __name__ == "__main__":
    main() 