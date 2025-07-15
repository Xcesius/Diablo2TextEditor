# Diablo II Data File Column Specifications

Place one JSON file per data sheet (e.g. `Levels.json`, `Skills.json`, `MonStats.json`) in this directory.

Each file must contain a simple mapping of column **name** → **description** so the editor can display contextual help when a user clicks on a column header.

Example `Levels.json` snippet:
```json
{
  "Name": "Defines the unique name pointer for the area level, which is used in other files.",
  "Id": "Defines the unique numeric ID for the area level, which is used in other files."
}
```

The editor automatically looks up `Levels.json` when `Levels.txt` is opened (case–insensitive, extension is ignored). If no JSON file exists the editor falls back to any hard-coded descriptions present in `column_descriptions.py`.

You can generate these JSON specs automatically by parsing the *Diablo II Resurrected Data Guide* PDF or by exporting from your own documentation sources. 