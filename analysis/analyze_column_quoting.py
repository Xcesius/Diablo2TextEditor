#!/usr/bin/env python3
"""
Analyze column-based quoting patterns in the working CubeMain file.
This will help us understand which columns should have quoted values.
"""
import pandas as pd
from file_parser import open_txt_file

def analyze_column_quoting():
    """Analyze which columns have quoted vs unquoted values in the working file."""
    
    print("Loading CubeMainWorking.txt...")
    df = open_txt_file("CubeMainWorking.txt")
    
    if df is None:
        print("Failed to load file!")
        return
    
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Analyze each column for quoting patterns
    column_quote_stats = {}
    
    for col_idx, col_name in enumerate(df.columns):
        quoted_count = 0
        unquoted_count = 0
        non_empty_count = 0
        
        for value in df[col_name]:
            if pd.isna(value) or value == '':
                continue
                
            non_empty_count += 1
            str_value = str(value).strip()
            
            if str_value.startswith('"') and str_value.endswith('"'):
                quoted_count += 1
            else:
                unquoted_count += 1
        
        if non_empty_count > 0:
            quote_percentage = (quoted_count / non_empty_count) * 100
            column_quote_stats[col_name] = {
                'column_index': col_idx,
                'quoted': quoted_count,
                'unquoted': unquoted_count,
                'total': non_empty_count,
                'quote_percentage': quote_percentage
            }
    
    print("\n" + "="*80)
    print("COLUMN QUOTING ANALYSIS")
    print("="*80)
    
    # Sort by column index for readability
    sorted_cols = sorted(column_quote_stats.items(), key=lambda x: x[1]['column_index'])
    
    for col_name, stats in sorted_cols:
        if stats['total'] > 0:  # Only show columns with data
            print(f"\nColumn {stats['column_index']:2d}: {col_name}")
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
    
    # Show some examples for mixed columns
    print("\n" + "="*80)
    print("DETAILED ANALYSIS OF MIXED COLUMNS")
    print("="*80)
    
    for col_name, stats in sorted_cols:
        if 20 <= stats['quote_percentage'] <= 80 and stats['total'] > 10:
            print(f"\nColumn: {col_name} ({stats['quote_percentage']:.1f}% quoted)")
            
            # Show some examples
            quoted_examples = []
            unquoted_examples = []
            
            for value in df[col_name]:
                if pd.isna(value) or value == '':
                    continue
                    
                str_value = str(value).strip()
                
                if str_value.startswith('"') and str_value.endswith('"'):
                    if len(quoted_examples) < 5:
                        quoted_examples.append(str_value)
                else:
                    if len(unquoted_examples) < 5:
                        unquoted_examples.append(str_value)
                
                if len(quoted_examples) >= 5 and len(unquoted_examples) >= 5:
                    break
            
            if quoted_examples:
                print(f"  Quoted examples: {quoted_examples}")
            if unquoted_examples:
                print(f"  Unquoted examples: {unquoted_examples}")

if __name__ == "__main__":
    analyze_column_quoting() 