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
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from ui.styles import THEME_CASSETTECAT

def load_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                full_path = os.path.join(fonts_dir, font_file)
                QFontDatabase.addApplicationFont(full_path)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CassetteCat Downloader")
    app.setOrganizationName("CassetteCat")

    # Set Window Icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cassettecat_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Load CassetteCat typography (Space Grotesk, IBM Plex Sans, IBM Plex Mono)
    load_fonts()

    # Set IBM Plex Sans as the default body font
    default_font = QFont("IBM Plex Sans", 10)
    app.setFont(default_font)

    # Apply CassetteCat Visual System Stylesheet
    app.setStyleSheet(THEME_CASSETTECAT)

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    print("CassetteCat Downloader initialized and running.", flush=True)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
