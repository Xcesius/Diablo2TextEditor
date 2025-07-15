import re
import json
import os

def load_full_text():
    """Load the complete extracted text from the text file."""
    text_file = "D2R_DataGuide_2.7_full_text.txt"
    
    if not os.path.exists(text_file):
        print(f"Error: Text file not found: {text_file}")
        print("Please run 'python extract_full_text.py' first to extract the complete text.")
        return None
    
    with open(text_file, 'r', encoding='utf-8') as f:
        return f.read()

# List of all files from the Table of Contents to guide the parsing
TOC_FILES = [
    "actinfo.txt", "armor.txt", "automagic.txt", "AutoMap.txt", "belts.txt",
    "books.txt", "charstats.txt", "cubemain.txt", "difficultylevels.txt",
    "experience.txt", "gamble.txt", "gems.txt", "hireling.txt",
    "hirelingdesc.txt", "inventory.txt", "itemratio.txt", "ItemStatCost.txt", "ItemTypes.txt",
    "LevelGroups.txt", "Levels.txt", "LvlMaze.txt", "LvlPrest.txt",
    "LvlSub.txt", "LvlTypes.txt", "LvlWarp.txt", "MagicPrefix.txt",
    "MagicSuffix.txt", "Missiles.txt", "misc.txt", "monequip.txt",
    "MonLvl.txt", "MonPreset.txt", "MonProp.txt", "monseq.txt",
    "monstats.txt", "monstats2.txt", "MonType.txt", "monumod.txt",
    "monsounds.txt", "npc.txt", "objects.txt", "objgroup.txt",
    "objpreset.txt", "Overlay.txt", "pettype.txt", "Properties.txt",
    "QualityItems.txt", "RarePrefix.txt", "RareSuffix.txt", "Runes.txt",
    "SetItems.txt", "Sets.txt", "shrines.txt", "skills.txt", "skilldesc.txt",
    "sounds.txt", "SoundEnviron.txt", "states.txt", "SuperUniques.txt",
    "TreasureClassEx.txt", "UniqueAppellation.txt", "UniqueItems.txt",
    "UniqueTitle.txt", "UniqueSuffix.txt", "weapons.txt", "wanderingmon.txt"
]

def get_indent(line: str) -> int:
    """Calculates the indentation of a line."""
    return len(line) - len(line.lstrip(' '))

def split_into_file_sections(text: str, toc_files: list) -> dict:
    """Splits the document text into a dictionary of sections, one for each file."""
    # Clean up page markers
    text = re.sub(r'==(Start|End) of OCR for page \d+==\n?', '', text)

    starts = []
    for fname in toc_files:
        # Find all occurrences of the filename on a line by itself.
        # This pattern is based on the OCR'd file headers.
        for match in re.finditer(f'^{re.escape(fname)}$', text, re.MULTILINE):
            starts.append({'filename': fname, 'start': match.start()})

    starts.sort(key=lambda x: x['start'])

    sections = {}
    for i, current in enumerate(starts):
        filename = current['filename']
        start_pos = current['start']

        content_start = text.find('\n', start_pos) + 1
        end_pos = starts[i + 1]['start'] if i + 1 < len(starts) else len(text)

        section_text = text[content_start:end_pos]
        sections[filename] = section_text.strip()

    return sections

def parse_table(lines: list) -> (list | None, int):
    """Parses a simple, column-based table from a list of lines."""
    if not lines or not lines[0].strip():
        return None, 0

    header_line = lines[0].strip()
    # Headers are often separated by two or more spaces
    headers = [h.strip() for h in re.split(r'\s{2,}', header_line)]

    # Heuristic to avoid misidentifying normal text as a table header
    if len(headers) < 2 or len(headers) > 6:
        return None, 0
    if not all(h for h in headers): # Ensure no empty headers
        return None, 0

    col_starts = [header_line.find(h) for h in headers]

    table = []
    lines_consumed = 1
    for line in lines[1:]:
        lines_consumed += 1
        # Stop table parsing on an empty line or a new, un-indented field definition
        if not line.strip() or (get_indent(line) == 0 and ' - ' in line):
            break

        row_dict = {}
        for j, header in enumerate(headers):
            start = col_starts[j]
            end = col_starts[j + 1] if j + 1 < len(col_starts) else len(line)
            value = line[start:end].strip()
            row_dict[header] = value

        if any(row_dict.values()):
            table.append(row_dict)

    if not table:
        return None, 0

    return table, lines_consumed

