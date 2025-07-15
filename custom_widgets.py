from PyQt6.QtWidgets import QTableView, QStyledItemDelegate, QMenu, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QStyle
from PyQt6.QtGui import QAction, QKeySequence

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set our custom delegate to disable hover effects
        self.setItemDelegate(NoHoverDelegate())
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
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
        
        # Row/column operations are enabled when we have a valid selection
        has_valid_selection = index.isValid()
        insert_row_above_action.setEnabled(has_valid_selection)
        insert_row_below_action.setEnabled(has_valid_selection)
        delete_row_action.setEnabled(has_valid_selection)
        insert_column_left_action.setEnabled(has_valid_selection)
        insert_column_right_action.setEnabled(has_valid_selection)
        delete_column_action.setEnabled(has_valid_selection)
        
        # Show the menu
        menu.exec(self.mapToGlobal(position)) 