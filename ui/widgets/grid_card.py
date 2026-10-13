import requests
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage
from typing import Dict, Any
from ..icon_helper import get_svg_icon

class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(bytes)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        if not self.url:
            return
        try:
            resp = requests.get(self.url, timeout=5)
            if resp.ok and len(resp.content) > 100:
                self.image_loaded.emit(resp.content)
        except Exception:
            pass

class SongCard(QFrame):
    download_requested = pyqtSignal(dict) # meta
    selection_changed = pyqtSignal(bool)

    def __init__(self, meta: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.meta = dict(meta)
        self.setFixedSize(160, 225)
        self.setProperty("class", "CardWidget")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_ui()
        self._load_cover()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 10)
        layout.setSpacing(6)

        # 1. Square Artwork Container (144x144, radius 8px)
        self.cover_label = QLabel(self)
        self.cover_label.setFixedSize(144, 144)
        self.cover_label.setStyleSheet("background-color: #22201D; border-radius: 8px;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("🎵")
        layout.addWidget(self.cover_label)

        # 2. Track Title (Space Grotesk)
        self.title_label = QLabel(self.meta.get("title", "Unknown Title"), self)
        self.title_label.setStyleSheet("""
            color: #F5F0EC;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
        """)
        self.title_label.setWordWrap(False)
        layout.addWidget(self.title_label)

        # 3. Bottom Row: Artist + Checkbox + Quick Download
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(4)

        self.artist_label = QLabel(self.meta.get("artist", "Unknown Artist"), self)
        self.artist_label.setStyleSheet("""
            color: #A8A49E;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 11px;
        """)
        bottom_row.addWidget(self.artist_label, stretch=1)

        # Selection Checkbox
        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(lambda chk: self.selection_changed.emit(chk))
        bottom_row.addWidget(self.checkbox)

        # Download Icon Button
        self.dl_btn = QPushButton(self)
        self.dl_btn.setFixedSize(26, 26)
        self.dl_btn.setIcon(get_svg_icon("arrow-down", 14, "#FFFFFF"))
        self.dl_btn.setStyleSheet("""
            QPushButton {
                background-color: #C23B30;
                border: none;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #D64337;
            }
        """)
        self.dl_btn.clicked.connect(lambda: self.download_requested.emit(self.meta))
        bottom_row.addWidget(self.dl_btn)

        layout.addLayout(bottom_row)

    def _load_cover(self):
        cover_url = self.meta.get("cover_url", "")
        if not cover_url:
            return
        self.loader = ImageLoaderThread(cover_url, self)
        self.loader.image_loaded.connect(self._on_image_loaded)
        self.loader.start()

    def _on_image_loaded(self, data: bytes):
        img = QImage.fromData(data)
        if not img.isNull():
            pix = QPixmap.fromImage(img).scaled(
                144, 144,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(pix)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def set_selected(self, selected: bool):
        self.checkbox.setChecked(selected)
