

import csv
from collections import defaultdict
import json
import os
import sys

def analyze_columns(file_path):
    """
    Analyzes a tab-separated file to find all unique values for each column.

    Args:
        file_path (str): The path to the file to analyze.

    Returns:
        dict: A dictionary where keys are column headers and values are sets
              of unique values for that column.
    """
    column_values = defaultdict(set)
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            for row in reader:
                for i, value in enumerate(row):
                    if i < len(header):
                        column_values[header[i]].add(value)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    # Convert sets to sorted lists for JSON serialization
    for column in column_values:
        column_values[column] = sorted(list(column_values[column]))
        
    return dict(column_values)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python column_analyzer.py <file_path>")
        sys.exit(1)

    file_to_analyze = sys.argv[1]
    
    if not os.path.exists(file_to_analyze):
        print(f"Error: File not found at {file_to_analyze}")
        sys.exit(1)

    unique_values = analyze_columns(file_to_analyze)
    
    if unique_values:
        output_filename = os.path.splitext(os.path.basename(file_to_analyze))[0] + '.json'
        output_path = os.path.join('specs', output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_values, f, indent=4)
            
        print(f"Successfully analyzed {file_to_analyze} and saved the results to {output_path}")


