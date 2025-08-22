# Diablo II Text Editor

A Python-based editor for Diablo II game data files, supporting advanced text file parsing, data binding, and file format detection.

## Project Structure

```
Diablo2TextEditor/
├── main.py                    # Main application entry point
├── ui.py                      # User interface implementation
├── file_parser.py             # Core file parsing functionality
├── file_bindings.py           # Data file binding system
├── custom_widgets.py          # Custom UI widgets
├── file_type_fingerprints.json # File format detection patterns
├── column_descriptions.py     # Column metadata and descriptions
├── verify_format.py           # File format verification tools
├── debug_columns.py           # Column debugging utilities
│
├── analysis/                  # Analysis and diagnostic tools
│   ├── analyze_unique_columns.py
│   ├── analyze_file_diff.py
│   ├── analyze_raw_quoting.py
│   └── analyze_column_quoting.py
│
├── tests/                     # Test files
│   ├── test_*.py             # Python test files
│   └── test_*.txt            # Test data files
│
├── docs/                      # Documentation
│   ├── AUTO_DETECTION_FEATURES.md
│   ├── ENHANCED_DETECTION_GUIDE.md
│   ├── FILE_BINDINGS_USAGE.md
│   └── PDF_EXTRACTION_GUIDE.md
│
├── backups/                   # Backup files
│   └── *.bak                 # Timestamped backup files
│
├── specs/                     # JSON metadata files and specifications  
├── extracted_data/            # Extracted PDF data
├── data/                      # Additional data files
├── *.txt                      # Game data files (CubeMain.txt, Levels.txt, etc.)
└── *.json                     # Large fingerprint databases
```
## Features

- **File Binding System**: Automatic mapping between JSON metadata and text data files
- **Advanced Parsing**: Sophisticated text file parsing with format detection
- **UI Editor**: Full-featured graphical interface for editing game data
- **Format Validation**: Comprehensive file format verification
- **PDF Extraction**: Tools for extracting data from PDF documentation
- **Drag-and-Drop Loading**: Open any supported `.txt` file by simply dropping it onto the editor window

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   #If you want only the PDF part use this.
   ```bash
   pip install -r requirements_pdf.txt
   ```

3. Run the application:
   ```bash
   python main_v2.py
   ```

## Usage

### Running Tests
```bash
python -m pytest tests/
```

### File Analysis
```bash
# Analyze column patterns
python analysis/analyze_unique_columns.py

# Compare file differences  
python analysis/analyze_file_diff.py

# Check quotation patterns
python analysis/analyze_raw_quoting.py
```

### PDF Data Extraction
```bash
python pdf_extractor.py
python browse_extracted_data.py
```

## Dynamic File Binding System

The project uses an advanced dynamic binding system that automatically applies JSON metadata to .txt files based on auto-detection:

```python
from file_bindings import get_binding_manager

# The system automatically detects file types and applies metadata
# when you open any .txt file from anywhere on your system
binding_manager = get_binding_manager()

# For detected file types, metadata is automatically bound
# providing column descriptions and file information
```

## Development

- All test files are in the `tests/` directory
- Analysis tools are in the `analysis/` directory  
- Documentation is in the `docs/` directory
- Backup files are automatically stored in `backups/`
