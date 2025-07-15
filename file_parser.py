import pandas as pd
import csv
import os
import json
from pathlib import Path

# Global variable to cache the fingerprint database
_fingerprint_db = None

def load_fingerprint_database():
    """Load the fingerprint database for column-based detection."""
    global _fingerprint_db
    
    if _fingerprint_db is None:
        fingerprint_file = "file_type_fingerprints.json"
        if os.path.exists(fingerprint_file):
            try:
                with open(fingerprint_file, 'r', encoding='utf-8') as f:
                    _fingerprint_db = json.load(f)
                print(f"Loaded fingerprint database with {len(_fingerprint_db)} file types")
            except Exception as e:
                print(f"Error loading fingerprint database: {e}")
                _fingerprint_db = {}
        else:
            print(f"Fingerprint database not found at {fingerprint_file}")
            _fingerprint_db = {}
    
    return _fingerprint_db

def detect_by_column_fingerprint(file_path):
    """
    Detect file type by analyzing column patterns against the fingerprint database.
    Returns tuple: (file_type, confidence, binding_key)
    """
    fingerprint_db = load_fingerprint_database()
    
    if not fingerprint_db:
        return ('unknown', 'none', None)
    
    try:
        # Read the first line to get column headers
        with open(file_path, 'r', encoding='windows-1252') as f:
            first_line = f.readline().strip()
        
        if not first_line:
            return ('unknown', 'none', None)
        
        # Extract column names (convert to lowercase for comparison)
        file_columns = set(col.lower().strip() for col in first_line.split('\t') if col.strip())
        
        if not file_columns:
            return ('unknown', 'none', None)
        
        print(f"Analyzing file columns: {len(file_columns)} columns found")
        
        # Try to match against fingerprint database
        best_match = None
        best_score = 0
        best_confidence = 'none'
        
        for file_key, fingerprint in fingerprint_db.items():
            score = 0
            confidence = 'none'
            
            # Check for unique column matches (highest priority)
            unique_columns = set(col.lower() for col in fingerprint.get('unique_columns', []))
            unique_matches = file_columns.intersection(unique_columns)
            
            if unique_matches:
                score += len(unique_matches) * 10  # High weight for unique columns
                confidence = 'high'
                print(f"  Found unique columns for {file_key}: {unique_matches}")
            
            # Check for distinctive combination matches (medium priority)
            distinctive_combinations = fingerprint.get('distinctive_combinations', [])
            for combination in distinctive_combinations:
                combo_set = set(col.lower() for col in combination)
                if combo_set.issubset(file_columns):
                    score += len(combo_set) * 5  # Medium weight for combinations
                    if confidence == 'none':
                        confidence = 'medium'
                    print(f"  Found distinctive combination for {file_key}: {combo_set}")
            
            # Check overall column overlap (low priority)
            all_columns = set(col.lower() for col in fingerprint.get('all_columns', []))
            overlap = file_columns.intersection(all_columns)
            if len(all_columns) > 0:
                overlap_ratio = len(overlap) / len(all_columns)
                if overlap_ratio > 0.5:  # At least 50% column overlap
                    score += overlap_ratio * 2  # Low weight for general overlap
                    if confidence == 'none' and overlap_ratio > 0.8:
                        confidence = 'low'
            
            # Track the best match
            if score > best_score:
                best_score = score
                best_match = file_key
                best_confidence = confidence
        
        if best_match and best_score > 0:
            print(f"Best column-based match: {best_match} (score: {best_score}, confidence: {best_confidence})")
            return (best_match, best_confidence, best_match)
        
    except Exception as e:
        print(f"Error in column fingerprint detection: {e}")
    
    return ('unknown', 'none', None)

