import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon
from .pages.search_page import SearchPage
from .pages.queue_page import QueuePage
from .pages.library_page import LibraryPage
from .pages.settings_page import SettingsPage
from .widgets.nav_rail import NavRail
from .widgets.top_bar import TopBar
from .widgets.player_bar import PlayerBar
from core.downloader.queue_manager import QueueManager
from core.audio_player import PreviewPlayer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CassetteCat Downloader")
        self.resize(1200, 800)
        self.setMinimumSize(960, 640)

        # Frameless window matching CassetteCat Main.qml
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # App Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "cassettecat_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.queue_manager = QueueManager(self)
        self.player = PreviewPlayer.get_instance()
        self._drag_pos = QPoint()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_vbox = QVBoxLayout(central)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # Content Row (NavRail + Pages Area)
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        # 1. 56px NavRail on the far left
        self.nav_rail = NavRail(self)
        self.nav_rail.page_changed.connect(self._set_page)
        content_row.addWidget(self.nav_rail)

        # 2. Right Main View Column (TopBar + Stacked Pages)
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(0)

        # TopBar
        self.top_bar = TopBar(self)
        self.top_bar.minimize_clicked.connect(self.showMinimized)
        self.top_bar.maximize_clicked.connect(self._toggle_maximize)
        self.top_bar.close_clicked.connect(self.close)
        right_col.addWidget(self.top_bar)

        # Stacked Pages
        self.stack = QStackedWidget(self)
        self.search_page = SearchPage(self)
        self.queue_page = QueuePage(self)
        self.library_page = LibraryPage(self)
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.queue_page)
        self.stack.addWidget(self.library_page)
        self.stack.addWidget(self.settings_page)

        right_col.addWidget(self.stack, stretch=1)
        content_row.addLayout(right_col, stretch=1)

        main_vbox.addLayout(content_row, stretch=1)

        # 3. Bottom Player Dock (surfaceDock #151412)
        self.player_bar = PlayerBar(self)
        main_vbox.addWidget(self.player_bar)

    def _set_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self.nav_rail.set_active_index(index)

        titles = ["Explore", "Download Queue", "Library", "Settings"]
        if 0 <= index < len(titles):
            self.top_bar.set_title(titles[index])

        if index == 2:
            self.library_page.scan_library()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # Window dragging for frameless title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 48:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint()

    def _connect_signals(self):
        # Search page -> Queue
        self.search_page.download_requested.connect(self._on_download_requested)

        # Queue manager -> Queue page
        self.queue_manager.job_added.connect(self.queue_page.add_job)
        self.queue_manager.job_progress.connect(self.queue_page.update_job_progress)
        self.queue_manager.job_finished.connect(self._on_job_finished)
        self.queue_manager.job_error.connect(self.queue_page.mark_job_error)

        # Queue page actions
        self.queue_page.cancel_job_requested.connect(self.queue_manager.cancel_job)
        self.queue_page.cancel_all_requested.connect(self.queue_manager.cancel_all)
        self.queue_page.play_requested.connect(self.player.play_file)

        # Library page play action
        self.library_page.play_requested.connect(self.player.play_file)

    def _on_download_requested(self, tracks: list):
        self.queue_manager.add_tracks(tracks)
        self._set_page(1)

    def _on_job_finished(self, job_id: str, file_path: str, meta: dict):
        self.queue_page.mark_job_completed(job_id, file_path)
