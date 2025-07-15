#!/usr/bin/env python3
"""
Simple PDF to Text extractor for D2R_DataGuide_2.7.pdf
Extracts all text from all pages and saves it to a file.
"""

import os
import sys
from pathlib import Path

def extract_all_text():
    """Extract all text from the PDF."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        print("Error: pdfminer.six not installed")
        print("Install with: pip install pdfminer.six")
        return False
    
    pdf_path = "D2R_DataGuide_2.7.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    print(f"Extracting text from {pdf_path}...")
    
    try:
        # Extract all text from all pages
        full_text = extract_text(pdf_path)
        
        # Save to text file
        output_file = "D2R_DataGuide_2.7_full_text.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"✅ Text extraction complete!")
        print(f"📄 Output saved to: {output_file}")
        print(f"📊 Total characters: {len(full_text):,}")
        print(f"📋 Total lines: {len(full_text.splitlines()):,}")
        
        return True
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return False

if __name__ == "__main__":
    extract_all_text() 