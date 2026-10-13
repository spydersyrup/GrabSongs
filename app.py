import sys
import os

# Add root folder to sys.path so core and ui imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from ui.styles import THEME_DARK

def main():
    # Enable High DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("Harmonix")
    app.setOrganizationName("HarmonixMusic")

    # Apply modern dark styling
    app.setStyleSheet(THEME_DARK)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
