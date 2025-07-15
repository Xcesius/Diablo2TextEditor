# Diablo II Text Editor – Feature Roadmap

This document captures **potential enhancements** for our Python/PyQt Diablo II text-editing tool, gleaned from the historical feature lists of AFJ tbl Edit and AFJ Sheet Edit. It is a living roadmap – re-prioritise or prune items as needed.

---

## 1. Quality-of-Life Editing Features (High Value, Low Complexity)
- [x] **Search / Search & Replace** across sheet cells and within a column. ✅ *Complete with Find Next, Replace, Replace All, case-sensitive option*
- [x] **Keyboard Shortcuts / Accelerators** mirroring Excel-style workflows (e.g. `Ctrl+O` open, `Ctrl+S` save, `Ctrl+Z` undo, `Ctrl+Y` redo, `Ctrl+F` find). ✅ *All essential shortcuts implemented*
- [x] **Right-click Context Menu** with basic operations: copy, cut, paste, delete, insert row/column. ✅ *Complete with clipboard operations, row/column management, and keyboard shortcuts*
- [ ] **Double-click to Edit / Enter to Commit** behaviour to reduce flicker and mis-clicks.
- [ ] **Multi-row / Multi-column Add, Insert, Delete** with optional fixed first row/column.
- [ ] **Multiselect / Multiedit** – select blocks of cells and perform bulk operations (e.g. copy, paste, increment/decrement).

## 2. Colour-Coding & Visual Aids
- [ ] **Colour Code Shortcuts** (`\red;`, `\gold;`, etc.) with in-cell preview and quick-insert menu.
- [ ]  Option to hide/show grid lines, header rows (A-Z, 1-N), and fixed columns.
- [ ] **Customisable Fonts** per view; store default in settings/registry-equivalent.
- [x] **Column Header Help**: Displays detailed description for each column when header is clicked.

## 3. Advanced Cell Operations
- [ ] **Math Menu** for common operations: `Round`, `Trunc`, `Apply Function …`.
- [ ] **Expression Parser**: evaluate `=sin($c)+3` style formulas, including SFL/UFL support.
- [ ] **Apply-to-Selection Functions** with variables `$c`, `$x`, `$y` and helpers like `cell(y:x)`.

## 4. File Handling & Safety
- [x] **Automatic Backups** - Timestamped `.bak` files created before each save ✅ *`Levels_20241220_143052.bak` format, keeps 5 most recent*
- [x] **Undo / Redo Stack** (10 levels) for cell edits & deletions ✅ *Tracks all changes, Ctrl+Z/Ctrl+Y shortcuts*
- [ ] **One-Instance-Only** option (toggle to prevent multiple editor windows).
- [ ] **Drag-and-Drop** and shell integration for opening files.
- [ ] **Extended Undo/Redo History** – configurable depth (option for unlimited), with smart grouping of actions.
- [ ] **Built-in Error Validator** – duplicate code checks, numeric bounds, inter-file linkage validation; rules configurable as warn / ignore / error.

## 5. Import / Export Enhancements
- [ ] **Tabbed .txt Import/Export** with Unicode support.
- [ ] **TXT ↔ TOML/JSON Converter** for cleaner diffs and git-friendly version control.
- [ ] **Bulk Import** options: overwrite existing entries, skip empty rows/cols.
- [ ] **String Table (.tbl) Support**: load, edit, and save Patchstring.tbl, Expansionstring.tbl.

## 6. Power-User Tools
- [ ] **Index Inspector**: show string index in each .tbl file (AFJ style window).
- [ ] **Hex Index Counter** in status bar for quick reference.
- [ ] **Sheet Tabs**: allow multiple open sheets, quick switching (`Ctrl+Tab`).
- [ ] **Timed CRC / Validity Check** similar to Enquettar script.
- [ ] **HTML Documentation Generator** – one-click export of Cube recipes, Runewords, Sets, Uniques, etc.
- [ ] **Bulk Utilities Suite**: item-code lookup, item GFX lookup, JSON template builder for Sets/Uniques.
- [ ] **Scripting / API Hooks** for programmatic batch edits (Python/Lua).

## 7. Nice-to-Have / Stretch Goals
- [ ] **Print / Print Preview** of current sheet.
- [ ] **Multi-language UI** with full UNICODE support (tested with Chinese fonts).
- [ ] **Custom Function Library Editor** for SFL/UFL – create & edit functions graphically.
- [ ] **Cell Commenting / Notes** (Excel-style sticky notes).

---

---

## 🎉 **Progress Update - Phase 1 Complete!**

### ✅ **COMPLETED: Core Safety & Productivity Features**
- **Undo/Redo System**: 10-level stack with smart change tracking
- **Automatic Backups**: Timestamped files with automatic cleanup
- **Search & Replace**: Full dialog with case-sensitive options
- **Professional Shortcuts**: Standard Ctrl+S, Ctrl+Z, Ctrl+F, etc.
- **Right-click Context Menu**: Complete with clipboard operations, row/column management, and keyboard shortcuts
- **Column Header Help**: Provides detailed descriptions for columns via header clicks
- **Error Handling**: User-friendly save warnings and backup notifications

### **Current Status:** The editor now provides **enterprise-level data safety** while maintaining **perfect Diablo II format compatibility**. All high-priority items from Phase 1 are complete.

---

### Prioritisation Strategy
1. ✅ **Stability & Safety** – backup, undo, crash fixes. **COMPLETE**
2. ✅ **Editing Experience** – search/replace ✅, shortcuts ✅, context menu ✅. **COMPLETE**
3. **Advanced Parsing & Colour Codes** – expression engine, colour helper.
4. **Import/Export & Integration** – .tbl support, drag-and-drop.

Feel free to strike through, reorder, or expand on items as the project evolves. 