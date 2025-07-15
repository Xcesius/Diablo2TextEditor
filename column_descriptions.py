
LEVELS_COLUMNS = {
    "Name": "Defines the unique name pointer for the area level, which is used in other files.",
    "Id": "Defines the unique numeric ID for the area level, which is used in other files.",
    "Pal": "Defines which palette file to use for the area level. This uses index values from 0 to 4 to convey Act 1 to Act 5.",
    "Act": "Defines the Act number that the area level is a part of. This uses index values from 0 to 4 to convey Act 1 to Act 5.",
    "QuestFlag": "Controls what quest record that the player needs to have completed before being allowed to enter this area level, while playing in Classic Mode.",
    "QuestFlagEx": "Controls what quest record that the player needs to have completed before being allowed to enter this area level, while playing in Expansion Mode.",
    "Layer": "Defines a unique numeric ID that is used to identify which Automap data belongs to which area level when saving and loading data from the character save.",
    "SizeX": "Specifies the Length tile size values of an entire area level for Normal Difficulty.",
    "SizeX(N)": "Specifies the Length tile size values of an entire area level for Nightmare Difficulty.",
    "SizeX(H)": "Specifies the Length tile size values of an entire area level for Hell Difficulty.",
    "SizeY": "Specifies the Width tile size values of an entire area level for Normal Difficulty.",
    "SizeY(N)": "Specifies the Width tile size values of an entire area level for Nightmare Difficulty.",
    "SizeY(H)": "Specifies the Width tile size values of an entire area level for Hell Difficulty.",
    "OffsetX": "Specifies the location offset coordinates (measured in tile size) for the origin point of the area level in the world.",
    "OffsetY": "Specifies the location offset coordinates (measured in tile size) for the origin point of the area level in the world.",
    "Depend": "Assigns another level to be this area level’s depended level. Uses the level 'Id' field. If this equals 0, then ignore this.",
    "Teleport": "Controls the functionality of Teleport/Dragon Flight. 0: disabled, 1: enabled, 2: enabled but adheres to room collision.",
    "Rain": "Boolean. If 1, allows rain (or snow in Act 5).",
    "Mud": "Boolean. If 1, random bubbles animate on water tiles.",
    "NoPer": "Boolean. If 1, allows Perspective Mode. If 0, forces Orthographic Mode.",
    "LOSDraw": "Boolean. If 1, checks player's line of sight before drawing monsters.",
    "FloorFilter": "Boolean. If 1, draw floor tiles with a linear texture sampler. If 0, use nearest texture sampler.",
    "BlankScreen": "Boolean. If 1, draw the area level screen. If 0, the level will be a blank screen.",
    "DrawEdges": "Boolean. If 1, draw the areas in levels that are not covered by floor tiles.",
    "DrlgType": "Determines the type of Dynamic Random Level Generation. 0: None, 1: Maze, 2: Preset, 3: Outdoor.",
    "LevelType": "Defines the Level Type used for this area level. Uses the Level Type’s ID from LvlType.txt.",
    "SubType": "Controls the group of tile substitutions for the area level (see LvlSub.txt).",
    "SubTheme": "Controls which theme number to use in a Level Substitution (see LvlSub.txt). Values 0-4.",
    "SubWaypoint": "Controls the level substitutions for adding waypoints.",
    "SubShrine": "Controls the level substitutions for adding shrines.",
    "Vis0": "Visibility to other area level ID.",
    "Vis1": "Visibility to other area level ID.",
    "Vis2": "Visibility to other area level ID.",
    "Vis3": "Visibility to other area level ID.",
    "Vis4": "Visibility to other area level ID.",
    "Vis5": "Visibility to other area level ID.",
    "Vis6": "Visibility to other area level ID.",
    "Vis7": "Visibility to other area level ID.",
    "Warp0": "Uses ID from LevelWarp.txt for exiting the level, related to Vis0.",
    "Warp1": "Uses ID from LevelWarp.txt for exiting the level, related to Vis1.",
    "Warp2": "Uses ID from LevelWarp.txt for exiting the level, related to Vis2.",
    "Warp3": "Uses ID from LevelWarp.txt for exiting the level, related to Vis3.",
    "Warp4": "Uses ID from LevelWarp.txt for exiting the level, related to Vis4.",
    "Warp5": "Uses ID from LevelWarp.txt for exiting the level, related to Vis5.",
    "Warp6": "Uses ID from LevelWarp.txt for exiting the level, related to Vis6.",
    "Warp7": "Uses ID from LevelWarp.txt for exiting the level, related to Vis7.",
    "Intensity": "Controls the intensity value of the area level’s ambient colors (0-128).",
    "Red": "Controls the red value of the area level’s ambient colors (0-255).",
    "Green": "Controls the green value of the area level’s ambient colors (0-255).",
    "Blue": "Controls the blue value of the area level’s ambient colors (0-255).",
    "Portal": "Boolean. If 1, flags level as a portal level.",
    "Position": "Boolean. If 1, enables special casing for player positioning (e.g., spawning in town).",
    "SaveMonsters": "Boolean. If 1, the game will save the monsters in the area level.",
    "Quest": "Controls what quest record is attached to monsters that spawn in this area level.",
    "WarpDist": "Defines the minimum pixel distance from a Level Warp that a monster is allowed to spawn near.",
    "MonLvl": "Monster level for Normal Difficulty (Classic).",
    "MonLvl(N)": "Monster level for Nightmare Difficulty (Classic).",
    "MonLvl(H)": "Monster level for Hell Difficulty (Classic).",
    "MonLvlEx": "Monster level for Normal Difficulty (Expansion).",
    "MonLvlEx(N)": "Monster level for Nightmare Difficulty (Expansion).",
    "MonLvlEx(H)": "Monster level for Hell Difficulty (Expansion).",
    "MonDen": "Monster density (random value out of 100000) for Normal Difficulty.",
    "MonDen(N)": "Monster density for Nightmare Difficulty.",
    "MonDen(H)": "Monster density for Hell Difficulty.",
    "MonUMin": "Min number of Unique Monsters for Normal Difficulty.",
    "MonUMin(N)": "Min number of Unique Monsters for Nightmare Difficulty.",
    "MonUMin(H)": "Min number of Unique Monsters for Hell Difficulty.",
    "MonUMax": "Max number of Unique Monsters for Normal Difficulty.",
    "MonUMax(N)": "Max number of Unique Monsters for Nightmare Difficulty.",
    "MonUMax(H)": "Max number of Unique Monsters for Hell Difficulty.",
    "MonWndr": "Boolean. If 1, allow Wandering Monsters to spawn.",
    "MonSpcWalk": "Distance value for monster pathing AI near blockers.",
    "NumMon": "Controls the number of different monsters randomly spawning (max 13).",
    "mon1": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon2": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon3": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon4": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon5": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon6": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon7": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon8": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon9": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon10": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon11": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon12": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon13": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon14": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon15": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon16": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon17": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon18": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon19": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon20": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon21": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon22": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon23": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon24": "Monster ID from monstats.txt for Normal Difficulty.",
    "mon25": "Monster ID from monstats.txt for Normal Difficulty.",
    "rangedspawn": "Boolean. If 1, try to pick a ranged monster first.",
    "nmon1": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon2": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon3": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon4": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon5": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon6": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon7": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon8": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon9": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon10": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon11": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon12": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon13": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon14": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon15": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon16": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon17": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon18": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon19": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon20": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon21": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon22": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon23": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon24": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "nmon25": "Monster ID from monstats.txt for Nightmare/Hell Difficulty.",
    "umon1": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon2": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon3": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon4": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon5": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon6": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon7": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon8": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon9": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon10": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon11": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon12": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon13": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon14": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon15": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon16": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon17": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon18": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon19": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon20": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon21": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon22": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon23": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon24": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "umon25": "Unique monster ID from monstats.txt for Normal Difficulty.",
    "cmon1": "Critter monster ID from monstats.txt.",
    "cmon2": "Critter monster ID from monstats.txt.",
    "cmon3": "Critter monster ID from monstats.txt.",
    "cmon4": "Critter monster ID from monstats.txt.",
    "cpct1": "Percent chance (out of 100) to spawn Critter monster 1.",
    "cpct2": "Percent chance (out of 100) to spawn Critter monster 2.",
    "cpct3": "Percent chance (out of 100) to spawn Critter monster 3.",
    "cpct4": "Percent chance (out of 100) to spawn Critter monster 4.",
    "camt1": "Amount of Critter monster 1 to spawn.",
    "camt2": "Amount of Critter monster 2 to spawn.",
    "camt3": "Amount of Critter monster 3 to spawn.",
    "camt4": "Amount of Critter monster 4 to spawn.",
    "Themes": "Bitmask for which themes to use when building a level room.",
    "SoundEnv": "Uses Index from SoundEnviron.txt to control music.",
    "Waypoint": "Unique numeric ID for the Waypoint. Ignore if >= 255.",
    "LevelName": "String. Name of the area level for Automap UI.",
    "LevelWarp": "String. Entrance name displayed on Level Warp tiles.",
    "LevelEntry": "String. UI popup title string when entering the area.",
    "ObjGrp0": "Numeric ID for Object Group to spawn (see objgroup.txt).",
    "ObjGrp1": "Numeric ID for Object Group to spawn.",
    "ObjGrp2": "Numeric ID for Object Group to spawn.",
    "ObjGrp3": "Numeric ID for Object Group to spawn.",
    "ObjGrp4": "Numeric ID for Object Group to spawn.",
    "ObjGrp5": "Numeric ID for Object Group to spawn.",
    "ObjGrp6": "Numeric ID for Object Group to spawn.",
    "ObjGrp7": "Numeric ID for Object Group to spawn.",
    "ObjPrb0": "Random chance (out of 100) for ObjGrp0 to spawn.",
    "ObjPrb1": "Random chance (out of 100) for ObjGrp1 to spawn.",
    "ObjPrb2": "Random chance (out of 100) for ObjGrp2 to spawn.",
    "ObjPrb3": "Random chance (out of 100) for ObjGrp3 to spawn.",
    "ObjPrb4": "Random chance (out of 100) for ObjGrp4 to spawn.",
    "ObjPrb5": "Random chance (out of 100) for ObjGrp5 to spawn.",
    "ObjPrb6": "Random chance (out of 100) for ObjGrp6 to spawn.",
    "ObjPrb7": "Random chance (out of 100) for ObjGrp7 to spawn.",
    "LevelGroup": "Defines what group this level belongs to for terror zones messaging."
} 

