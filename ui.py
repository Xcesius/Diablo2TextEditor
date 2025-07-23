from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenuBar, QFileDialog, QAbstractItemView, QMessageBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QGridLayout, QListWidget, QListWidgetItem, QTextEdit, QSplitter, QComboBox, QStyledItemDelegate, QInputDialog
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QKeySequence
from PyQt6.QtCore import Qt, QItemSelection
from file_parser import open_txt_file, detect_file_type, auto_detect_encoding, save_txt_file, check_for_working_version
import pandas as pd
from custom_widgets import CleanTableView
from column_descriptions import get_description
from file_bindings import get_binding_manager, DataFileBinding
import copy
import os
import shutil
from datetime import datetime
import json

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.items = items or []

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        editor.setEditable(True)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setCurrentText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class UndoCommand:
    """Represents a single undoable action"""
    def __init__(self, row, col, old_value, new_value):
        self.row = row
        self.col = col
        self.old_value = old_value
        self.new_value = new_value

class UndoStack:
    """Manages undo/redo operations with a maximum stack size"""
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.undo_stack = []
        self.redo_stack = []
    
    def push(self, command):
        """Add a new command to the undo stack"""
        self.undo_stack.append(command)
        self.redo_stack.clear()
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
    
    def can_undo(self):
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        return len(self.redo_stack) > 0
    
    def undo(self):
        """Return the last command for undoing"""
        if self.can_undo():
            command = self.undo_stack.pop()
            self.redo_stack.append(command)
            return command
        return None
    
    def redo(self):
        """Return the last undone command for redoing"""
        if self.can_redo():
            command = self.redo_stack.pop()
            self.undo_stack.append(command)
            return command
        return None
    
    def clear(self):
        """Clear both stacks"""
        self.undo_stack.clear()
        self.redo_stack.clear()

