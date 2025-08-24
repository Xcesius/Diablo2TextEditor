from PyQt6.QtWidgets import (QTableView, QStyledItemDelegate, QMenu, QApplication,
                             QHeaderView, QStyle, QAbstractItemView, QInputDialog, QMessageBox)
from PyQt6.QtCore import (Qt, pyqtSignal, QItemSelection, QItemSelectionModel,
                          QTimer, QEvent, QPersistentModelIndex)
from PyQt6.QtGui import (QAction, QKeySequence, QStandardItemModel, QStandardItem,
                         QPainter, QPen, QColor)
from config_manager import ConfigManager as AppConfigManager

class CustomHeaderView(QHeaderView):
    rightClicked = pyqtSignal(int)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self._is_selecting = False
        self._start_section = -1
        # Crosshair highlighting for active section
        self._highlighted_section = -1
        self._show_crosshair_guides = True
        self._crosshair_color = QColor(0, 120, 215, 60)  # light accent fill
        self._crosshair_border = QColor(0, 120, 215, 180)
        self._crosshair_border_width = 1

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
                try:
                    multi_enabled = table.config_manager.get_setting("multi_column_selection_enabled", True) if self.orientation() == Qt.Orientation.Horizontal else table.config_manager.get_setting("multi_row_selection_enabled", True)
                except AttributeError as e:
                    import logging
                    logging.debug(f"Config manager not available for multi-selection: {e}")
                    multi_enabled = True # Default fallback
                except Exception as e:
                    import logging
                    logging.warning(f"Unexpected error accessing multi-selection setting: {e}")
                    multi_enabled = True
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

    # --- Crosshair helpers ---
    def setCrosshairGuidesEnabled(self, enabled: bool):
        self._show_crosshair_guides = bool(enabled)
        self.viewport().update()

    def setHighlightedSection(self, section_index: int):
        self._highlighted_section = section_index if section_index is not None else -1
        self.viewport().update()

    def setCrosshairStyle(self, fill_color: QColor = None, border_color: QColor = None, border_width: int = None):
        if fill_color is not None:
            self._crosshair_color = fill_color
        if border_color is not None:
            self._crosshair_border = border_color
        if border_width is not None:
            self._crosshair_border_width = int(border_width)
        self.viewport().update()

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        if not self._show_crosshair_guides:
            return
        if logicalIndex != self._highlighted_section or not rect.isValid():
            return
        # Light fill to make the active column/row name pop
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._crosshair_color)
        painter.drawRect(rect)
        # Subtle border to increase contrast
        pen = QPen(self._crosshair_border)
        pen.setWidth(self._crosshair_border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
        painter.restore()

class NoHoverDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = option
        if opt.state & QStyle.StateFlag.State_MouseOver:
            opt.state &= ~QStyle.StateFlag.State_MouseOver
        super().paint(painter, opt, index)

    def createEditor(self, parent, option, index):
        # Ensure editors are parented to the view's viewport so commitData sees them as belonging to the view
        try:
            view = self.parent() if isinstance(self.parent(), QTableView) else None
            parent_to_use = view.viewport() if (view is not None and hasattr(view, 'viewport')) else parent
        except (AttributeError, TypeError) as e:
            import logging
            logging.debug(f"Error setting up editor parent: {e}")
            view = None
            parent_to_use = parent
        except Exception as e:
            import logging
            logging.warning(f"Unexpected error in createEditor parent setup: {e}")
            view = None
            parent_to_use = parent
        editor = super().createEditor(parent_to_use, option, index)
        # Tag the editor with a persistent index so we can commit manually without ambiguity
        try:
            editor.setProperty("_d2te_index", QPersistentModelIndex(index))
        except (AttributeError, TypeError) as e:
            import logging
            logging.debug(f"Could not set _d2te_index property on editor: {e}")
        except Exception as e:
            import logging
            logging.warning(f"Unexpected error setting editor property: {e}")
        # Name and debug-log the default editor to trace ownership
        try:
            # Get view ID if available for better tracking
            view_id = getattr(view, '_view_id', 'unknown') if view else 'noview'
            editor.setObjectName(f"DefaultEditor_{view_id}_r{index.row()}_c{index.column()}")
            
            vname = (view.objectName() if view else parent_to_use.objectName()) or repr(view or parent_to_use)
            # Config may not be reachable; guard
            debug_on = False
            try:
                cfg = getattr(view, 'config_manager', None)
                if cfg:
                    debug_on = cfg.get_setting("debug_mode_enabled", False)
            except Exception:
                debug_on = False
            if debug_on:
                chain = []
                p = editor.parent()
                steps = 0
                while p is not None and steps < 6:
                    chain.append(p.__class__.__name__)
                    p = p.parent()
                    steps += 1
                print(f"[DEBUG] default createEditor -> {editor.objectName()} for view {vname}; parent_chain={' > '.join(chain) if chain else 'None'}")
        except (AttributeError, TypeError, ValueError) as e:
            import logging
            logging.debug(f"Error in editor debug setup: {e}")
        except Exception as e:
            import logging
            logging.warning(f"Unexpected error in createEditor debug setup: {e}")
        return editor

class OverlayTableView(QTableView):
    """Lightweight QTableView that allows drawing an overlay after normal paint.
    Used for frozen panes so crosshair lines render reliably on top.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_callback = None

    def setOverlayCallback(self, callback):
        self._overlay_callback = callback

    def paintEvent(self, event):
        super().paintEvent(event)
        if callable(self._overlay_callback):
            try:
                painter = QPainter(self.viewport())
                self._overlay_callback(painter)
                painter.end()
            except (RuntimeError, AttributeError) as e:
                import logging
                logging.debug(f"Error in overlay painting: {e}")
            except Exception as e:
                import logging
                logging.warning(f"Unexpected error in paintEvent overlay: {e}")

    # Guard against stray commitData for editors not owned by this mirror view
    def commitData(self, editor):
        try:
            # Determine if the editor belongs to this view or its viewport
            p = editor
            owns = False
            depth = 0
            while p is not None and depth < 8:
                if p is self or p is self.viewport():
                    owns = True
                    break
                p = p.parent()
                depth += 1
            if not owns:
                # Optional debug
                try:
                    cfg = getattr(self.parent(), 'config_manager', None) or getattr(self, 'config_manager', None)
                    if cfg and cfg.get_setting("debug_mode_enabled", False):
                        vname = self.objectName() or f"OverlayTableView@{id(self):x}"
                        ename = editor.objectName() or editor.__class__.__name__
                        print(f"[DEBUG] overlay.commitData ignored on {vname}: editor={ename} not owned by this view")
                except (AttributeError, TypeError) as e:
                    import logging
                    logging.debug(f"Error in overlay commitData debug: {e}")
                except Exception as e:
                    import logging
                    logging.warning(f"Unexpected error in overlay commitData: {e}")
                return
        except Exception:
            pass
        super().commitData(editor)

class CleanTableView(QTableView):
    # --- Signals remain unchanged ---
    copy_requested = pyqtSignal()
    cut_requested = pyqtSignal()
    paste_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    select_all_requested = pyqtSignal()
    insert_row_above_requested = pyqtSignal()
    insert_row_below_requested = pyqtSignal()
    insert_rows_above_requested = pyqtSignal(int)
    insert_rows_below_requested = pyqtSignal(int)
    delete_row_requested = pyqtSignal()
    insert_column_left_requested = pyqtSignal()
    insert_column_right_requested = pyqtSignal()
    insert_columns_left_requested = pyqtSignal(int)
    insert_columns_right_requested = pyqtSignal(int)
    delete_column_requested = pyqtSignal()
    math_action_requested = pyqtSignal(str)
    conditional_math_requested = pyqtSignal(object)
    select_column_requested = pyqtSignal(int)
    select_row_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = AppConfigManager()
        # Generate unique identifier for this view instance
        import time
        self._view_id = f"ctv_{int(time.time() * 1000000) % 1000000}_{id(self) % 10000}"
        # Use a stored base delegate so we can optionally introspect its signals during debugging
        try:
            self._base_delegate = NoHoverDelegate(self)
        except Exception:
            self._base_delegate = NoHoverDelegate()
        self.setItemDelegate(self._base_delegate)
        # Improve edit UX: double-click or edit key starts edit, Enter commits
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self._saved_edit_triggers = None

        # Crosshair guides settings
        self._show_crosshair_guides = True
        self._crosshair_color = QColor(0, 120, 215, 180)  # Windows accent-like
        self._crosshair_width = 1
        self._current_row = -1
        self._current_col = -1
        self._hover_row = -1
        self._hover_col = -1
        self._hover_enabled = True

        # --- Frozen Column View Setup ---
        self.frozen_column_view = OverlayTableView(self)
        self.frozen_column_view.setItemDelegate(NoHoverDelegate())
        self.frozen_column_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Prevent any editing from occurring in the frozen column mirror view
        self.frozen_column_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.frozen_column_view.verticalHeader().hide()  # Hide vertical header; main view's suffices
        self.frozen_column_view.setHorizontalHeader(CustomHeaderView(Qt.Orientation.Horizontal, self.frozen_column_view))  # Use CustomHeaderView for consistency
        self.frozen_column_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # Fix: Set resize mode to Fixed for frozen header
        self.frozen_column_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_column_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_column_view.setVisible(False)

        # --- Frozen Row View Setup ---
        self.frozen_row_view = OverlayTableView(self)
        self.frozen_row_view.setItemDelegate(NoHoverDelegate())
        self.frozen_row_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Prevent any editing from occurring in the frozen row mirror view
        self.frozen_row_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.frozen_row_view.verticalHeader().hide()
        self.frozen_row_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_row_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.frozen_row_view.setVisible(False)

        self._frozen_column_width = 0
        self._frozen_row_height = 0

        self.setHorizontalHeader(CustomHeaderView(Qt.Orientation.Horizontal, self))
        self.setVerticalHeader(CustomHeaderView(Qt.Orientation.Vertical, self))

        # --- Fix stacking order: Raise frozen views after headers are set ---
        self.frozen_column_view.raise_()
        self.frozen_row_view.raise_()

        # --- Connect Scrollbars for Synchronization ---
        self.verticalScrollBar().valueChanged.connect(self.frozen_column_view.verticalScrollBar().setValue)
        self.frozen_column_view.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.horizontalScrollBar().valueChanged.connect(self.frozen_row_view.horizontalScrollBar().setValue)
        self.frozen_row_view.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBar().setValue)

        # Connect header resizing to update frozen view geometries
        self.horizontalHeader().sectionResized.connect(self._update_frozen_views_column_width)
        self.verticalHeader().sectionResized.connect(self._update_frozen_column_row_height)

        # Additional: Sync header height changes (if dynamic)
        self.horizontalHeader().sectionResized.connect(self._sync_header_heights)  # New connection for header height sync
        self.verticalHeader().sectionResized.connect(self._sync_header_heights)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)

        # Connect signals for column/row selection
        self.select_column_requested.connect(self.select_column)
        self.select_row_requested.connect(self.select_row)

        # Track current cell for crosshair guides
        # Will be fully connected when a model is set
        self._selection_conn_made = False

        # Enable hover tracking across all viewports
        try:
            self.viewport().setMouseTracking(True)
            self.viewport().installEventFilter(self)
        except Exception:
            pass
        # Hook delegate signals for debug tracing if available
        try:
            self._base_delegate.commitData.connect(self._on_delegate_commit)
        except Exception:
            pass
        try:
            self._base_delegate.closeEditor.connect(self._on_delegate_close)
        except Exception:
            pass

    def setModel(self, model):
        super().setModel(model)
        if model:
            self.frozen_column_view.setModel(model)
            self.frozen_column_view.setSelectionModel(self.selectionModel())
            self.frozen_row_view.setModel(model)
            self.frozen_row_view.setSelectionModel(self.selectionModel())
            # Hook current index changes for crosshair
            if not self._selection_conn_made:
                try:
                    self.selectionModel().currentChanged.connect(self._on_current_changed)
                    self._selection_conn_made = True
                except Exception:
                    pass
            # Ensure hover tracking is set for frozen views
            try:
                self.frozen_column_view.viewport().setMouseTracking(True)
                self.frozen_column_view.viewport().installEventFilter(self)
            except Exception:
                pass
            try:
                self.frozen_row_view.viewport().setMouseTracking(True)
                self.frozen_row_view.viewport().installEventFilter(self)
            except Exception:
                pass
            # Overlay callbacks to draw crosshair lines reliably on frozen panes
            def draw_frozen_col_overlay(p: QPainter):
                if not self._show_crosshair_guides:
                    return
                eff_row = self._hover_row if self._hover_row >= 0 else self._current_row
                if self.model() is None or eff_row < 0:
                    return
                try:
                    idx_left = self.model().index(eff_row, 0)
                    rect_left = self.frozen_column_view.visualRect(idx_left)
                    if not rect_left.isValid():
                        return
                    pen2 = QPen(self._crosshair_color)
                    pen2.setWidth(self._crosshair_width)
                    p.setPen(pen2)
                    y_left = rect_left.top()
                    p.drawLine(0, y_left, self.frozen_column_view.viewport().width(), y_left)
                except Exception:
                    pass

            def draw_frozen_row_overlay(p: QPainter):
                if not self._show_crosshair_guides:
                    return
                eff_col = self._hover_col if self._hover_col >= 0 else self._current_col
                if self.model() is None or eff_col < 0:
                    return
                try:
                    idx_top = self.model().index(0, eff_col)
                    rect_top = self.frozen_row_view.visualRect(idx_top)
                    if not rect_top.isValid():
                        return
                    pen3 = QPen(self._crosshair_color)
                    pen3.setWidth(self._crosshair_width)
                    p.setPen(pen3)
                    x_top = rect_top.left()
                    p.drawLine(x_top, 0, x_top, self.frozen_row_view.viewport().height())
                except Exception:
                    pass

            self.frozen_column_view.setOverlayCallback(draw_frozen_col_overlay)
            self.frozen_row_view.setOverlayCallback(draw_frozen_row_overlay)

    def set_first_column_frozen(self, frozen: bool):
        if self.model() is None or self.model().columnCount() == 0:
            frozen = False
            
        self._frozen_column_width = self.columnWidth(0) if frozen else 0
        self.frozen_column_view.setVisible(frozen)

        if frozen:
            # Hide all but first column
            for col in range(1, self.model().columnCount()):
                self.frozen_column_view.setColumnHidden(col, True)
            self.frozen_column_view.setColumnHidden(0, False)
            # Initial sync of column width and all row heights
            self.frozen_column_view.setColumnWidth(0, self.columnWidth(0))
            for row in range(self.model().rowCount()):
                self.frozen_column_view.setRowHeight(row, self.rowHeight(row))
            # Sync header height
            self._sync_header_heights()
        
        # Remove viewport margins - follow official Qt example
        self._update_geometries()

    def set_first_row_frozen(self, frozen: bool):
        if self.model() is None or self.model().rowCount() == 0:
            frozen = False
            
        self._frozen_row_height = self.rowHeight(0) if frozen else 0
        self.frozen_row_view.setVisible(frozen)
        
        if frozen:
            # Hide all but first row
            for row in range(1, self.model().rowCount()):
                self.frozen_row_view.setRowHidden(row, True)
            self.frozen_row_view.setRowHidden(0, False)

    # --- Crosshair guides public API ---
    def setCrosshairGuidesEnabled(self, enabled: bool):
        self._show_crosshair_guides = bool(enabled)
        # Propagate to headers
        for hv in (self.horizontalHeader(), self.verticalHeader(),
                   getattr(self.frozen_column_view, 'horizontalHeader', lambda: None)() or None,
                   getattr(self.frozen_row_view, 'horizontalHeader', lambda: None)() or None):
            if isinstance(hv, CustomHeaderView):
                hv.setCrosshairGuidesEnabled(self._show_crosshair_guides)
        self.viewport().update()
        self.frozen_column_view.viewport().update()
        self.frozen_row_view.viewport().update()

    def crosshairGuidesEnabled(self) -> bool:
        return self._show_crosshair_guides

    def setCrosshairColor(self, color: QColor):
        self._crosshair_color = color
        self.viewport().update()
        self.frozen_column_view.viewport().update()
        self.frozen_row_view.viewport().update()

    def setCrosshairWidth(self, width: int):
        self._crosshair_width = max(1, int(width))
        self.viewport().update()
        self.frozen_column_view.viewport().update()
        self.frozen_row_view.viewport().update()

    def setCrosshairHoverEnabled(self, enabled: bool):
        self._hover_enabled = bool(enabled)
        if not self._hover_enabled:
            self._hover_row = -1
            self._hover_col = -1
            self._on_current_changed(self.currentIndex(), None)
        else:
            # Trigger a repaint to pick up the current hover if any
            self.viewport().update()
            self.frozen_column_view.viewport().update()
            self.frozen_row_view.viewport().update()

    # --- Crosshair core logic ---
    def _on_current_changed(self, current, previous):
        if not current or not current.isValid():
            self._current_row = -1
            self._current_col = -1
        else:
            self._current_row = current.row()
            self._current_col = current.column()
        # Update header highlights
        try:
            eff_col = self._hover_col if self._hover_col >= 0 else self._current_col
            eff_row = self._hover_row if self._hover_row >= 0 else self._current_row
            if isinstance(self.horizontalHeader(), CustomHeaderView):
                self.horizontalHeader().setHighlightedSection(eff_col)
            if isinstance(self.verticalHeader(), CustomHeaderView):
                self.verticalHeader().setHighlightedSection(eff_row)
            # Frozen mirrors
            h_frozen = self.frozen_column_view.horizontalHeader()
            if isinstance(h_frozen, CustomHeaderView):
                h_frozen.setHighlightedSection(eff_col)
            h_frozen_row = self.frozen_row_view.horizontalHeader()
            if isinstance(h_frozen_row, CustomHeaderView):
                h_frozen_row.setHighlightedSection(eff_col)
        except Exception:
            pass
        # Repaint overlays
        self.viewport().update()
        self.frozen_column_view.viewport().update()
        self.frozen_row_view.viewport().update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseMove and self._show_crosshair_guides and self._hover_enabled:
            try:
                if obj is self.viewport():
                    idx = self.indexAt(event.pos())
                elif obj is self.frozen_column_view.viewport():
                    idx = self.frozen_column_view.indexAt(event.pos())
                elif obj is self.frozen_row_view.viewport():
                    idx = self.frozen_row_view.indexAt(event.pos())
                else:
                    return super().eventFilter(obj, event)

                if idx and idx.isValid():
                    # Determine effective hover row/col per source viewport
                    if obj is self.viewport():
                        row = idx.row()
                        col = idx.column()
                    elif obj is self.frozen_column_view.viewport():
                        row = idx.row()
                        # Column is first frozen column (0)
                        col = 0
                    else:  # frozen_row_view
                        # Row is first frozen row (0); take actual column
                        row = 0
                        col = idx.column()
                    self._hover_row = row
                    self._hover_col = col
                    # Update headers to reflect hover
                    try:
                        if isinstance(self.horizontalHeader(), CustomHeaderView):
                            self.horizontalHeader().setHighlightedSection(self._hover_col)
                        if isinstance(self.verticalHeader(), CustomHeaderView):
                            self.verticalHeader().setHighlightedSection(self._hover_row)
                        hf = self.frozen_column_view.horizontalHeader()
                        if isinstance(hf, CustomHeaderView):
                            hf.setHighlightedSection(self._hover_col)
                        hfr = self.frozen_row_view.horizontalHeader()
                        if isinstance(hfr, CustomHeaderView):
                            hfr.setHighlightedSection(self._hover_col)
                    except Exception:
                        pass
                    # Repaint
                    self.viewport().update()
                    self.frozen_column_view.viewport().update()
                    self.frozen_row_view.viewport().update()
            except Exception:
                pass
        elif event.type() == QEvent.Type.Leave:
            # Clear hover; fall back to current selection
            self._hover_row = -1
            self._hover_col = -1
            self._on_current_changed(self.currentIndex(), None)
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._show_crosshair_guides:
            return
        # Determine effective row/col from hover if available, else current selection
        eff_row = self._hover_row if self._hover_row >= 0 else self._current_row
        eff_col = self._hover_col if self._hover_col >= 0 else self._current_col
        if self.model() is None or eff_row < 0 or eff_col < 0:
            return
        # Draw crosshair lines aligned to the active cell
        try:
            model = self.model()
            # Main view overlay
            idx = model.index(eff_row, eff_col)
            rect = self.visualRect(idx)
            if rect.isValid() and self.viewport().isVisible():
                p = QPainter(self.viewport())
                if p.isActive():  # Check if painter is valid
                    pen = QPen(self._crosshair_color)
                    pen.setWidth(self._crosshair_width)
                    p.setPen(pen)
                    # Vertical line across main viewport
                    x = rect.left()
                    p.drawLine(x, 0, x, self.viewport().height())
                    # Horizontal line across main viewport
                    y = rect.top()
                    p.drawLine(0, y, self.viewport().width(), y)
                p.end()

            # Frozen overlays are handled by OverlayTableView callbacks

            # 3) Extend crosshair into headers
            try:
                # Horizontal header (column names) - draw vertical line at column
                hh = self.horizontalHeader()
                if hh and hh.isVisible() and hh.viewport().isVisible():
                    xh = hh.sectionViewportPosition(eff_col)
                    if xh >= 0:
                        ph = QPainter(hh.viewport())
                        if ph.isActive():  # Check if painter is valid
                            penh = QPen(self._crosshair_color)
                            penh.setWidth(self._crosshair_width)
                            ph.setPen(penh)
                            ph.drawLine(xh, 0, xh, hh.viewport().height())
                        ph.end()
                # Vertical header (row numbers) - draw horizontal line at row
                vh = self.verticalHeader()
                if vh and vh.isVisible() and vh.viewport().isVisible():
                    yv = vh.sectionViewportPosition(eff_row)
                    if yv >= 0:
                        pv = QPainter(vh.viewport())
                        if pv.isActive():  # Check if painter is valid
                            penv = QPen(self._crosshair_color)
                            penv.setWidth(self._crosshair_width)
                            pv.setPen(penv)
                            pv.drawLine(0, yv, vh.viewport().width(), yv)
                        pv.end()
                # Frozen row view header (top header for all columns) - vertical line
                fr_hh = self.frozen_row_view.horizontalHeader()
                if fr_hh and fr_hh.isVisible() and fr_hh.viewport().isVisible():
                    xfh = fr_hh.sectionViewportPosition(eff_col)
                    if xfh >= 0:
                        pfh = QPainter(fr_hh.viewport())
                        if pfh.isActive():  # Check if painter is valid
                            penfh = QPen(self._crosshair_color)
                            penfh.setWidth(self._crosshair_width)
                            pfh.setPen(penfh)
                            pfh.drawLine(xfh, 0, xfh, fr_hh.viewport().height())
                        pfh.end()
            except Exception:
                pass
        except Exception:
            pass
            # Initial sync of row height and all column widths
            self.frozen_row_view.setRowHeight(0, self.rowHeight(0))
            for col in range(self.model().columnCount()):
                self.frozen_row_view.setColumnWidth(col, self.columnWidth(col))
            # Sync header height (for completeness)
            self._sync_header_heights()
        
        # Remove viewport margins - follow official Qt example
        self._update_geometries()

    def _update_geometries(self):
        """Positions the frozen views in the margin area."""
        # Position the frozen row view
        if self.frozen_row_view.isVisible():
            self.frozen_row_view.setGeometry(
                self.frameWidth() + self.verticalHeader().width() + self._frozen_column_width,
                self.frameWidth(),
                self.viewport().width(),
                self._frozen_row_height
            )

        # Position the frozen column view - fix y position to 0 for better alignment
        if self.frozen_column_view.isVisible():
            x_pos = self.frameWidth() + (self.verticalHeader().width() if self.verticalHeader().isVisible() else 0)
            self.frozen_column_view.setGeometry(
                x_pos,
                0,  # Changed from self.frameWidth() to 0 for better alignment
                self._frozen_column_width,
                self.viewport().height() + self.horizontalHeader().height()
            )
        
        # Note: No calls to sync methods here to avoid recursion

    def _update_frozen_views_column_width(self, logicalIndex, oldSize, newSize):
        """Sync column widths on resize."""
        if self.frozen_row_view.isVisible():
            self.frozen_row_view.setColumnWidth(logicalIndex, newSize)
        if self.frozen_column_view.isVisible() and logicalIndex == 0:
            self.frozen_column_view.setColumnWidth(0, newSize)
            if oldSize != newSize:
                self._frozen_column_width = newSize
                self._update_geometries()

    def _update_frozen_column_row_height(self, logicalIndex, oldSize, newSize):
        """Sync row heights on resize."""
        if self.frozen_column_view.isVisible():
            self.frozen_column_view.setRowHeight(logicalIndex, newSize)
        if self.frozen_row_view.isVisible() and logicalIndex == 0:
            self.frozen_row_view.setRowHeight(0, newSize)
            if oldSize != newSize:
                self._frozen_row_height = newSize
                self._update_geometries()

    def _sync_header_heights(self, *args):
        """Sync horizontal header heights between main and frozen views."""
        header_height = self.horizontalHeader().height()
        self.frozen_column_view.horizontalHeader().setFixedHeight(header_height)
        self.frozen_row_view.horizontalHeader().setFixedHeight(header_height)
        self._update_geometries()

    def resizeEvent(self, event):
        """On resize, update geometries."""
        super().resizeEvent(event)
        self._update_geometries()

    def moveCursor(self, cursorAction, modifiers):
        """Override moveCursor to prevent selection from hiding under frozen column."""
        current = super().moveCursor(cursorAction, modifiers)
        if cursorAction == QAbstractItemView.CursorAction.MoveLeft and current.column() > 0:
            rect = self.visualRect(current)
            if rect.topLeft().x() < self._frozen_column_width:
                new_value = self.horizontalScrollBar().value() + rect.topLeft().x() - self._frozen_column_width
                self.horizontalScrollBar().setValue(new_value)
        return current

    # --- Other methods like select_column, select_row, keyPressEvent, etc. remain unchanged ---
    def select_column(self, column: int):
        model = self.model()
        if model:
            rows = model.rowCount()
            if rows > 0:
                start = model.index(0, column)
                end = model.index(rows - 1, column)
                selection = QItemSelection(start, end)
                self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select)

    def select_row(self, row: int):
        model = self.model()
        if model:
            cols = model.columnCount()
            if cols > 0:
                start = model.index(row, 0)
                end = model.index(row, cols - 1)
                selection = QItemSelection(start, end)
                self.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.Select)

    def _is_debug_enabled(self):
        """Helper method to check if debug mode is enabled"""
        try:
            return self.config_manager.get_setting("debug_mode_enabled", False)
        except Exception:
            return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Commit current editor if any
            if self.state() == QAbstractItemView.State.EditingState:
                try:
                    self._close_current_inline_editor()
                except Exception:
                    pass
            # Move down to mimic spreadsheet feel (optional)
            current = self.currentIndex()
            if current.isValid() and current.row() + 1 < (self.model().rowCount() if self.model() else 0):
                self.setCurrentIndex(self.model().index(current.row() + 1, current.column()))
            return
        if event.key() == Qt.Key.Key_R and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            current_index = self.currentIndex()
            if current_index.isValid():
                self.select_column_requested.emit(current_index.column())
        else:
            super().keyPressEvent(event)

    # --- Debug helpers ---
    def closeEditor(self, editor, hint):
        try:
            debug_on = self._is_debug_enabled()
            if debug_on:
                vname = self.objectName() or f"CleanTableView@{id(self):x}"
                ename = editor.objectName() or editor.__class__.__name__
                p = editor.parent()
                chain = []
                steps = 0
                while p is not None and steps < 4:
                    chain.append(p.__class__.__name__ + ("[viewport]" if hasattr(self, 'viewport') and p is self.viewport() else ""))
                    p = p.parent()
                    steps += 1
                print(f"[DEBUG] closeEditor called on {vname}: editor={ename} ({editor.__class__.__name__}), parent_chain={' > '.join(chain) if chain else 'None'}, hint={int(hint)}")
        except Exception:
            pass
        super().closeEditor(editor, hint)

    def commitData(self, editor):
        # Intercept commitData to avoid warnings for editors that do not belong to this view
        try:
            debug_on = self._is_debug_enabled()
            
            vname = self.objectName() or f"CleanTableView@{id(self):x}"
            ename = editor.objectName() or editor.__class__.__name__
            view_id = getattr(self, '_view_id', 'no_id')
            
            if debug_on:
                print(f"[DEBUG] commitData called on view {vname} (view_id={view_id}) for editor {ename}")
            
            # Ensure the editor lives under this view's viewport
            try:
                current_parent = editor.parent()
                expected_parent = self.viewport()
                if current_parent is not expected_parent and expected_parent is not None:
                    if debug_on:
                        print(f"[DEBUG] Reparenting editor {ename} from {current_parent.__class__.__name__ if current_parent else 'None'} to {expected_parent.__class__.__name__}")
                    editor.setParent(expected_parent)
            except Exception as commit_ex:
                if debug_on:
                    print(f"[DEBUG] Exception ensuring editor parent: {commit_ex}")
            
            # Manual commit path to avoid Qt's internal warning. Resolve the target index robustly.
            idx = None
            try:
                pidx = editor.property("_d2te_index")
                if pidx is not None:
                    # Guard against stale indices
                    row = int(pidx.row())
                    col = int(pidx.column())
                    if self.model() and 0 <= row < self.model().rowCount() and 0 <= col < self.model().columnCount():
                        idx = self.model().index(row, col)
            except Exception:
                idx = None
            if (idx is None) or (not getattr(idx, 'isValid', lambda: False)()):
                try:
                    ci = self.currentIndex()
                    if ci and ci.isValid():
                        idx = ci
                except Exception:
                    idx = None
            if (idx is None) or (not getattr(idx, 'isValid', lambda: False)()):
                # Best-effort: map editor geometry to an index
                try:
                    center = editor.geometry().center()
                    idx = self.indexAt(center)
                except Exception:
                    idx = None
            
            if idx and idx.isValid():
                # Use the effective delegate for this index (column-specific or base)
                delegate = None
                try:
                    delegate = self.itemDelegateForColumn(idx.column())
                except Exception:
                    delegate = None
                if delegate is None:
                    try:
                        delegate = self.itemDelegateForRow(idx.row())
                    except Exception:
                        pass
                if delegate is None:
                    try:
                        # Some bindings support itemDelegate(QModelIndex); ignore if not
                        delegate = self.itemDelegate(idx)
                    except Exception:
                        pass
                if delegate is None:
                    try:
                        delegate = self.itemDelegate()
                    except Exception:
                        delegate = None
                if delegate is None:
                    # Fallback to our base delegate or a vanilla one
                    delegate = getattr(self, "_base_delegate", None) or QStyledItemDelegate(self)
                try:
                    delegate.setModelData(editor, self.model(), idx)
                except Exception as e_set:
                    if debug_on:
                        print(f"[DEBUG] Manual setModelData failed: {e_set}")
            else:
                if debug_on:
                    print("[DEBUG] Could not resolve a valid index for manual commit; skipping setModelData")
            
            if debug_on:
                print(f"[DEBUG] Successfully committed editor {ename} on view {vname} (manual path)")
            return
                    
        except Exception as e:
            # Log the exception if debug is enabled
            try:
                if self.config_manager.get_setting("debug_mode_enabled", False):
                    vname = self.objectName() or f"CleanTableView@{id(self):x}"
                    print(f"[DEBUG] Exception in commitData ownership check on {vname}: {e}")
            except Exception:
                pass

    # --- Editing suppression helpers ---
    def temporarily_disable_editing(self, ms: int = 350):
        try:
            if self._saved_edit_triggers is None:
                self._saved_edit_triggers = self.editTriggers()
                self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                QTimer.singleShot(int(ms), self._restore_edit_triggers)
        except Exception:
            pass

    def _restore_edit_triggers(self):
        try:
            if self._saved_edit_triggers is not None:
                self.setEditTriggers(self._saved_edit_triggers)
                self._saved_edit_triggers = None
        except Exception:
            pass

    def _on_delegate_commit(self, editor):
        # Owning view check
        try:
            p = editor
            owns = False
            depth = 0
            while p is not None and depth < 8:
                if p is self or p is self.viewport():
                    owns = True
                    break
                p = p.parent()
                depth += 1
            if not owns:
                return
        except Exception:
            return
        
        try:
            debug_on = False
            try:
                debug_on = self.config_manager.get_setting("debug_mode_enabled", False)
            except Exception:
                debug_on = False
            if debug_on:
                vname = self.objectName() or f"CleanTableView@{id(self):x}"
                ename = editor.objectName() or editor.__class__.__name__
                print(f"[DEBUG] delegate.commitData on {vname}: editor={ename} ({editor.__class__.__name__})")
        except Exception:
            pass

    def _on_delegate_close(self, editor, hint):
        try:
            debug_on = False
            try:
                debug_on = self.config_manager.get_setting("debug_mode_enabled", False)
            except Exception:
                debug_on = False
            if debug_on:
                vname = self.objectName() or f"CleanTableView@{id(self):x}"
                ename = editor.objectName() or editor.__class__.__name__
                print(f"[DEBUG] delegate.closeEditor on {vname}: editor={ename} ({editor.__class__.__name__}), hint={int(hint)}")
        except Exception:
            pass

    # --- Internal helpers ---
    def _close_current_inline_editor(self):
        from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit
        editor_classes = (QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit)
        fw = QApplication.focusWidget()
        if fw is None:
            return
        # Ascend to find the top-level editor widget
        ed = fw
        top = None
        depth = 0
        while ed is not None and depth < 6:
            if isinstance(ed, editor_classes):
                top = ed
            ed = ed.parent()
            depth += 1
        if top is None:
            return
        # If inside an editable QComboBox, prefer the combobox as the editor
        if isinstance(top, QLineEdit):
            p = top.parent()
            if isinstance(p, QComboBox):
                top = p

        # Find the view that owns the editor
        owner_view = None
        for view in [self, self.frozen_column_view, self.frozen_row_view]:
            if view is None:
                continue
            
            p = top.parent()
            depth = 0
            is_owned = False
            while p is not None and depth < 8:
                if p is view or (hasattr(view, 'viewport') and p is view.viewport()):
                    is_owned = True
                    break
                p = p.parent()
                depth += 1
            
            if is_owned:
                owner_view = view
                break
        
        if owner_view:
            try:
                owner_view.closeEditor(top, QStyledItemDelegate.EndEditHint.SubmitModelCache)
            except Exception:
                pass

    def show_context_menu(self, position):
        # This method is unchanged
        index = self.indexAt(position)
        menu = QMenu(self)
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
        math_menu.addSeparator()
        conditional_action = QAction("Conditional…", self)
        conditional_action.triggered.connect(self._prompt_conditional_math)
        math_menu.addAction(conditional_action)
        menu.addSeparator()
        insert_row_above_action = QAction("Insert Row &Above", self)
        insert_row_above_action.triggered.connect(self.insert_row_above_requested.emit)
        menu.addAction(insert_row_above_action)
        insert_row_below_action = QAction("Insert Row &Below", self)
        insert_row_below_action.triggered.connect(self.insert_row_below_requested.emit)
        menu.addAction(insert_row_below_action)
        insert_rows_above_action = QAction("Insert &Rows Above…", self)
        insert_rows_above_action.triggered.connect(lambda: self._prompt_insert_rows(True))
        menu.addAction(insert_rows_above_action)
        insert_rows_below_action = QAction("Insert R&ows Below…", self)
        insert_rows_below_action.triggered.connect(lambda: self._prompt_insert_rows(False))
        menu.addAction(insert_rows_below_action)
        delete_row_action = QAction("&Delete Row", self)
        delete_row_action.triggered.connect(self.delete_row_requested.emit)
        menu.addAction(delete_row_action)
        menu.addSeparator()
        insert_column_left_action = QAction("Insert Column &Left", self)
        insert_column_left_action.triggered.connect(self.insert_column_left_requested.emit)
        menu.addAction(insert_column_left_action)
        insert_column_right_action = QAction("Insert Column &Right", self)
        insert_column_right_action.triggered.connect(self.insert_column_right_requested.emit)
        menu.addAction(insert_column_right_action)
        insert_columns_left_action = QAction("Insert C&olumns Left…", self)
        insert_columns_left_action.triggered.connect(lambda: self._prompt_insert_columns(True))
        menu.addAction(insert_columns_left_action)
        insert_columns_right_action = QAction("Insert Co&lumns Right…", self)
        insert_columns_right_action.triggered.connect(lambda: self._prompt_insert_columns(False))
        menu.addAction(insert_columns_right_action)
        delete_column_action = QAction("Delete &Column", self)
        delete_column_action.triggered.connect(self.delete_column_requested.emit)
        menu.addAction(delete_column_action)
        has_selection = len(self.selectedIndexes()) > 0
        clipboard = QApplication.clipboard()
        has_clipboard_data = clipboard.mimeData().hasText()
        copy_action.setEnabled(has_selection)
        cut_action.setEnabled(has_selection)
        paste_action.setEnabled(has_clipboard_data)
        clear_action.setEnabled(has_selection)
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
        # Enable/disable only simple math actions based on numeric selection; keep Conditional always enabled
        multiply_action.setEnabled(can_do_math)
        divide_action.setEnabled(can_do_math)
        add_action.setEnabled(can_do_math)
        subtract_action.setEnabled(can_do_math)
        increment_action.setEnabled(can_do_math)
        decrement_action.setEnabled(can_do_math)
        has_valid_selection = index.isValid()
        select_row_action.setEnabled(has_valid_selection)
        select_column_action.setEnabled(has_valid_selection)
        insert_row_above_action.setEnabled(has_valid_selection)
        insert_row_below_action.setEnabled(has_valid_selection)
        insert_rows_above_action.setEnabled(has_valid_selection)
        insert_rows_below_action.setEnabled(has_valid_selection)
        delete_row_action.setEnabled(has_valid_selection)
        insert_column_left_action.setEnabled(has_valid_selection)
        insert_column_right_action.setEnabled(has_valid_selection)
        insert_columns_left_action.setEnabled(has_valid_selection)
        insert_columns_right_action.setEnabled(has_valid_selection)
        delete_column_action.setEnabled(has_valid_selection)
        menu.exec(self.mapToGlobal(position))

    def _prompt_insert_rows(self, above: bool):
        count, ok = QInputDialog.getInt(self, "Insert Rows", "Number of rows:", 5, 1, 10000, 1)
        if not ok:
            return
        if above:
            self.insert_rows_above_requested.emit(count)
        else:
            self.insert_rows_below_requested.emit(count)

    def _prompt_insert_columns(self, left: bool):
        count, ok = QInputDialog.getInt(self, "Insert Columns", "Number of columns:", 2, 1, 500, 1)
        if not ok:
            return
        if left:
            self.insert_columns_left_requested.emit(count)
        else:
            self.insert_columns_right_requested.emit(count)

    def _prompt_conditional_math(self):
        # 1) Condition input
        text, ok = QInputDialog.getText(self, "Conditional Math", "Condition (e.g., primeevil == 1):")
        if not ok or not text.strip():
            return
        condition_str = text.strip()

        # 2) Operation choice
        operations = ["multiply", "divide", "add", "subtract", "increment", "decrement"]
        op, ok = QInputDialog.getItem(self, "Operation", "Choose operation:", operations, 0, False)
        if not ok:
            return

        operand = None
        if op not in ("increment", "decrement"):
            val, ok = QInputDialog.getDouble(self, op.capitalize(), f"Enter value to {op}:")
            if not ok:
                return
            operand = val

        # 3) Target columns
        selected_cols = sorted({idx.column() for idx in self.selectedIndexes()})
        use_sel = False
        if selected_cols:
            reply = QMessageBox.question(self, "Target Columns", "Apply to currently selected columns?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.Yes)
            use_sel = reply == QMessageBox.StandardButton.Yes

        target_columns = []
        if use_sel:
            target_columns = selected_cols
        else:
            # Build comma-separated prompt of columns
            model = self.model()
            # Prefer header items; fallback to headerData with DisplayRole
            headers = []
            for c in range(model.columnCount()):
                header_item = model.horizontalHeaderItem(c)
                if header_item is not None and header_item.text() is not None:
                    headers.append(header_item.text())
                else:
                    try:
                        headers.append(str(model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)))
                    except Exception:
                        headers.append(str(c))
            default_cols = ", ".join([h for h in headers if isinstance(h, str)][:2])
            cols_str, ok = QInputDialog.getText(self, "Target Columns", "Column names (comma separated):", text=default_cols)
            if not ok or not cols_str.strip():
                return
            requested = [c.strip() for c in cols_str.split(',') if c.strip()]
            name_to_index = {str(headers[i]): i for i in range(len(headers))}
            missing = [c for c in requested if c not in name_to_index]
            if missing:
                QMessageBox.warning(self, "Unknown Columns", f"Columns not found: {', '.join(missing)}")
                return
            target_columns = [name_to_index[c] for c in requested]

        payload = {
            "condition": condition_str,
            "operation": op,
            "operand": operand,
            "target_columns": target_columns,
        }
        # Minimal debug output to help trace selection -> payload mapping
        try:
            from config_manager import ConfigManager as _Cfg
            if _Cfg().get_setting("debug_mode_enabled", False):
                print("[DEBUG] Conditional prompt payload:", payload)
        except Exception:
            pass
        self.conditional_math_requested.emit(payload)
