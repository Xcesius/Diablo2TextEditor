#!/usr/bin/env python3
"""
Analyze column-based quoting patterns in the raw CubeMain file content.
This will help us understand which columns should have quoted values.
"""

def analyze_raw_quoting():
    """Analyze which columns have quoted vs unquoted values in the raw file."""
    
    print("Loading raw CubeMainWorking.txt...")
    
    with open("CubeMainWorking.txt", 'r', encoding='windows-1252') as f:
        lines = f.readlines()
    
    print(f"Loaded {len(lines)} lines")
    
    # Skip the header line
    header_line = lines[0].strip()
    column_names = header_line.split('\t')
    print(f"Found {len(column_names)} columns")
    
    # Analyze each column for quoting patterns
    column_quote_stats = {}
    
    for col_idx in range(len(column_names)):
        quoted_count = 0
        unquoted_count = 0
        non_empty_count = 0
        quoted_examples = []
        unquoted_examples = []
        
        # Skip header line
        for line in lines[1:]:
            fields = line.strip().split('\t')
            
            # Handle cases where there might be fewer fields than columns
            if col_idx >= len(fields):
                continue
                
            value = fields[col_idx].strip()
            
            # Skip empty values
            if not value:
                continue
                
            non_empty_count += 1
            
            if value.startswith('"') and value.endswith('"'):
                quoted_count += 1
                if len(quoted_examples) < 10:
                    quoted_examples.append(value)
            else:
                unquoted_count += 1
                if len(unquoted_examples) < 10:
                    unquoted_examples.append(value)
        
        if non_empty_count > 0:
            quote_percentage = (quoted_count / non_empty_count) * 100
            column_quote_stats[col_idx] = {
                'name': column_names[col_idx] if col_idx < len(column_names) else f"Column {col_idx}",
                'quoted': quoted_count,
                'unquoted': unquoted_count,
                'total': non_empty_count,
                'quote_percentage': quote_percentage,
                'quoted_examples': quoted_examples,
                'unquoted_examples': unquoted_examples
            }
    
    print("\n" + "="*80)
    print("COLUMN QUOTING ANALYSIS (RAW FILE)")
    print("="*80)
    
    for col_idx, stats in column_quote_stats.items():
        if stats['total'] > 0:  # Only show columns with data
            print(f"\nColumn {col_idx:2d}: {stats['name']}")
            print(f"  Total non-empty values: {stats['total']:4d}")
            print(f"  Quoted values:          {stats['quoted']:4d} ({stats['quote_percentage']:5.1f}%)")
            print(f"  Unquoted values:        {stats['unquoted']:4d} ({100-stats['quote_percentage']:5.1f}%)")
            
            # Classify the column
            if stats['quote_percentage'] > 80:
                classification = "MOSTLY QUOTED"
            elif stats['quote_percentage'] < 20:
                classification = "MOSTLY UNQUOTED"
            else:
                classification = "MIXED"
            
            print(f"  Classification: {classification}")
            
            # Show examples for columns with quotes
            if stats['quoted'] > 0:
                print(f"  Quoted examples: {stats['quoted_examples'][:5]}")
            if stats['unquoted'] > 0:
                print(f"  Unquoted examples: {stats['unquoted_examples'][:5]}")
    
    print("\n" + "="*80)
    print("SUMMARY FOR SAVE FUNCTION")
    print("="*80)
    
    # Create lists for different quoting patterns
    mostly_quoted_cols = []
    mostly_unquoted_cols = []
    mixed_cols = []
    
    for col_idx, stats in column_quote_stats.items():
        if stats['quote_percentage'] > 80:
            mostly_quoted_cols.append((col_idx, stats['name']))
        elif stats['quote_percentage'] < 20:
            mostly_unquoted_cols.append((col_idx, stats['name']))
        else:
            mixed_cols.append((col_idx, stats['name'], stats['quote_percentage']))
    
    print(f"\nMostly quoted columns ({len(mostly_quoted_cols)}):")
    for col_idx, name in mostly_quoted_cols:
        print(f"  {col_idx:2d}: {name}")
    
    print(f"\nMostly unquoted columns ({len(mostly_unquoted_cols)}):")
    for col_idx, name in mostly_unquoted_cols:
        print(f"  {col_idx:2d}: {name}")
    
    print(f"\nMixed columns ({len(mixed_cols)}):")
    for col_idx, name, percentage in mixed_cols:
        print(f"  {col_idx:2d}: {name} ({percentage:.1f}% quoted)")

if __name__ == "__main__":
    analyze_raw_quoting() 