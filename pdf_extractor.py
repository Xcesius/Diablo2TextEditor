#!/usr/bin/env python3
"""
PDF Data Extractor for Diablo II Data Guide

This script extracts both raw text and structured tables from PDF files,
specifically designed for D2R_DataGuide_2.7.pdf. Uses multiple extraction
methods for comprehensive data recovery.

Dependencies:
    pip install pdfminer.six camelot-py[cv] tabula-py

Alternative for camelot if OpenCV issues:
    pip install "camelot-py[base]"
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        missing.append("pdfminer.six")
    
    try:
        import camelot
    except ImportError:
        missing.append("camelot-py")
    
    try:
        import tabula
    except ImportError:
        missing.append("tabula-py")
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Install with: pip install pdfminer.six camelot-py[cv] tabula-py")
        return False
    
    return True

def extract_text_pdfminer(pdf_path: str) -> Dict[str, Any]:
    """Extract raw text using pdfminer.six."""
    from pdfminer.high_level import extract_pages, extract_text
    from pdfminer.layout import LTTextContainer, LTChar
    
    logger.info("Extracting text with pdfminer.six...")
    
    try:
        # Extract all text
        full_text = extract_text(pdf_path)
        
        # Extract text by pages
        pages = []
        page_num = 1
        
        for page_layout in extract_pages(pdf_path):
            page_text = ""
            text_elements = []
            
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    element_text = element.get_text().strip()
                    if element_text:
                        page_text += element_text + "\n"
                        
                        # Try to extract formatting info
                        text_elements.append({
                            "text": element_text,
                            "bbox": [element.x0, element.y0, element.x1, element.y1],
                            "font_info": extract_font_info(element)
                        })
            
            pages.append({
                "page_number": page_num,
                "text": page_text.strip(),
                "elements": text_elements
            })
            page_num += 1
        
        return {
            "method": "pdfminer.six",
            "full_text": full_text,
            "pages": pages,
            "total_pages": len(pages)
        }
    
    except Exception as e:
        logger.error(f"Error extracting text with pdfminer: {e}")
        return {"method": "pdfminer.six", "error": str(e)}

def extract_font_info(element) -> Dict[str, Any]:
    """Extract font information from text element."""
    from pdfminer.layout import LTChar
    
    fonts = {}
    for item in element:
        if isinstance(item, LTChar):
            font_name = getattr(item, 'fontname', 'unknown')
            font_size = getattr(item, 'height', 0)
            fonts[font_name] = font_size
    
    return fonts

def extract_tables_camelot(pdf_path: str) -> Dict[str, Any]:
    """Extract tables using camelot."""
    try:
        import camelot
        
        logger.info("Extracting tables with camelot...")
        
        # Extract all tables from all pages
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        
        extracted_tables = []
        
        for i, table in enumerate(tables):
            table_data = {
                "table_number": i + 1,
                "page": table.page,
                "accuracy": table.accuracy,
                "whitespace": table.whitespace,
                "order": table.order,
                "data": table.df.to_dict('records'),  # Convert to list of dicts
                "raw_data": table.df.values.tolist(),  # Raw 2D array
                "columns": table.df.columns.tolist(),
                "shape": list(table.df.shape)
            }
            extracted_tables.append(table_data)
        
        return {
            "method": "camelot",
            "total_tables": len(extracted_tables),
            "tables": extracted_tables
        }
    
    except Exception as e:
        logger.error(f"Error extracting tables with camelot: {e}")
        return {"method": "camelot", "error": str(e)}

def extract_tables_tabula(pdf_path: str) -> Dict[str, Any]:
    """Extract tables using tabula-py."""
    try:
        import tabula
        
        logger.info("Extracting tables with tabula...")
        
        # Extract all tables from all pages
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        extracted_tables = []
        
        for i, df in enumerate(tables):
            table_data = {
                "table_number": i + 1,
                "data": df.to_dict('records'),
                "raw_data": df.values.tolist(),
                "columns": df.columns.tolist(),
                "shape": list(df.shape)
            }
            extracted_tables.append(table_data)
        
        return {
            "method": "tabula-py",
            "total_tables": len(extracted_tables),
            "tables": extracted_tables
        }
    
    except Exception as e:
        logger.error(f"Error extracting tables with tabula: {e}")
        return {"method": "tabula-py", "error": str(e)}

def save_json(data: Dict[str, Any], filename: str) -> None:
    """Save data to JSON file with pretty formatting."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved data to {filename}")
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")

def extract_pdf_data(pdf_path: str, output_dir: str = "extracted_data") -> None:
    """Main extraction function that combines all methods."""
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(pdf_path).stem
    
    logger.info(f"Starting extraction of {pdf_path}")
    
    # Extract text with pdfminer
    text_data = extract_text_pdfminer(pdf_path)
    text_filename = f"{output_dir}/{base_name}_text_{timestamp}.json"
    save_json(text_data, text_filename)
    
    # Extract tables with camelot
    camelot_data = extract_tables_camelot(pdf_path)
    camelot_filename = f"{output_dir}/{base_name}_tables_camelot_{timestamp}.json"
    save_json(camelot_data, camelot_filename)
    
    # Extract tables with tabula
    tabula_data = extract_tables_tabula(pdf_path)
    tabula_filename = f"{output_dir}/{base_name}_tables_tabula_{timestamp}.json"
    save_json(tabula_data, tabula_filename)
    
    # Create combined summary
    summary = {
        "extraction_timestamp": timestamp,
        "source_file": pdf_path,
        "methods_used": ["pdfminer.six", "camelot", "tabula-py"],
        "output_files": {
            "text_extraction": text_filename,
            "camelot_tables": camelot_filename,
            "tabula_tables": tabula_filename
        },
        "summary": {
            "total_pages": text_data.get("total_pages", 0),
            "camelot_tables_found": camelot_data.get("total_tables", 0),
            "tabula_tables_found": tabula_data.get("total_tables", 0),
            "text_extraction_success": "error" not in text_data,
            "camelot_success": "error" not in camelot_data,
            "tabula_success": "error" not in tabula_data
        }
    }
    
    summary_filename = f"{output_dir}/{base_name}_summary_{timestamp}.json"
    save_json(summary, summary_filename)
    
    logger.info("Extraction complete!")
    logger.info(f"Check the '{output_dir}' directory for output files")
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Source PDF: {pdf_path}")
    print(f"Total pages: {summary['summary']['total_pages']}")
    print(f"Camelot tables found: {summary['summary']['camelot_tables_found']}")
    print(f"Tabula tables found: {summary['summary']['tabula_tables_found']}")
    print(f"\nOutput directory: {output_dir}/")
    print(f"Summary file: {summary_filename}")
    print("="*60)

def main():
    """Main entry point."""
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Default PDF file
    pdf_file = "D2R_DataGuide_2.7.pdf"
    
    # Allow command line argument for different PDF
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(pdf_file):
        logger.error(f"PDF file '{pdf_file}' not found in current directory")
        logger.info("Usage: python pdf_extractor.py [pdf_file_path]")
        sys.exit(1)
    
    # Run extraction
    extract_pdf_data(pdf_file)

if __name__ == "__main__":
    main() 