# --- Modular specification loader for all Diablo II .txt files ---
import json
import os
from functools import lru_cache

# Directory that will contain per-file JSON specs, e.g. specs/Levels.json, specs/Skills.json, etc.
_SPECS_DIR = os.path.join(os.path.dirname(__file__), "specs")

# Ensure the directory exists (no-op if already present)
os.makedirs(_SPECS_DIR, exist_ok=True)

@lru_cache(maxsize=None)
def _load_spec(file_key: str) -> dict:
    """Load column descriptions for the given txt/ tbl file from JSON spec.

    Parameters
    ----------
    file_key : str
        The base name of the data file without extension (e.g. "Levels" for Levels.txt).

    Returns
    -------
    dict
        Mapping of column name -> description strings. Empty dict if no spec found.
    """
    spec_path = os.path.join(_SPECS_DIR, f"{file_key}.json")
    if not os.path.exists(spec_path):
        return {}

    try:
        with open(spec_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        # Fail safe – log and return empty mapping
        print(f"[WARN] Failed to load column spec for {file_key}: {exc}")
        return {}


def get_description(txt_file_path: str, column_name: str) -> str:
    """Retrieve the description for *column_name* belonging to the supplied Diablo II data file.

    The lookup order is:
    1. JSON spec found under specs/<FileKey>.json
    2. Hard-coded fallback such as LEVELS_COLUMNS (currently only for Levels.txt)
    3. Generic placeholder string.
    """
    if not column_name:
        return "No description available for this column."

    # Derive key from filename (strip extension). If path is missing, default to empty string.
    file_key = os.path.splitext(os.path.basename(txt_file_path or ""))[0]
    json_spec = _load_spec(file_key)

    if column_name in json_spec:
        return json_spec[column_name]

    # Fallbacks for built-in hard-coded dictionaries
    if file_key.lower() == "levels" and column_name in LEVELS_COLUMNS:
        return LEVELS_COLUMNS[column_name]

    # Unknown
    return "No description available for this column." 