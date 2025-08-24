import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
from ui import EditorWindow

def main():
    # Suppress noisy Qt logs (e.g., QWidget::paintEngine warnings)
    os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false")

    def _qt_message_filter(mode, context, message):
        # Filter specific noisy warnings
        if "QWidget::paintEngine: Should no longer be called" in message:
            return
        # Forward other messages (skip debug-level to reduce noise)
        if mode == QtMsgType.QtDebugMsg:
            return
        try:
            sys.__stderr__.write(message + "\n")
        except Exception:
            pass

    qInstallMessageHandler(_qt_message_filter)
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.setWindowTitle("Diablo II .txt Editor")
    window.setGeometry(100, 100, 1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