def detect_file_type(file_path):
    """
    Auto-detect the type of Diablo 2 data file and return binding information.
    Returns tuple: (file_type, confidence, binding_key)
    
    Now enhanced with column-based fingerprint detection.
    """
    file_name = Path(file_path).name.lower()
    base_name = Path(file_path).stem.lower()
    
    # Known Diablo 2 files mapping (existing filename-based detection)
    known_files = {
        'cubemain.txt': ('cubemain', 'high', 'CubeMain'),
        'cubemainworking.txt': ('cubemain', 'high', 'CubeMain'),
        'armor.txt': ('armor', 'high', 'armor'),
        'weapons.txt': ('weapons', 'high', 'weapons'),
        'misc.txt': ('misc', 'high', 'misc'),
        'itemstatcost.txt': ('itemstatcost', 'high', 'ItemStatCost'),
        'itemtypes.txt': ('itemtypes', 'high', 'ItemTypes'),
        'charstats.txt': ('charstats', 'high', 'charstats'),
        'skills.txt': ('skills', 'high', 'skills'),
        'levels.txt': ('levels', 'high', 'Levels'),
        'monstats.txt': ('monstats', 'high', 'monstats'),
        'treasureclassex.txt': ('treasureclassex', 'high', 'TreasureClassEx'),
        'uniqueitems.txt': ('uniqueitems', 'high', 'UniqueItems'),
        'setitems.txt': ('setitems', 'high', 'SetItems'),
        'magicprefix.txt': ('magicprefix', 'high', 'MagicPrefix'),
        'magicsuffix.txt': ('magicsuffix', 'high', 'MagicSuffix'),
        'automagic.txt': ('automagic', 'high', 'AutoMagic'),
        'runes.txt': ('runes', 'high', 'Runes'),
        'experience.txt': ('experience', 'high', 'experience'),
        'gamble.txt': ('gamble', 'high', 'Gamble'),
        'hireling.txt': ('hireling', 'high', 'Hireling'),
        'missiles.txt': ('missiles', 'high', 'Missiles'),
        'properties.txt': ('properties', 'high', 'Properties'),
        'skilldesc.txt': ('skilldesc', 'high', 'Skilldesc'),
        'states.txt': ('states', 'high', 'states'),
        'monprop.txt': ('monprop', 'high', 'MonProp'),
        'monlvl.txt': ('monlvl', 'high', 'MonLvl'),
        'monstats2.txt': ('monstats2', 'high', 'MonStats2'),
        'montype.txt': ('montype', 'high', 'MonType'),
        'monumod.txt': ('monumod', 'high', 'MonUMod'),
        'pettype.txt': ('pettype', 'high', 'PetType'),
        'sets.txt': ('sets', 'high', 'Sets'),
        'difficultylevels.txt': ('difficultylevels', 'high', 'DifficultyLevels'),
        'itemratio.txt': ('itemratio', 'high', 'ItemRatio'),
        'skillcalc.txt': ('skillcalc', 'high', 'SkillCalc'),
        'monai.txt': ('monai', 'high', 'MonAi'),
        # Additional files from warnings (even if no .txt equivalents exist)
        'actinfo.txt': ('actinfo', 'high', 'actinfo'),
        'automap.txt': ('automap', 'high', 'AutoMap'),
        'belts.txt': ('belts', 'high', 'belts'),
        'books.txt': ('books', 'high', 'books'),
        'gems.txt': ('gems', 'high', 'gems'),
        'hirelingdesc.txt': ('hirelingdesc', 'high', 'hirelingdesc'),
        'inventory.txt': ('inventory', 'high', 'inventory'),
        'levelgroups.txt': ('levelgroups', 'high', 'LevelGroups'),
        'lvlmaze.txt': ('lvlmaze', 'high', 'LvlMaze'),
        'lvlprest.txt': ('lvlprest', 'high', 'LvlPrest'),
        'lvlsub.txt': ('lvlsub', 'high', 'LvlSub'),
        'lvltypes.txt': ('lvltypes', 'high', 'LvlTypes'),
        'lvlwarp.txt': ('lvlwarp', 'high', 'LvlWarp'),
        'monequip.txt': ('monequip', 'high', 'monequip'),
        'monpreset.txt': ('monpreset', 'high', 'MonPreset'),
        'monseq.txt': ('monseq', 'high', 'monseq'),
        'monsounds.txt': ('monsounds', 'high', 'monsounds'),
        'npc.txt': ('npc', 'high', 'npc'),
        'objects.txt': ('objects', 'high', 'objects'),
        'objgroup.txt': ('objgroup', 'high', 'objgroup'),
        'objpreset.txt': ('objpreset', 'high', 'objpreset'),
        'overlay.txt': ('overlay', 'high', 'Overlay'),
        'qualityitems.txt': ('qualityitems', 'high', 'QualityItems'),
        'rareprefix.txt': ('rareprefix', 'high', 'RarePrefix'),
        'raresuffix.txt': ('raresuffix', 'high', 'RareSuffix'),
        'shrines.txt': ('shrines', 'high', 'shrines'),
        'soundenviron.txt': ('soundenviron', 'high', 'SoundEnviron'),
        'sounds.txt': ('sounds', 'high', 'sounds'),
        'superuniques.txt': ('superuniques', 'high', 'SuperUniques'),
        'uniqueappellation.txt': ('uniqueappellation', 'high', 'UniqueAppellation'),
        'uniquesuffix.txt': ('uniquesuffix', 'high', 'UniqueSuffix'),
        'uniquetitle.txt': ('uniquetitle', 'high', 'UniqueTitle'),
        'wanderingmon.txt': ('wanderingmon', 'high', 'wanderingmon'),
    }
    
    # Check for exact match first
    if file_name in known_files:
        return known_files[file_name]
    
    # Check for partial matches (without .txt extension)
    for known_file, info in known_files.items():
        if base_name == known_file.replace('.txt', ''):
            return (info[0], 'medium', info[2])
    
    print(f"Filename detection failed for {file_name}, trying column-based detection...")
    
    # Try column-based fingerprint detection
    column_result = detect_by_column_fingerprint(file_path)
    if column_result[1] != 'none':  # If we found a match
        print(f"Column-based detection successful: {column_result}")
        return column_result
    
    # Try to detect by content analysis (fallback to original content detection)
    try:
        # Read first few lines to detect common Diablo 2 patterns
        with open(file_path, 'r', encoding='windows-1252') as f:
            first_lines = [f.readline().strip() for _ in range(3)]
        
        # Check for common Diablo 2 column patterns
        if first_lines and any(line for line in first_lines if line):
            header = first_lines[0].split('\t')
            
            # Common Diablo 2 patterns
            common_patterns = {
                'index': 'generic_data',
                'name': 'generic_data',
                'code': 'item_data',
                'type': 'item_data',
                'level': 'character_data',
                'stat': 'stat_data',
                'treasure class': 'treasure_data',
                'class': 'character_data',
                'input': 'recipe_data',
                'output': 'recipe_data',
            }
            
            for col in header:
                col_lower = col.lower()
                for pattern, file_type in common_patterns.items():
                    if pattern in col_lower:
                        return (file_type, 'low', None)
    
    except Exception:
        pass
    
    return ('unknown', 'none', None)

