from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from .pages.search_page import SearchPage
from .pages.queue_page import QueuePage
from .pages.library_page import LibraryPage
from .pages.settings_page import SettingsPage
from .widgets.player_bar import PlayerBar
from core.downloader.queue_manager import QueueManager
from core.audio_player import PreviewPlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harmonix — Unified Multi-Platform Music Downloader")
        self.resize(1180, 780)
        self.setMinimumSize(940, 620)

        self.queue_manager = QueueManager(self)
        self.player = PreviewPlayer.get_instance()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_vbox = QVBoxLayout(central)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # Top area: Sidebar + Pages
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame(self)
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 20)
        sidebar_layout.setSpacing(12)

        # Logo and Title
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)
        app_title = QLabel("HARMONIX", sidebar)
        app_title.setObjectName("AppTitle")
        brand_layout.addWidget(app_title)

        app_sub = QLabel("Universal Music Downloader", sidebar)
        app_sub.setObjectName("AppSubtitle")
        brand_layout.addWidget(app_sub)
        sidebar_layout.addLayout(brand_layout)

        sidebar_layout.addSpacing(16)

        # Nav Buttons
        self.btn_search = QPushButton("🔍  Explore & Search", sidebar)
        self.btn_search.setProperty("class", "NavButton")
        self.btn_search.setCheckable(True)
        self.btn_search.setChecked(True)
        self.btn_search.clicked.connect(lambda: self._set_page(0))
        sidebar_layout.addWidget(self.btn_search)

        self.btn_queue = QPushButton("📥  Queue (0)", sidebar)
        self.btn_queue.setProperty("class", "NavButton")
        self.btn_queue.setCheckable(True)
        self.btn_queue.clicked.connect(lambda: self._set_page(1))
        sidebar_layout.addWidget(self.btn_queue)

        self.btn_library = QPushButton("🎵  Library", sidebar)
        self.btn_library.setProperty("class", "NavButton")
        self.btn_library.setCheckable(True)
        self.btn_library.clicked.connect(lambda: self._set_page(2))
        sidebar_layout.addWidget(self.btn_library)

        self.btn_settings = QPushButton("⚙️  Settings", sidebar)
        self.btn_settings.setProperty("class", "NavButton")
        self.btn_settings.setCheckable(True)
        self.btn_settings.clicked.connect(lambda: self._set_page(3))
        sidebar_layout.addWidget(self.btn_settings)

        sidebar_layout.addStretch(1)

        # Footer info
        version_lbl = QLabel("v1.0.0 • Freyr + Apmyx Core", sidebar)
        version_lbl.setStyleSheet("color: #555566; font-size: 11px;")
        sidebar_layout.addWidget(version_lbl)

        content_row.addWidget(sidebar)

        # 2. Stacked Pages
        self.stack = QStackedWidget(self)

        self.search_page = SearchPage(self)
        self.queue_page = QueuePage(self)
        self.library_page = LibraryPage(self)
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.queue_page)
        self.stack.addWidget(self.library_page)
        self.stack.addWidget(self.settings_page)

        content_row.addWidget(self.stack, stretch=1)
        main_vbox.addLayout(content_row, stretch=1)

        # 3. Bottom Audio Player Bar
        self.player_bar = PlayerBar(self)
        main_vbox.addWidget(self.player_bar)

    def _set_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_search.setChecked(index == 0)
        self.btn_queue.setChecked(index == 1)
        self.btn_library.setChecked(index == 2)
        self.btn_settings.setChecked(index == 3)

        if index == 2:
            self.library_page.scan_library()

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
        # Update queue button label and switch to queue view
        self._update_queue_label()
        self._set_page(1)

    def _on_job_finished(self, job_id: str, file_path: str, meta: dict):
        self.queue_page.mark_job_completed(job_id, file_path)
        self._update_queue_label()

    def _update_queue_label(self):
        active_count = len(self.queue_manager.active_workers) + len(self.queue_manager.queue)
        self.btn_queue.setText(f"📥  Queue ({active_count})")
