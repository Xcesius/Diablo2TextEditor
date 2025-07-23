from PyQt6.QtWidgets import QTableView, QStyledItemDelegate, QMenu, QApplication, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal, QItemSelection, QItemSelectionModel
from PyQt6.QtWidgets import QStyle
from PyQt6.QtGui import QAction, QKeySequence

class CustomHeaderView(QHeaderView):
    rightClicked = pyqtSignal(int)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self._is_selecting = False
        self._start_section = -1

    def show_context_menu(self, position):
        logical_index = self.logicalIndexAt(position)
        self.rightClicked.emit(logical_index)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier):
            index = self.logicalIndexAt(event.pos())
            if index != -1:
                self._is_selecting = True
                self._start_section = index
                table = self.parent()
                if self.orientation() == Qt.Orientation.Horizontal:
                    table.select_column(index)
                else:
                    table.select_row(index)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_selecting:
            index = self.logicalIndexAt(event.pos())
            if index != -1:
                table = self.parent()
                multi_enabled = table.config_manager.get_setting("multi_column_selection_enabled", True) if self.orientation() == Qt.Orientation.Horizontal else table.config_manager.get_setting("multi_row_selection_enabled", True)
                if multi_enabled:
                    min_sec = min(self._start_section, index)
                    max_sec = max(self._start_section, index)
                    for i in range(min_sec, max_sec + 1):
                        if self.orientation() == Qt.Orientation.Horizontal:
                            table.select_column(i)
                        else:
                            table.select_row(i)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_selecting:
            self._is_selecting = False
            self._start_section = -1
            event.accept()
            return
        super().mouseReleaseEvent(event)

class NoHoverDelegate(QStyledItemDelegate):
    """Custom delegate that ignores hover states"""
    def paint(self, painter, option, index):
        # Create a copy of the option and remove hover state
        opt = option
        # Remove the State_MouseOver flag if it exists
        if opt.state & QStyle.StateFlag.State_MouseOver:
            opt.state &= ~QStyle.StateFlag.State_MouseOver
        # Call the parent paint method with modified option
        super().paint(painter, opt, index)

from config_manager import ConfigManager