def auto_detect_encoding(file_path):
    """
    Auto-detect the best encoding for a file.
    Returns the encoding that works best.
    """
    encodings = ['windows-1252', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Try to read a substantial portion
                content = f.read(1024)
                if content:  # If we can read content successfully
                    return encoding
        except UnicodeDecodeError:
            continue
        except Exception:
            continue
    
    return 'windows-1252'  # Default fallback

def open_txt_file(file_path):
    """
    Opens a tab-delimited .txt file and returns a pandas DataFrame.
    Tries multiple encodings to handle various file formats.
    """
    # List of encodings to try in order (Windows-1252 first for Diablo II files)
    encodings = ['windows-1252', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    try:
        for encoding in encodings:
            try:
                # Diablo II txt files are tab-separated with specific encoding
                # Use quoting=csv.QUOTE_NONE to preserve original quotes in the data
                import csv
                df = pd.read_csv(file_path, sep='\t', encoding=encoding, keep_default_na=False, quoting=csv.QUOTE_NONE)
                if encoding != 'windows-1252':
                    print(f"Successfully loaded file using {encoding} encoding")
                return df
            except UnicodeDecodeError:
                # Try next encoding
                continue
            except Exception as e:
                # For non-encoding errors, break and handle below
                raise e
        
        # If all encodings failed
        print(f"Error: Could not decode file {file_path} with any supported encoding")
        print(f"Tried encodings: {', '.join(encodings)}")
        return None
        
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_txt_file(df, file_path):
    """
    Saves a pandas DataFrame to a tab-delimited .txt file with exact formatting.
    """
    try:
        def format_value(value, column_name, row=None):
            """Format a single value - now just returns the raw value since quotes are preserved during loading."""
            # Handle empty/null values
            if pd.isna(value) or value == '':
                return ''
            
            # Return the raw string value as-is
            return str(value)
        
        # Manually build the file content
        lines = []
        
        # Add header row
        header_line = '\t'.join(df.columns)
        lines.append(header_line)
        
        # Add data rows
        for _, row in df.iterrows():
            formatted_values = []
            for col_name, value in row.items():
                formatted_values.append(format_value(value, col_name, row))
            line = '\t'.join(formatted_values)
            lines.append(line)
        
        # Write to file with Windows-style line endings to match CubeMainWorking.txt
        with open(file_path, 'w', encoding='windows-1252', newline='') as f:
            for line in lines:
                f.write(line + '\r\n')
        
        print(f"File saved successfully to {file_path}")
        return True
    except Exception as e:
        print(f"An error occurred while saving: {e}")
        return False 

def check_for_working_version(file_path):
    """
    Check if there's a working version of the file that should be used instead.
    Returns tuple: (should_use_alternative, alternative_path, message)
    """
    base_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path).lower()
    
    # Check for other common working version patterns
    working_patterns = [
        ('working', 'Working version found'),
        ('fixed', 'Fixed version found'),
        ('correct', 'Correct version found'),
        ('good', 'Good version found')
    ]
    
    base_name = os.path.splitext(file_name)[0]
    for pattern, message in working_patterns:
        working_file = f"{base_name}{pattern}.txt"
        working_path = os.path.join(base_dir, working_file)
        if os.path.exists(working_path):
            return (True, working_path, f"{message}: {working_file}")
    
    return (False, None, None) 