class SearchReplaceDialog(QDialog):
    """Dialog for search and replace functionality"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search and Replace")
        self.setModal(True)
        self.resize(400, 150)
        
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Search for:"), 0, 0)
        self.search_input = QLineEdit()
        layout.addWidget(self.search_input, 0, 1)
        
        layout.addWidget(QLabel("Replace with:"), 1, 0)
        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_input, 1, 1)
        
        self.case_sensitive = QCheckBox("Case sensitive")
        layout.addWidget(self.case_sensitive, 2, 0, 1, 2)
        
        button_layout = QHBoxLayout()
        
        self.find_next_btn = QPushButton("Find Next")
        self.find_next_btn.clicked.connect(self.find_next)
        button_layout.addWidget(self.find_next_btn)
        
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.clicked.connect(self.replace_current)
        button_layout.addWidget(self.replace_btn)
        
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.clicked.connect(self.replace_all)
        button_layout.addWidget(self.replace_all_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        self.parent_editor = parent
        self.current_row = 0
        self.current_col = 0
        self.found_positions = []
        self.current_find_index = -1
        
    def find_next(self):
        """Find the next occurrence of the search term"""
        search_term = self.search_input.text()
        if not search_term:
            return
            
        case_sensitive = self.case_sensitive.isChecked()
        model = self.parent_editor.tableView.model()
        
        if not model:
            return
            
        start_row = self.current_row
        start_col = self.current_col
        
        found = False
        for row in range(start_row, model.rowCount()):
            start_column = start_col if row == start_row else 0
            for col in range(start_column, model.columnCount()):
                item = model.item(row, col)
                if item:
                    cell_text = item.text()
                    if not case_sensitive:
                        cell_text = cell_text.lower()
                        search_term_check = search_term.lower()
                    else:
                        search_term_check = search_term
                        
                    if search_term_check in cell_text:
                        self.current_row = row
                        self.current_col = col
                        index = model.index(row, col)
                        self.parent_editor.tableView.setCurrentIndex(index)
                        self.parent_editor.tableView.scrollTo(index)
                        self.current_col += 1
                        if self.current_col >= model.columnCount():
                            self.current_col = 0
                            self.current_row += 1
                        found = True
                        return
        
        if start_row > 0 or start_col > 0:
            self.current_row = 0
            self.current_col = 0
            self.find_next()
        else:
            QMessageBox.information(self, "Search", f"'{search_term}' not found.")
    
    def replace_current(self):
        """Replace the currently selected cell if it contains the search term"""
        search_term = self.search_input.text()
        replace_term = self.replace_input.text()
        
        if not search_term:
            return
            
        model = self.parent_editor.tableView.model()
        current_index = self.parent_editor.tableView.currentIndex()
        
        if current_index.isValid():
            item = model.item(current_index.row(), current_index.column())
            if item:
                cell_text = item.text()
                case_sensitive = self.case_sensitive.isChecked()
                
                if not case_sensitive:
                    if search_term.lower() in cell_text.lower():
                        import re
                        new_text = re.sub(re.escape(search_term), replace_term, cell_text, flags=re.IGNORECASE)
                        item.setText(new_text)
                else:
                    if search_term in cell_text:
                        new_text = cell_text.replace(search_term, replace_term)
                        item.setText(new_text)
    
    def replace_all(self):
        """Replace all occurrences of the search term"""
        search_term = self.search_input.text()
        replace_term = self.replace_input.text()
        
        if not search_term:
            return
            
        model = self.parent_editor.tableView.model()
        if not model:
            return
            
        case_sensitive = self.case_sensitive.isChecked()
        replace_count = 0
        
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                item = model.item(row, col)
                if item:
                    cell_text = item.text()
                    original_text = cell_text
                    
                    if not case_sensitive:
                        if search_term.lower() in cell_text.lower():
                            import re
                            cell_text = re.sub(re.escape(search_term), replace_term, cell_text, flags=re.IGNORECASE)
                    else:
                        if search_term in cell_text:
                            cell_text = cell_text.replace(search_term, replace_term)
                    
                    if cell_text != original_text:
                        item.setText(cell_text)
                        replace_count += 1
        
        if replace_count > 0:
            QMessageBox.information(self, "Replace All", f"Replaced {replace_count} occurrence(s).")

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.tableView = CleanTableView(self.centralWidget)
        self.tableView.setObjectName("tableView")
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.verticalLayout.addWidget(self.tableView)
        
        MainWindow.setCentralWidget(self.centralWidget)
        
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

class BoundFileDialog(QDialog):
    """Dialog for selecting bound data files with metadata display."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_binding = None
        self.init_ui()
        self.populate_files()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Select Diablo II Data File")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        
        file_label = QLabel("Available Data Files:")
        file_layout.addWidget(file_label)
        
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        file_layout.addWidget(self.file_list)
        
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        
        metadata_label = QLabel("File Information:")
        metadata_layout.addWidget(metadata_label)
        
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        metadata_layout.addWidget(self.metadata_display)
        
        splitter.addWidget(file_widget)
        splitter.addWidget(metadata_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.accept)
        self.open_button.setEnabled(False)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_files(self):
        """Populate the file list with available bound files."""
        binding_manager = get_binding_manager()
        bindings = binding_manager.get_all_bindings()
        
        for key, binding in sorted(bindings.items()):
            display_name = f"{binding.base_name} ({os.path.basename(binding.txt_path)})"
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, binding)
            self.file_list.addItem(item)
    
    def on_file_selected(self, current, previous):
        """Handle file selection change."""
        if current:
            self.selected_binding = current.data(Qt.ItemDataRole.UserRole)
            self.open_button.setEnabled(True)
            self.update_metadata_display()
        else:
            self.selected_binding = None
            self.open_button.setEnabled(False)
            self.metadata_display.clear()
    
    def update_metadata_display(self):
        """Update the metadata display with information about the selected file."""
        if not self.selected_binding:
            return
        
        binding = self.selected_binding
        metadata = binding.metadata
        
        display_text = f"<h3>{binding.base_name}</h3>"
        display_text += f"<p><strong>Data File:</strong> {os.path.basename(binding.txt_path)}</p>"
        display_text += f"<p><strong>Metadata File:</strong> {os.path.basename(binding.json_path)}</p>"
        
        description = binding.get_description()
        if description and description != "No description available":
            display_text += f"<p><strong>Description:</strong><br>{description}</p>"
        
        column_descriptions = binding.get_column_descriptions()
        if column_descriptions:
            display_text += f"<p><strong>Columns ({len(column_descriptions)}):</strong></p>"
            display_text += "<ul>"
            for col_name, col_desc in list(column_descriptions.items())[:10]:
                display_text += f"<li><strong>{col_name}:</strong> {col_desc}</li>"
            if len(column_descriptions) > 10:
                display_text += f"<li><em>... and {len(column_descriptions) - 10} more columns</em></li>"
            display_text += "</ul>"
        
        self.metadata_display.setHtml(display_text)

