import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.config import AppConfig

class LibraryPage(QWidget):
    play_requested = pyqtSignal(str, str, str) # file_path, title, artist

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(18)

        # Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title_label = QLabel("Library & Local Files", self)
        title_label.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #F5F0EC;
            letter-spacing: -0.3px;
        """)
        title_layout.addWidget(title_label)

        self.subtitle_label = QLabel("Downloaded audio catalog", self)
        self.subtitle_label.setStyleSheet("""
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            color: #A8A49E;
        """)
        title_layout.addWidget(self.subtitle_label)

        header_row.addLayout(title_layout, stretch=1)

        # Buttons
        refresh_btn = QPushButton("🔄 Refresh", self)
        refresh_btn.setProperty("class", "SecondaryButton")
        refresh_btn.clicked.connect(self.scan_library)
        header_row.addWidget(refresh_btn)

        open_folder_btn = QPushButton("📁 Open Folder", self)
        open_folder_btn.setProperty("class", "PrimaryButton")
        open_folder_btn.clicked.connect(self._open_download_folder)
        header_row.addWidget(open_folder_btn)

        layout.addLayout(header_row)

        # Scrollable items area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(6)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area, stretch=1)

        self.scan_library()

    def scan_library(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        download_dir = AppConfig.get_instance().get("download_dir", "")
        if not download_dir or not os.path.exists(download_dir):
            self._show_empty_state("Download folder does not exist.")
            return

        supported_exts = {".mp3", ".m4a", ".flac", ".opus", ".wav"}
        files = []
        try:
            for root, _, filenames in os.walk(download_dir):
                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in supported_exts:
                        full_path = os.path.join(root, f)
                        files.append((f, full_path, os.path.getsize(full_path)))
        except Exception as e:
            print(f"[Library] Scan error: {e}")

        if not files:
            self._show_empty_state("No downloaded tracks found yet.")
            return

        self.subtitle_label.setText(f"{len(files)} downloaded tracks found")

        for fname, fpath, fsize in sorted(files, key=lambda x: x[0]):
            row_card = QFrame(self.container)
            row_card.setProperty("class", "CardWidget")
            row_card.setFixedHeight(54)
            row_layout = QHBoxLayout(row_card)
            row_layout.setContentsMargins(14, 6, 14, 6)
            row_layout.setSpacing(12)

            icon_lbl = QLabel("🎵", row_card)
            icon_lbl.setStyleSheet("font-size: 15px;")
            row_layout.addWidget(icon_lbl)

            name_without_ext = os.path.splitext(fname)[0]
            name_lbl = QLabel(name_without_ext, row_card)
            name_lbl.setStyleSheet("""
                color: #F5F0EC;
                font-family: 'Space Grotesk', 'IBM Plex Sans', sans-serif;
                font-size: 13px;
                font-weight: 500;
            """)
            row_layout.addWidget(name_lbl, stretch=1)

            size_mb = f"{fsize / 1024 / 1024:.1f} MB"
            size_lbl = QLabel(size_mb, row_card)
            size_lbl.setStyleSheet("""
                color: #918E88;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 11px;
            """)
            row_layout.addWidget(size_lbl)

            # Play Button
            play_btn = QPushButton("▶ Play", row_card)
            play_btn.setProperty("class", "PrimaryButton")
            play_btn.setFixedSize(68, 28)
            play_btn.clicked.connect(lambda _, p=fpath, n=name_without_ext: self.play_requested.emit(p, n, ""))
            row_layout.addWidget(play_btn)

            # Reveal Button
            reveal_btn = QPushButton("📂", row_card)
            reveal_btn.setProperty("class", "SecondaryButton")
            reveal_btn.setFixedSize(34, 28)
            reveal_btn.setToolTip("Show in Explorer")
            reveal_btn.clicked.connect(lambda _, p=fpath: self._reveal_file(p))
            row_layout.addWidget(reveal_btn)

            self.items_layout.addWidget(row_card)

    def _show_empty_state(self, message: str):
        self.subtitle_label.setText("0 downloaded tracks found")
        empty_box = QFrame(self.container)
        empty_box.setProperty("class", "CardWidget")
        empty_layout = QVBoxLayout(empty_box)
        empty_layout.setContentsMargins(40, 50, 40, 50)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(12)

        icon_lbl = QLabel("📁", empty_box)
        icon_lbl.setStyleSheet("font-size: 38px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_lbl)

        title_lbl = QLabel("No Music Files Found", empty_box)
        title_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #F5F0EC;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title_lbl)

        desc_lbl = QLabel(message, empty_box)
        desc_lbl.setStyleSheet("""
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 12px;
            color: #A8A49E;
        """)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_lbl)

        self.items_layout.addWidget(empty_box)

    def _open_download_folder(self):
        download_dir = AppConfig.get_instance().get("download_dir", "")
        if download_dir and os.path.exists(download_dir):
            if os.name == 'nt':
                os.startfile(download_dir)
            else:
                subprocess.Popen(['xdg-open', download_dir])

    def _reveal_file(self, file_path: str):
        if os.name == 'nt':
            subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
        else:
            subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
