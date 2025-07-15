# PDF Extraction Guide

This guide explains how to use the `pdf_extractor.py` script to extract data from the Diablo II Data Guide PDF.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_pdf.txt
```

If you encounter issues with OpenCV, try the alternative installation:
```bash
pip install pdfminer.six "camelot-py[base]" tabula-py pandas
```

## Usage

### Basic Usage
```bash
python pdf_extractor.py
```
This will extract data from `D2R_DataGuide_2.7.pdf` in the current directory.

### Custom PDF File
```bash
python pdf_extractor.py path/to/your/file.pdf
```

## Output

The script creates an `extracted_data/` directory with timestamped JSON files:

- `**_text_YYYYMMDD_HHMMSS.json` - Raw text extraction using pdfminer.six
- `**_tables_camelot_YYYYMMDD_HHMMSS.json` - Table extraction using camelot
- `**_tables_tabula_YYYYMMDD_HHMMSS.json` - Table extraction using tabula-py
- `**_summary_YYYYMMDD_HHMMSS.json` - Combined summary and metadata

## What Each Method Does

### pdfminer.six (Text Extraction)
- Extracts all raw text from the PDF
- Preserves page structure
- Includes font information and positioning
- Best for paragraphs, descriptions, and unstructured content

### camelot (Table Extraction)
- Detects table boundaries using lattice/stream algorithms
- Good for well-formatted tables with clear borders
- Provides accuracy metrics for each table

### tabula-py (Table Extraction)
- Java-based table extraction (requires Java)
- Alternative approach, sometimes catches tables camelot misses
- Good fallback option

## Post-Processing Tips

The extracted JSON will need manual cleanup:

1. **Text Data**: Look in the `pages` array for structured content
2. **Tables**: Compare camelot vs tabula results - they often complement each other
3. **Manual Review**: Check accuracy scores and visually verify important tables
4. **Data Cleaning**: Remove empty rows/columns, fix merged cells, standardize formats

## Troubleshooting

### Java Not Found (tabula-py)
If you get Java errors, install Java JRE 8+:
- Windows: Download from Oracle or use `choco install openjdk`
- macOS: `brew install openjdk`
- Linux: `sudo apt install default-jre`

### OpenCV Issues (camelot)
If camelot fails to install:
```bash
pip install "camelot-py[base]" 
```

### Missing Dependencies
The script will check dependencies and provide installation instructions if anything is missing. 