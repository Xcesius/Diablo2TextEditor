# Auto-Detection Features for Diablo 2 Text Editor

## Overview
The Diablo 2 Text Editor now includes intelligent auto-detection capabilities that automatically identify file types, encodings, and apply appropriate bindings when opening files.

## Key Features

### 1. File Type Detection
- **High Confidence Detection**: Recognizes 33+ known Diablo 2 data files by filename
- **Content Analysis**: Analyzes file content for common Diablo 2 patterns when filename matching fails
- **Binding Integration**: Automatically applies appropriate metadata bindings for known files

### 2. Encoding Detection
- **Multi-Encoding Support**: Automatically detects best encoding from: windows-1252, utf-8, latin-1, cp1252, iso-8859-1
- **Fallback Strategy**: Uses windows-1252 as default fallback for Diablo 2 files
- **Smart Detection**: Reads file content to determine optimal encoding

### 3. Working Version Detection
- **CubeMain.txt Special Case**: Always suggests CubeMainWorking.txt when opening CubeMain.txt (per system requirement)
- **Pattern Recognition**: Detects files with "working", "fixed", "correct", or "good" versions
- **User Choice**: Allows users to choose between original and working versions

### 4. Enhanced User Experience
- **Detection Dialog**: Shows comprehensive detection results with confidence levels
- **Manual Override**: Option to manually select bindings if auto-detection is incorrect
- **Success Feedback**: Clear confirmation of what was detected and loaded
- **Detailed Information**: Shows file type, encoding, and binding information

## Supported File Types

### High Confidence Detection (57 files):
- CubeMain.txt, CubeMainWorking.txt, Armor.txt, Weapons.txt, Misc.txt
- ItemStatCost.txt, ItemTypes.txt, CharStats.txt
- Skills.txt, Levels.txt, MonStats.txt
- TreasureClassEx.txt, UniqueItems.txt, SetItems.txt
- MagicPrefix.txt, MagicSuffix.txt, AutoMagic.txt
- Runes.txt, Experience.txt, Gamble.txt
- Hireling.txt, Missiles.txt, Properties.txt
- Skilldesc.txt, States.txt, MonProp.txt
- MonLvl.txt, MonStats2.txt, MonType.txt
- MonUMod.txt, PetType.txt, Sets.txt
- DifficultyLevels.txt, ItemRatio.txt, SkillCalc.txt
- MonAi.txt, ActInfo.txt, AutoMap.txt
- Belts.txt, Books.txt, Gems.txt
- HirelingDesc.txt, Inventory.txt, LevelGroups.txt
- LvlMaze.txt, LvlPrest.txt, LvlSub.txt
- LvlTypes.txt, LvlWarp.txt, MonEquip.txt
- MonPreset.txt, MonSeq.txt, MonSounds.txt
- NPC.txt, Objects.txt, ObjGroup.txt
- ObjPreset.txt, Overlay.txt, QualityItems.txt
- RarePrefix.txt, RareSuffix.txt, Shrines.txt
- SoundEnviron.txt, Sounds.txt, SuperUniques.txt
- UniqueAppellation.txt, UniqueSuffix.txt, UniqueTitle.txt
- WanderingMon.txt

### Content-Based Detection:
- Generic data files (containing 'index', 'name' columns)
- Item data files (containing 'code', 'type' columns)
- Character data files (containing 'level', 'class' columns)
- Stat data files (containing 'stat' columns)
- Treasure data files (containing 'treasure class' columns)
- Recipe data files (containing 'input', 'output' columns)

## How It Works

### Opening a File:
1. **Working Version Check**: Checks if a working version exists (especially for CubeMain.txt)
2. **File Type Detection**: Analyzes filename and content to determine file type
3. **Encoding Detection**: Determines optimal encoding for the file
4. **Binding Application**: Automatically applies appropriate metadata binding if available
5. **User Confirmation**: Shows detection results and allows manual override
6. **File Loading**: Loads the file with detected settings

### Auto-Detection Process:
```
File Selected → Working Version Check → File Type Detection → Encoding Detection → Binding Lookup → User Confirmation → File Loading
```

## Usage Examples

### Automatic Detection:
- Open `CubeMain.txt` → Suggests `CubeMainWorking.txt` → Detects as "cubemain" type → Applies CubeMain binding
- Open `Armor.txt` → Detects as "armor" type → Applies armor binding with metadata
- Open `unknown.txt` → Content analysis → Detects as "generic_data" → Loads without binding

### Manual Override:
- Auto-detection suggests one binding → User selects "Choose Binding Manually" → Select from available bindings

## Benefits

1. **Reduced Errors**: Prevents opening incorrect file versions
2. **Better User Experience**: Automatic detection reduces manual configuration
3. **Metadata Integration**: Automatically applies column descriptions and help text
4. **Encoding Reliability**: Ensures files are opened with correct encoding
5. **Flexibility**: Allows manual override when needed

## Technical Implementation

- `detect_file_type()`: Analyzes filename and content patterns
- `auto_detect_encoding()`: Tests multiple encodings to find the best match
- `check_for_working_version()`: Checks for alternative file versions
- `AutoDetectionDialog`: Enhanced UI for showing detection results
- Integration with existing binding system for metadata support

## Testing

Run `test_auto_detection.py` to test the auto-detection functionality on all available files in the project. 