from config_manager import ConfigManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.config_manager = ConfigManager()

        layout = QVBoxLayout()

        self.multi_column_selection_checkbox = QCheckBox("Enable multi-column selection")
        self.multi_column_selection_checkbox.setChecked(self.config_manager.get_setting("multi_column_selection_enabled", False))
        layout.addWidget(self.multi_column_selection_checkbox)

        self.ignore_empty_cells_checkbox = QCheckBox("Ignore empty cells on column select")
        self.ignore_empty_cells_checkbox.setChecked(self.config_manager.get_setting("ignore_empty_cells_on_column_select", False))
        layout.addWidget(self.ignore_empty_cells_checkbox)

        self.multi_column_select_all_checkbox = QCheckBox("Enable multi-column select all (Ctrl+R)")
        self.multi_column_select_all_checkbox.setChecked(self.config_manager.get_setting("multi_column_select_all_enabled", False))
        layout.addWidget(self.multi_column_select_all_checkbox)

        self.debug_mode_checkbox = QCheckBox("Enable Debug Mode")
        self.debug_mode_checkbox.setChecked(self.config_manager.get_setting("debug_mode_enabled", False))
        layout.addWidget(self.debug_mode_checkbox)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_settings(self):
        self.config_manager.set_setting("multi_column_selection_enabled", self.multi_column_selection_checkbox.isChecked())
        self.config_manager.set_setting("ignore_empty_cells_on_column_select", self.ignore_empty_cells_checkbox.isChecked())
        self.config_manager.set_setting("multi_column_select_all_enabled", self.multi_column_select_all_checkbox.isChecked())
        self.config_manager.set_setting("debug_mode_enabled", self.debug_mode_checkbox.isChecked())
        self.accept()

class EditorWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(EditorWindow, self).__init__(parent)
        self.setupUi(self)
        self.create_menus()
        self.data_frame = None
        self.current_file_path = None
        self.current_binding = None
        self.undo_stack = UndoStack()
        self._tracking_changes = True
        self.update_window_title()
        self.config_manager = ConfigManager()
        self.unique_column_values = {}
        self.load_unique_column_values()

    def create_menus(self):
        file_menu = self.menubar.addMenu("&File")

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        open_bound_action = QAction("Open &Bound File...", self)
        open_bound_action.setShortcut(QKeySequence("Ctrl+B"))
        open_bound_action.triggered.connect(self.open_bound_file)
        file_menu.addAction(open_bound_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        edit_menu = self.menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_replace_action = QAction("&Find && Replace...", self)
        find_replace_action.setShortcut(QKeySequence.StandardKey.Find)
        find_replace_action.triggered.connect(self.show_search_replace)
        edit_menu.addAction(find_replace_action)

        edit_menu.addSeparator()

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(copy_action)

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_selection)
        edit_menu.addAction(cut_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_selection)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        clear_action = QAction("&Clear Contents", self)
        clear_action.setShortcut(QKeySequence.StandardKey.Delete)
        clear_action.triggered.connect(self.clear_selection)
        edit_menu.addAction(clear_action)

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)

        settings_menu = self.menubar.addMenu("&Settings")
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open .txt file", "", "Text Files (*.txt)")
        if file_path:
            file_type, confidence, binding_key = detect_file_type(file_path)
            detected_encoding = auto_detect_encoding(file_path)
            
            binding_manager = get_binding_manager()
            if len(binding_manager.get_all_bindings()) == 0:
                print("  No metadata loaded, forcing refresh...")
                binding_manager.refresh_bindings()
            
            applied_binding = None
            if binding_key and confidence in ['high', 'medium']:
                applied_binding = binding_manager.create_dynamic_binding(binding_key, file_path)
            
            print(f"Auto-detection results:")
            print(f"  File: {os.path.basename(file_path)}")
            print(f"  Type: {file_type} (confidence: {confidence})")
            print(f"  Encoding: {detected_encoding}")
            if applied_binding:
                print(f"  Applied binding: {applied_binding.base_name}")
            
            self.current_file_path = file_path
            self.current_binding = applied_binding
            data = open_txt_file(file_path)
            if data is not None:
                print(f"File loaded successfully! Type: {file_type}, Encoding: {detected_encoding}")
                self.data_frame = data
                self.display_data_in_table()
                self.update_window_title()
            else:
                QMessageBox.warning(self, "Load Error", "Failed to load file!")
    
    def show_binding_info(self, binding):
        print(f"Applied binding: {binding.base_name}")
        print(f"Description: {binding.get_description()}")

    def open_bound_file(self):
        dialog = BoundFileDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_binding:
            binding = dialog.selected_binding
            self.current_binding = binding
            self.current_file_path = binding.txt_path
            data = binding.load_data()
            if data is not None:
                print(f"Bound file loaded successfully: {binding.base_name}")
                self.data_frame = data
                self.display_data_in_table()
                self.update_window_title()
            else:
                QMessageBox.warning(self, "Load Error", f"Failed to load bound file: {binding.base_name}")
    
    def update_window_title(self):
        if self.current_binding:
            title = f"Diablo II .txt Editor - {self.current_binding.base_name} ({os.path.basename(self.current_binding.txt_path)})"
        elif self.current_file_path:
            title = f"Diablo II .txt Editor - {os.path.basename(self.current_file_path)}"
        else:
            title = "Diablo II .txt Editor"
        self.setWindowTitle(title)

    def load_unique_column_values(self):
        specs_dir = 'specs'
        if not os.path.exists(specs_dir):
            return
        for filename in os.listdir(specs_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(specs_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unique_column_values[os.path.splitext(filename)[0]] = data

    def display_data_in_table(self):
        if self.data_frame is not None:
            model = QStandardItemModel(self.data_frame.shape[0], self.data_frame.shape[1])
            model.setHorizontalHeaderLabels(self.data_frame.columns)

            for row in range(self.data_frame.shape[0]):
                for col in range(self.data_frame.shape[1]):
                    value = self.data_frame.iat[row, col]
                    if pd.isna(value):
                        display_value = ""
                    else:
                        try:
                            if float(value) == int(float(value)):
                                display_value = str(int(float(value)))
                            else:
                                display_value = str(value)
                        except (ValueError, TypeError):
                            display_value = str(value)
                    item = QStandardItem(display_value)
                    model.setItem(row, col, item)
            
            self.tableView.setModel(model)
            model.itemChanged.connect(self.on_item_changed)
            
            header = self.tableView.horizontalHeader()
            header.sectionClicked.connect(self.tableView.select_column)
            header.rightClicked.connect(self.on_header_clicked)
            
            self.connect_context_menu_signals()
            self.undo_stack.clear()

            file_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
            if file_name in self.unique_column_values:
                for col_idx, col_name in enumerate(self.data_frame.columns):
                    if col_name in self.unique_column_values[file_name]:
                        delegate = ComboBoxDelegate(self.tableView, self.unique_column_values[file_name][col_name])
                        self.tableView.setItemDelegateForColumn(col_idx, delegate)
            
            print("Data displayed in table.")
            
    def on_header_clicked(self, logical_index):
        if self.data_frame is not None and logical_index < len(self.data_frame.columns):
            column_name = self.data_frame.columns[logical_index]
            description = "No description available for this column."
            if self.current_binding:
                column_descriptions = self.current_binding.get_column_descriptions()
                description = column_descriptions.get(column_name, description)
            if description == "No description available for this column.":
                description = get_description(self.current_file_path if hasattr(self, 'current_file_path') else "", column_name)
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Column Help: {column_name}")
            msg.setText(f"<b>{column_name}</b><br><br>{description}")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            
    def get_data_from_table(self):
        model = self.tableView.model()
        if not model:
            return None
        data = []
        for row in range(model.rowCount()):
            row_data = []
            for col in range(model.columnCount()):
                item = model.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        columns = [model.horizontalHeaderItem(i).text() for i in range(model.columnCount())]
        return pd.DataFrame(data, columns=columns)

    def create_backup(self, file_path):
        if not os.path.exists(file_path):
            return
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}.bak"
        backup_path = os.path.join(dir_path, backup_name)
        try:
            shutil.copy2(file_path, backup_path)
            print(f"Backup created: {backup_name}")
            self.cleanup_old_backups(dir_path, name)
        except Exception as e:
            print(f"Failed to create backup: {e}")
    
    def cleanup_old_backups(self, dir_path, base_name):
        try:
            backup_files = []
            for filename in os.listdir(dir_path):
                if filename.startswith(f"{base_name}_") and filename.endswith(".bak"):
                    backup_path = os.path.join(dir_path, filename)
                    mtime = os.path.getmtime(backup_path)
                    backup_files.append((mtime, backup_path, filename))
            backup_files.sort(reverse=True)
            max_backups = 5
            if len(backup_files) > max_backups:
                for _, backup_path, filename in backup_files[max_backups:]:
                    os.remove(backup_path)
                    print(f"Removed old backup: {filename}")
        except Exception as e:
            print(f"Failed to cleanup old backups: {e}")

    def save_file(self):
        if self.current_file_path:
            self.create_backup(self.current_file_path)
            df = self.get_data_from_table()
            if df is not None:
                success = save_txt_file(df, self.current_file_path)
                if success:
                    print(f"File saved: {self.current_file_path}")
                else:
                    QMessageBox.warning(self, "Save Error", "Failed to save file!")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save .txt file", "", "Text Files (*.txt)")
        if file_path:
            if os.path.exists(file_path):
                self.create_backup(file_path)
            self.current_file_path = file_path
            self.current_binding = None
            df = self.get_data_from_table()
            if df is not None:
                success = save_txt_file(df, file_path)
                if success:
                    print(f"File saved as: {file_path}")
                    self.update_window_title()
                else:
                    QMessageBox.warning(self, "Save Error", "Failed to save file!")

    def on_item_changed(self, item):
        if not self._tracking_changes:
            return
        row = item.row()
        col = item.column()
        new_value = item.text()
        if self.data_frame is not None and row < len(self.data_frame) and col < len(self.data_frame.columns):
            old_value = self.data_frame.iat[row, col]
            if pd.isna(old_value):
                old_value = ""
            else:
                try:
                    if float(old_value) == int(float(old_value)):
                        old_value = str(int(float(old_value)))
                    else:
                        old_value = str(old_value)
                except (ValueError, TypeError):
                    old_value = str(old_value)
            if old_value != new_value:
                command = UndoCommand(row, col, old_value, new_value)
                self.undo_stack.push(command)
                self.data_frame.iat[row, col] = new_value if new_value != "" else None

    def undo(self):
        command = self.undo_stack.undo()
        if command:
            self._tracking_changes = False
            model = self.tableView.model()
            if model:
                item = model.item(command.row, command.col)
                if item:
                    item.setText(command.old_value)
                    self.data_frame.iat[command.row, command.col] = command.old_value if command.old_value != "" else None
            self._tracking_changes = True

    def redo(self):
        command = self.undo_stack.redo()
        if command:
            self._tracking_changes = False
            model = self.tableView.model()
            if model:
                item = model.item(command.row, command.col)
                if item:
                    item.setText(command.new_value)
                    self.data_frame.iat[command.row, command.col] = command.new_value if command.new_value != "" else None
            self._tracking_changes = True

    def show_search_replace(self):
        if not hasattr(self, 'search_dialog') or self.search_dialog is None:
            self.search_dialog = SearchReplaceDialog(self)
        self.search_dialog.current_row = 0
        self.search_dialog.current_col = 0
        self.search_dialog.show()
        self.search_dialog.search_input.setFocus()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def connect_context_menu_signals(self):
        self.tableView.copy_requested.connect(self.copy_selection)
        self.tableView.cut_requested.connect(self.cut_selection)
        self.tableView.paste_requested.connect(self.paste_selection)
        self.tableView.clear_requested.connect(self.clear_selection)
        self.tableView.select_all_requested.connect(self.select_all)
        self.tableView.insert_row_above_requested.connect(self.insert_row_above)
        self.tableView.insert_row_below_requested.connect(self.insert_row_below)
        self.tableView.delete_row_requested.connect(self.delete_row)
        self.tableView.insert_column_left_requested.connect(self.insert_column_left)
        self.tableView.insert_column_right_requested.connect(self.insert_column_right)
        self.tableView.delete_column_requested.connect(self.delete_column)
        self.tableView.math_action_requested.connect(self.handle_math_action)
        self.tableView.select_column_requested.connect(self.select_column)

    def copy_selection(self):
        selection = self.tableView.selectionModel().selectedIndexes()
        if not selection:
            return
        rows = {}
        for index in selection:
            row = index.row()
            col = index.column()
            if row not in rows:
                rows[row] = {}
            rows[row][col] = index
        clipboard_text = []
        for row in sorted(rows.keys()):
            row_data = []
            cols = sorted(rows[row].keys())
            for col in cols:
                index = rows[row][col]
                item = self.tableView.model().item(index.row(), index.column())
                cell_text = item.text() if item else ""
                row_data.append(cell_text)
            clipboard_text.append("\t".join(row_data))
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(clipboard_text))
        print(f"Copied {len(selection)} cells to clipboard")

    def cut_selection(self):
        self.copy_selection()
        self.clear_selection()

    def paste_selection(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        model = self.tableView.model()
        if not model:
            return
        lines = text.strip().split('\n')
        start_row = current_index.row()
        start_col = current_index.column()
        self._tracking_changes = False
        try:
            for row_offset, line in enumerate(lines):
                cells = line.split('\t')
                target_row = start_row + row_offset
                if target_row >= model.rowCount():
                    break
                for col_offset, cell_value in enumerate(cells):
                    target_col = start_col + col_offset
                    if target_col >= model.columnCount():
                        break
                    item = model.item(target_row, target_col)
                    if item:
                        old_value = item.text()
                        if old_value != cell_value:
                            command = UndoCommand(target_row, target_col, old_value, cell_value)
                            self.undo_stack.push(command)
                            item.setText(cell_value)
                            self.data_frame.iat[target_row, target_col] = cell_value if cell_value != "" else None
        finally:
            self._tracking_changes = True
        print(f"Pasted data at row {start_row}, column {start_col}")

    def clear_selection(self):
        selection = self.tableView.selectionModel().selectedIndexes()
        if not selection:
            return
        model = self.tableView.model()
        if not model:
            return
        self._tracking_changes = False
        try:
            for index in selection:
                item = model.item(index.row(), index.column())
                if item:
                    old_value = item.text()
                    if old_value:
                        command = UndoCommand(index.row(), index.column(), old_value, "")
                        self.undo_stack.push(command)
                        item.setText("")
                        self.data_frame.iat[index.row(), index.column()] = None
        finally:
            self._tracking_changes = True
        print(f"Cleared {len(selection)} cells")

    def select_all(self):
        self.tableView.selectAll()

    def select_column(self, column):
        model = self.tableView.model()
        if not model:
            return
        multi_column_select_all = self.config_manager.get_setting("multi_column_select_all_enabled", False)
        ignore_empty = self.config_manager.get_setting("ignore_empty_cells_on_column_select", False)
        selection = QItemSelection()
        columns_to_select = [column]
        if multi_column_select_all:
            selected_indexes = self.tableView.selectionModel().selectedIndexes()
            if selected_indexes:
                columns_to_select = sorted(list(set(index.column() for index in selected_indexes)))
        for col in columns_to_select:
            for row in range(model.rowCount()):
                index = model.index(row, col)
                item = model.itemFromIndex(index)
                if not ignore_empty or (item and item.text()):
                    selection.select(index, index)
        self.tableView.selectionModel().clear()
        self.tableView.selectionModel().select(selection, self.tableView.selectionModel().SelectionFlag.Select)

    def insert_row_above(self):
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        target_row = current_index.row()
        self._insert_row_at_position(target_row)
        
    def insert_row_below(self):
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        target_row = current_index.row() + 1
        self._insert_row_at_position(target_row)
        
    def _insert_row_at_position(self, row_position):
        model = self.tableView.model()
        if not model:
            return
        model.insertRow(row_position)
        for col in range(model.columnCount()):
            item = QStandardItem("")
            model.setItem(row_position, col, item)
        if self.data_frame is not None:
            new_row = [None] * len(self.data_frame.columns)
            import pandas as pd
            new_df_row = pd.DataFrame([new_row], columns=self.data_frame.columns)
            if row_position == 0:
                self.data_frame = pd.concat([new_df_row, self.data_frame], ignore_index=True)
            elif row_position >= len(self.data_frame):
                self.data_frame = pd.concat([self.data_frame, new_df_row], ignore_index=True)
            else:
                before = self.data_frame.iloc[:row_position]
                after = self.data_frame.iloc[row_position:]
                self.data_frame = pd.concat([before, new_df_row, after], ignore_index=True)
        print(f"Inserted new row at position {row_position}")
        
    def delete_row(self):
        selection = self.tableView.selectionModel().selectedIndexes()
        if not selection:
            return
        selected_rows = sorted(set(index.row() for index in selection), reverse=True)
        model = self.tableView.model()
        if not model:
            return
        if len(selected_rows) > 1:
            reply = QMessageBox.question(
                self,
                "Delete Rows",
                f"Are you sure you want to delete {len(selected_rows)} rows?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        for row in selected_rows:
            model.removeRow(row)
            if self.data_frame is not None and row < len(self.data_frame):
                self.data_frame = self.data_frame.drop(self.data_frame.index[row]).reset_index(drop=True)
        print(f"Deleted {len(selected_rows)} row(s)")
        
    def insert_column_left(self):
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        target_col = current_index.column()
        self._insert_column_at_position(target_col)
        
    def insert_column_right(self):
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        target_col = current_index.column() + 1
        self._insert_column_at_position(target_col)
        
    def _insert_column_at_position(self, col_position):
        model = self.tableView.model()
        if not model:
            return
        from PyQt6.QtWidgets import QInputDialog
        column_name, ok = QInputDialog.getText(
            self,
            "Insert Column",
            "Enter column name:",
            text=f"NewColumn{col_position}"
        )
        if not ok or not column_name.strip():
            return
        column_name = column_name.strip()
        model.insertColumn(col_position)
        model.setHorizontalHeaderItem(col_position, QStandardItem(column_name))
        for row in range(model.rowCount()):
            item = QStandardItem("")
            model.setItem(row, col_position, item)
        if self.data_frame is not None:
            new_column_data = [None] * len(self.data_frame)
            columns = list(self.data_frame.columns)
            columns.insert(col_position, column_name)
            new_data = {}
            for i, col_name in enumerate(columns):
                if i < col_position:
                    old_col_name = list(self.data_frame.columns)[i]
                    new_data[col_name] = self.data_frame[old_col_name]
                elif i == col_position:
                    new_data[col_name] = new_column_data
                else:
                    old_col_name = list(self.data_frame.columns)[i - 1]
                    new_data[col_name] = self.data_frame[old_col_name]
            self.data_frame = pd.DataFrame(new_data)
        print(f"Inserted new column '{column_name}' at position {col_position}")
        
    def delete_column(self):
        current_index = self.tableView.currentIndex()
        if not current_index.isValid():
            return
        selected_col = current_index.column()
        model = self.tableView.model()
        if not model:
            return
        header_item = model.horizontalHeaderItem(selected_col)
        column_name = header_item.text() if header_item else f"Column {selected_col}"
        reply = QMessageBox.question(
            self,
            "Delete Column",
            f"Are you sure you want to delete column '{column_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        model.removeColumn(selected_col)
        if self.data_frame is not None and selected_col < len(self.data_frame.columns):
            column_to_drop = list(self.data_frame.columns)[selected_col]
            self.data_frame = self.data_frame.drop(columns=[column_to_drop])
        print(f"Deleted column '{column_name}'")

    def handle_math_action(self, action):
        """Handle math operations on selected columns"""
        selection = self.tableView.selectionModel().selectedIndexes()
        if not selection:
            return

        if action in ["increment", "decrement"]:
            value = 1  # Fixed value for increment/decrement
            ok = True
        else:
            value, ok = QInputDialog.getDouble(self, f"{action.capitalize()} Column", f"Enter value to {action}:")

        if ok:
            model = self.tableView.model()
            self._tracking_changes = False
            try:
                for index in selection:
                    item = model.item(index.row(), index.column())
                    if item:
                        try:
                            current_value = float(item.text())
                            new_value = 0
                            if action == "multiply":
                                new_value = round(current_value * value)  # Round to nearest integer
                            elif action == "divide":
                                if value != 0:  # Prevent division by zero
                                    new_value = round(current_value / value)
                            elif action == "add":
                                new_value = round(current_value + value)
                            elif action == "subtract":
                                new_value = round(current_value - value)
                            elif action == "increment":
                                new_value = round(current_value + 1)
                            elif action == "decrement":
                                new_value = round(current_value - 1)
                            
                            item.setText(str(new_value))
                            self.data_frame.iat[index.row(), index.column()] = new_value
                        except (ValueError, TypeError):
                            pass
            finally:
                self._tracking_changes = True