def parse_data_fields(lines: list) -> list:
    """Parses the Data Fields section into a list of field objects."""
    fields = []
    field_regex = re.compile(r'^(?P<name>[\w\s\(\)\[\]&.,#\d\-\>]+?)\s*-\s*(?P<desc>.*)')

    field_starts = []
    for i, line in enumerate(lines):
        # A new field starts at indentation 0 and matches the "name - description" pattern
        if get_indent(line) == 0 and field_regex.match(line.strip()):
            field_starts.append(i)

    for i, start_idx in enumerate(field_starts):
        end_idx = field_starts[i + 1] if i + 1 < len(field_starts) else len(lines)
        field_lines = [line.strip() for line in lines[start_idx:end_idx]]

        # The first line is the main definition
        match = field_regex.match(field_lines[0])
        if not match: continue

        name = match.group('name').strip()
        desc_start = match.group('desc').strip()

        field_data = {'name': name}
        description_parts = [desc_start]
        
        # Process the rest of the lines for this field block
        j = 1
        while j < len(field_lines):
            line = field_lines[j]
            # Try to parse a table starting from the current line
            table_data, consumed = parse_table(field_lines[j:])
            if table_data:
                field_data['table'] = table_data
                j += consumed
            else:
                description_parts.append(line)
                j += 1
        
        field_data['description'] = ' '.join(p for p in description_parts if p).strip()
        fields.append(field_data)

    return fields

def parse_section(section_text: str) -> dict:
    """Parses the text of a single file section."""
    data = {}
    lines = section_text.split('\n')
    
    overview_lines = []
    data_fields_lines = []
    
    current_subsection = None
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == 'Overview':
            current_subsection = 'overview'
            continue
        elif stripped_line == 'Data Fields':
            current_subsection = 'data_fields'
            continue
        elif stripped_line in ['Calculations', 'Reference Data Files']: # Other subsections to ignore for now
            current_subsection = None
            continue

        if current_subsection == 'overview':
            overview_lines.append(stripped_line)
        elif current_subsection == 'data_fields':
            # Pass raw lines with indentation to preserve table structure
            data_fields_lines.append(line)

    data['overview'] = ' '.join(overview_lines).strip()
    data['data_fields'] = parse_data_fields(data_fields_lines)
    
    return data

def main():
    """Main function to parse the document and write JSON files."""
    print("Parsing Diablo II Data File Guide...")
    
    full_text = load_full_text()
    
    if full_text is None:
        return

    file_sections = split_into_file_sections(full_text, TOC_FILES)
    
    if not file_sections:
        print("Could not find any file sections. Please check the input text and TOC_FILES list.")
        return

    output_dir = "specs"
    os.makedirs(output_dir, exist_ok=True)
    
    parsed_count = 0
    for filename, text in file_sections.items():
        print(f"  - Parsing {filename}...")
        try:
            parsed_data = parse_section(text)
            parsed_data['filename'] = filename
            
            # Write to JSON
            json_filename = filename.replace('.txt', '.json')
            output_path = os.path.join(output_dir, json_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            parsed_count += 1
        except Exception as e:
            print(f"    [ERROR] Could not parse {filename}: {e}")

    print(f"\nParsing complete. {parsed_count} files were generated in the '{output_dir}' directory.")

if __name__ == '__main__':
    main()