class CleanTableView(QTableView):
    """A clean table view without hover effects during scrolling, with context menu support"""
    
    # Define signals for context menu actions
    copy_requested = pyqtSignal()
    cut_requested = pyqtSignal()
    paste_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    select_all_requested = pyqtSignal()
    insert_row_above_requested = pyqtSignal()
    insert_row_below_requested = pyqtSignal()
    delete_row_requested = pyqtSignal()
    insert_column_left_requested = pyqtSignal()
    insert_column_right_requested = pyqtSignal()
    delete_column_requested = pyqtSignal()
    math_action_requested = pyqtSignal(str)
    select_column_requested = pyqtSignal(int)
    select_row_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        # Set our custom delegate to disable hover effects
        self.setItemDelegate(NoHoverDelegate())

        # Set custom headers
        self.setHorizontalHeader(CustomHeaderView(Qt.Orientation.Horizontal, self))
        self.setVerticalHeader(CustomHeaderView(Qt.Orientation.Vertical, self))
    
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
        # Set selection behavior - explicitly to SelectItems for cell-level selection
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)  # Ensure cell-based
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)  # Enables drag for rectangle
    
        # Connect signals to methods for selection
        self.select_column_requested.connect(self.select_column)
        self.select_row_requested.connect(self.select_row)

    def select_column(self, column: int):
        """Select all rows in the given column, additively."""
        model = self.model()
        if model:
            rows = model.rowCount()
            if rows > 0:
                start = model.index(0, column)
                end = model.index(rows - 1, column)
                selection = QItemSelection(start, end)
                self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select)

    def select_row(self, row: int):
        """Select all columns in the given row, additively."""
        model = self.model()
        if model:
            cols = model.columnCount()
            if cols > 0:
                start = model.index(row, 0)
                end = model.index(row, cols - 1)
                selection = QItemSelection(start, end)
                self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            current_index = self.currentIndex()
            if current_index.isValid():
                self.select_column_requested.emit(current_index.column())
        else:
            super().keyPressEvent(event)
        
    def show_context_menu(self, position):
        """Show context menu at the given position"""
        # Get the item at the position
        index = self.indexAt(position)
        
        # Create context menu
        menu = QMenu(self)
        
        # Basic clipboard operations
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_requested.emit)
        menu.addAction(copy_action)
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_requested.emit)
        menu.addAction(cut_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_requested.emit)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # Cell operations
        clear_action = QAction("&Clear Contents", self)
        clear_action.setShortcut(QKeySequence.StandardKey.Delete)
        clear_action.triggered.connect(self.clear_requested.emit)
        menu.addAction(clear_action)
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.select_all_requested.emit)
        menu.addAction(select_all_action)

        select_row_action = QAction("Select Ro&w", self)
        select_row_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        select_row_action.triggered.connect(lambda: self.select_row_requested.emit(index.row()))
        menu.addAction(select_row_action)

        select_column_action = QAction("Select &Column", self)
        select_column_action.setShortcut(QKeySequence("Ctrl+R"))
        select_column_action.triggered.connect(lambda: self.select_column_requested.emit(index.column()))
        menu.addAction(select_column_action)
        
        menu.addSeparator()

        # Math operations
        math_menu = menu.addMenu("Math Operations")
        
        multiply_action = QAction("Multiply", self)
        multiply_action.triggered.connect(lambda: self.math_action_requested.emit("multiply"))
        math_menu.addAction(multiply_action)

        divide_action = QAction("Divide", self)
        divide_action.triggered.connect(lambda: self.math_action_requested.emit("divide"))
        math_menu.addAction(divide_action)

        add_action = QAction("Add", self)
        add_action.triggered.connect(lambda: self.math_action_requested.emit("add"))
        math_menu.addAction(add_action)

        subtract_action = QAction("Subtract", self)
        subtract_action.triggered.connect(lambda: self.math_action_requested.emit("subtract"))
        math_menu.addAction(subtract_action)

        increment_action = QAction("Increment by 1", self)
        increment_action.triggered.connect(lambda: self.math_action_requested.emit("increment"))
        math_menu.addAction(increment_action)

        decrement_action = QAction("Decrement by 1", self)
        decrement_action.triggered.connect(lambda: self.math_action_requested.emit("decrement"))
        math_menu.addAction(decrement_action)

        menu.addSeparator()
        
        # Row operations
        insert_row_above_action = QAction("Insert Row &Above", self)
        insert_row_above_action.triggered.connect(self.insert_row_above_requested.emit)
        menu.addAction(insert_row_above_action)
        
        insert_row_below_action = QAction("Insert Row &Below", self)
        insert_row_below_action.triggered.connect(self.insert_row_below_requested.emit)
        menu.addAction(insert_row_below_action)
        
        delete_row_action = QAction("&Delete Row", self)
        delete_row_action.triggered.connect(self.delete_row_requested.emit)
        menu.addAction(delete_row_action)
        
        menu.addSeparator()
        
        # Column operations
        insert_column_left_action = QAction("Insert Column &Left", self)
        insert_column_left_action.triggered.connect(self.insert_column_left_requested.emit)
        menu.addAction(insert_column_left_action)
        
        insert_column_right_action = QAction("Insert Column &Right", self)
        insert_column_right_action.triggered.connect(self.insert_column_right_requested.emit)
        menu.addAction(insert_column_right_action)
        
        delete_column_action = QAction("Delete &Column", self)
        delete_column_action.triggered.connect(self.delete_column_requested.emit)
        menu.addAction(delete_column_action)
        
        # Enable/disable actions based on selection and clipboard state
        has_selection = len(self.selectedIndexes()) > 0
        clipboard = QApplication.clipboard()
        has_clipboard_data = clipboard.mimeData().hasText()
        
        copy_action.setEnabled(has_selection)
        cut_action.setEnabled(has_selection)
        paste_action.setEnabled(has_clipboard_data)
        clear_action.setEnabled(has_selection)

        # Enable math actions only if selection is numeric
        can_do_math = False
        if has_selection:
            can_do_math = True
            for s_index in self.selectedIndexes():
                item = self.model().itemFromIndex(s_index)
                if item:
                    try:
                        float(item.text())
                    except (ValueError, TypeError):
                        can_do_math = False
                        break
        math_menu.setEnabled(can_do_math)
        
        # Row/column operations are enabled when we have a valid selection
        has_valid_selection = index.isValid()
        select_row_action.setEnabled(has_valid_selection)
        select_column_action.setEnabled(has_valid_selection)
        insert_row_above_action.setEnabled(has_valid_selection)
        insert_row_below_action.setEnabled(has_valid_selection)
        delete_row_action.setEnabled(has_valid_selection)
        insert_column_left_action.setEnabled(has_valid_selection)
        insert_column_right_action.setEnabled(has_valid_selection)
        delete_column_action.setEnabled(has_valid_selection)
        
        # Show the menu
        menu.exec(self.mapToGlobal(position))