import os
import sys

# Ensure Basic style for QtQuick Controls (exact style used by CassetteCat Desktop)
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

log_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_debug.log"), "w", encoding="utf-8", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

def handle_exception(exc_type, exc_value, exc_traceback):
    import traceback
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=log_file)
    log_file.flush()

sys.excepthook = handle_exception

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon, QFont
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, QCoreApplication

from bridge import (
    PyCoverImageProvider, SettingsBridge, LibraryBridge, PlayerBridge,
    ServicesBridge, StreamingBridge, WindowFrameBridge, TrayBridge,
    PhoneRemoteBridge, GlobalShortcutsBridge, MprisBridge, SmtcBridge,
    DiscordBridge, DownloaderBridge
)

def load_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
    display_family = "Space Grotesk"
    body_family = "IBM Plex Sans"
    mono_family = "IBM Plex Mono"

    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                full_path = os.path.join(fonts_dir, font_file)
                QFontDatabase.addApplicationFont(full_path)

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
    app.setQuitOnLastWindowClosed(False)
    QCoreApplication.setApplicationName("GrabSongs")
    QCoreApplication.setOrganizationName("GrabSongs")

    # Set Window Icon (.ico has all resolutions for Windows taskbar)
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cassettecat_icon.ico")
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "cassettecat_icon.png")
    icon_path = ico_path if os.path.exists(ico_path) else png_path
    app_icon = None
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    display_family, body_family, mono_family = load_fonts()
    app.setFont(QFont(display_family))

    # Initialize Engine & Provider
    engine = QQmlApplicationEngine()
    engine.addImageProvider("cover", PyCoverImageProvider())

    qml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml")
    engine.addImportPath(qml_dir)

    # Instantiate Bridges
    settings_bridge = SettingsBridge()
    library_bridge = LibraryBridge()
    player_bridge = PlayerBridge()
    services_bridge = ServicesBridge()
    streaming_bridge = StreamingBridge()
    window_frame_bridge = WindowFrameBridge()
    tray_bridge = TrayBridge()
    phone_remote_bridge = PhoneRemoteBridge()
    global_shortcuts_bridge = GlobalShortcutsBridge()
    mpris_bridge = MprisBridge()
    smtc_bridge = SmtcBridge()
    discord_bridge = DiscordBridge()
    downloader_bridge = DownloaderBridge(library_bridge)

    # Register Context Properties
    ctx = engine.rootContext()
    ctx.setContextProperty("displayFontFamily", display_family)
    ctx.setContextProperty("bodyFontFamily", body_family)
    ctx.setContextProperty("monoFontFamily", mono_family)
    ctx.setContextProperty("installedFromStore", False)

    ctx.setContextProperty("appSettings", settings_bridge)
    ctx.setContextProperty("library", library_bridge)
    ctx.setContextProperty("player", player_bridge)
    ctx.setContextProperty("services", services_bridge)
    ctx.setContextProperty("streaming", streaming_bridge)
    ctx.setContextProperty("windowFrame", window_frame_bridge)
    ctx.setContextProperty("tray", tray_bridge)
    ctx.setContextProperty("phoneRemote", phone_remote_bridge)
    ctx.setContextProperty("globalShortcuts", global_shortcuts_bridge)
    ctx.setContextProperty("mpris", mpris_bridge)
    ctx.setContextProperty("smtc", smtc_bridge)
    ctx.setContextProperty("discord", discord_bridge)
    ctx.setContextProperty("downloader", downloader_bridge)
    ctx.setContextProperty("appIconUrl", QUrl.fromLocalFile(png_path).toString() if os.path.exists(png_path) else "")

    engine.warnings.connect(lambda warns: [print("QML Warning:", w.toString()) for w in warns])

    main_qml = os.path.join(qml_dir, "GrabSongsMain.qml")
    engine.load(QUrl.fromLocalFile(main_qml))

    if not engine.rootObjects():
        print("FATAL: QML root objects is empty! Check warnings above.", file=sys.stderr)
        sys.exit(1)

    root = engine.rootObjects()[0]
    print(f"ROOT OBJECT: {root}", flush=True)
    print(f"ROOT SIZE: {root.width()}x{root.height()}, VISIBLE: {root.isVisible()}, WINID: {int(root.winId())}", flush=True)
    if app_icon:
        root.setIcon(app_icon)
    root.show()
    root.raise_()
    root.requestActivate()
    print(f"AFTER SHOW VISIBLE: {root.isVisible()}, WINID: {int(root.winId())}", flush=True)

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

    print("CassetteCat initialized and running.", flush=True)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
