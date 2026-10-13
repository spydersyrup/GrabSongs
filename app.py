import sys
import os

# Add root folder to sys.path so core and ui imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure attachment to interactive desktop on Windows
if sys.platform == "win32":
    try:
        import ctypes
        user32 = ctypes.windll.user32
        h_winsta = user32.OpenWindowStationW("WinSta0", False, 0x10000000)
        if h_winsta:
            user32.SetProcessWindowStation(h_winsta)
        h_desk = user32.OpenDesktopW("Default", 0, False, 0x10000000)
        if h_desk:
            user32.SetThreadDesktop(h_desk)
    except Exception:
        pass

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
    window.raise_()
    window.activateWindow()

    print("Harmonix GUI initialized and running.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
