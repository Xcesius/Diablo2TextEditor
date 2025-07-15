import sys
from PyQt6.QtWidgets import QApplication
from ui import EditorWindow

def main():
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.setWindowTitle("Diablo II .txt Editor")
    window.setGeometry(100, 100, 1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 