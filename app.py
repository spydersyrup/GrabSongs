import os
import sys

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon, QFont
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, QCoreApplication

from bridge import PyCoverImageProvider, DownloaderBridge


def load_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
    display_family = "IBM Plex Sans"
    body_family = "IBM Plex Sans"
    mono_family = "IBM Plex Mono"

    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith((".ttf", ".otf")):
                full_path = os.path.join(fonts_dir, font_file)
                QFontDatabase.addApplicationFont(full_path)

    families = QFontDatabase.families()
    if "IBM Plex Sans" not in families:
        display_family = "Adwaita Sans" if "Adwaita Sans" in families else "DejaVu Sans"
        body_family = display_family
    if "IBM Plex Mono" not in families:
        mono_family = "Fira Code" if "Fira Code" in families else "monospace"

    return display_family, body_family, mono_family


def main():
    if sys.platform == "win32":
        import ctypes
        app_user_model_id = "GrabSongs.AudioEngine.Desktop.App"
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_user_model_id)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    QCoreApplication.setApplicationName("GrabSongs")
    QCoreApplication.setOrganizationName("GrabSongs")

    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "grabsongs_icon.ico")
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "grabsongs_icon.png")
    icon_path = ico_path if os.path.exists(ico_path) else png_path
    app_icon = None
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    display_family, body_family, mono_family = load_fonts()
    app.setFont(QFont(display_family))

    engine = QQmlApplicationEngine()
    engine.addImageProvider("cover", PyCoverImageProvider())

    qml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml")
    engine.addImportPath(qml_dir)

    downloader_bridge = DownloaderBridge()

    ctx = engine.rootContext()
    ctx.setContextProperty("displayFontFamily", display_family)
    ctx.setContextProperty("bodyFontFamily", body_family)
    ctx.setContextProperty("monoFontFamily", mono_family)
    ctx.setContextProperty("installedFromStore", False)
    ctx.setContextProperty("downloader", downloader_bridge)
    ctx.setContextProperty("appIconUrl", QUrl.fromLocalFile(png_path).toString() if os.path.exists(png_path) else "")

    engine.warnings.connect(lambda warns: [print("QML Warning:", w.toString()) for w in warns])

    main_qml = os.path.join(qml_dir, "GrabSongsMain.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("FATAL: QML root objects is empty! Check warnings above.", file=sys.stderr)
        sys.exit(1)

    root = engine.rootObjects()[0]
    if app_icon:
        root.setIcon(app_icon)
    root.show()
    root.raise_()
    root.requestActivate()

    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = int(root.winId())
            if os.path.exists(ico_path):
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x0010
                WM_SETICON = 0x0080
                hicon_big = ctypes.windll.user32.LoadImageW(0, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                hicon_small = ctypes.windll.user32.LoadImageW(0, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                if hicon_big:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)
                if hicon_small:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_small)
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            ctypes.windll.user32.BringWindowToTop(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    print("GrabSongs initialized and running.", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
