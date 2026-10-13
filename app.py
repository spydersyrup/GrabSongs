import sys
import os

# Ensure Basic style for QtQuick Controls (exact style used by CassetteCat Desktop)
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"

# Add root folder to sys.path so core and ui imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

from bridge import PlayerBridge, DownloaderBridge

def load_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                full_path = os.path.join(fonts_dir, font_file)
                QFontDatabase.addApplicationFont(full_path)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Harmonix • CassetteCat Downloader")
    app.setOrganizationName("CassetteCat")

    # Set Window Icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cassettecat_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Load CassetteCat typography (Space Grotesk, IBM Plex Sans, IBM Plex Mono)
    load_fonts()

    # Create backend bridges
    player_bridge = PlayerBridge()
    downloader_bridge = DownloaderBridge(player_bridge)

    # Initialize QML Application Engine
    engine = QQmlApplicationEngine()
    qml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml")
    engine.addImportPath(qml_dir)

    # Register bridge context properties
    engine.rootContext().setContextProperty("player", player_bridge)
    engine.rootContext().setContextProperty("bridge", downloader_bridge)

    engine.warnings.connect(lambda warns: [print("QML Warning:", w.toString()) for w in warns])

    main_qml = os.path.join(qml_dir, "Main.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("FATAL: QML root objects is empty! Check warnings above.", file=sys.stderr)
        sys.exit(1)

    root = engine.rootObjects()[0]
    root.show()
    root.raise_()
    root.requestActivate()

    try:
        import ctypes
        ctypes.windll.user32.SetForegroundWindow(int(root.winId()))
    except Exception:
        pass

    print("Harmonix CassetteCat QML Downloader initialized and running.", flush=True)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
