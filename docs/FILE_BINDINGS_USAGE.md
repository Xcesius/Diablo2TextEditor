# Diablo II File Binding System

The file binding system connects JSON metadata files in `diablo2_data_files/` to their corresponding `.txt` data files in `excel/`. This provides enhanced functionality with metadata, column descriptions, and file information.

## Features

- **Automatic Binding**: Automatically discovers and binds JSON files to their corresponding .txt files
- **Case-Insensitive Matching**: Handles various capitalizations (e.g., `cubemain.txt`, `CubeMain.txt`, `CUBEMAIN.txt`)
- **Rich Metadata**: Provides file descriptions, column explanations, and data field information
- **Enhanced UI**: New dialog for browsing and selecting files with metadata display
- **Column Help**: Click on column headers to see detailed descriptions from the metadata

## How to Use

### Using the Bound File Dialog

1. **Open the Application**: Launch the Diablo II .txt Editor
2. **Access Bound Files**: Go to `File > Open Bound File...` (or press `Ctrl+B`)
3. **Browse Files**: The dialog shows all available bound files with their metadata
4. **Select File**: Click on a file in the list to see its description and column information
5. **Open File**: Click "Open File" to load the selected file with full metadata support

### Enhanced Features

- **Window Title**: Shows the current file name and binding information
- **Column Descriptions**: Click on any column header to see detailed descriptions from the metadata
- **File Information**: View comprehensive information about each data file including:
  - File description and purpose
  - Column definitions and explanations
  - Data structure information

### Available Bound Files

Currently bound files include:
- `CubeMain.txt` - Horadric Cube recipes
- `Levels.txt` - Area level configurations
- `Armor.txt` - Armor item definitions
- `Weapons.txt` - Weapon item definitions
- `Skills.txt` - Skill definitions and properties
- `Monsters.txt` - Monster statistics
- And many more...

## Technical Details

### File Structure

```
diablo2_data_files/          # JSON metadata files
├── CubeMain.json           # Metadata for CubeMain.txt
├── Levels.json             # Metadata for Levels.txt
├── armor.json              # Metadata for Armor.txt
└── ...

excel/                       # Actual data files
├── CubeMain.txt            # Cube recipe data
├── Levels.txt              # Level configuration data
├── Armor.txt               # Armor definitions
└── ...
```

### Binding Process

1. **Discovery**: The system scans both directories for files
2. **Matching**: JSON files are matched to .txt files using case-insensitive comparison
3. **Metadata Loading**: JSON files are parsed to extract descriptions and column information
4. **Integration**: Bindings are integrated into the UI for enhanced functionality

### Fallback Behavior

- If no binding is found for a file, the application falls back to the original column description system
- Regular file opening (`File > Open...`) still works for any .txt file
- The system gracefully handles missing files or metadata

## Benefits

1. **Better Understanding**: Rich metadata helps understand file structure and purpose
2. **Enhanced Productivity**: Column descriptions make editing easier and more accurate
3. **Data Integrity**: Better understanding reduces errors when modifying files
4. **User Experience**: Intuitive browsing and selection of data files

## Maintenance

The binding system automatically refreshes when the application starts. If you add new JSON files or .txt files, restart the application to pick up the changes. 