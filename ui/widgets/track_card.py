import requests
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage
from typing import Dict, Any
from .badge import ServiceBadge

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

class TrackCard(QFrame):
    download_requested = pyqtSignal(dict) # metadata
    selection_changed = pyqtSignal(bool)

    def __init__(self, meta: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.meta = dict(meta)
        self.setProperty("class", "CardWidget")
        self.setFixedHeight(68)

        self._setup_ui()
        self._load_cover()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 14, 8)
        layout.setSpacing(14)

        # Selection Checkbox
        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(lambda chk: self.selection_changed.emit(chk))
        layout.addWidget(self.checkbox)

        # Cover Thumbnail
        self.cover_label = QLabel(self)
        self.cover_label.setFixedSize(50, 50)
        self.cover_label.setStyleSheet("background-color: #22201D; border-radius: 8px;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cover_label)

        # Track Info (Title, Artist, Album)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel(self.meta.get("title", "Unknown Title"), self)
        self.title_label.setStyleSheet("""
            color: #F5F0EC;
            font-family: 'Space Grotesk', 'IBM Plex Sans', sans-serif;
            font-size: 13px;
            font-weight: 600;
        """)
        info_layout.addWidget(self.title_label)

        details_text = f"{self.meta.get('artist', 'Unknown Artist')} • {self.meta.get('album', '')}"
        self.details_label = QLabel(details_text, self)
        self.details_label.setStyleSheet("""
            color: #A8A49E;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 11px;
        """)
        info_layout.addWidget(self.details_label)

        layout.addLayout(info_layout, stretch=1)

        # Duration in IBM Plex Mono
        dur_sec = self.meta.get("duration", 0)
        dur_str = f"{int(dur_sec // 60)}:{int(dur_sec % 60):02d}" if dur_sec > 0 else ""
        if dur_str:
            self.dur_label = QLabel(dur_str, self)
            self.dur_label.setStyleSheet("""
                color: #918E88;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 11px;
                font-weight: 500;
            """)
            layout.addWidget(self.dur_label)

        # Service Badge
        service = self.meta.get("service", "search")
        self.badge = ServiceBadge(service, self)
        layout.addWidget(self.badge)

        # Download Button
        self.dl_btn = QPushButton("Download", self)
        self.dl_btn.setProperty("class", "PrimaryButton")
        self.dl_btn.setFixedSize(92, 32)
        self.dl_btn.clicked.connect(lambda: self.download_requested.emit(self.meta))
        layout.addWidget(self.dl_btn)

    def _load_cover(self):
        cover_url = self.meta.get("cover_url", "")
        if not cover_url:
            self.cover_label.setText("🎵")
            return

        self.loader_thread = ImageLoaderThread(cover_url, self)
        self.loader_thread.image_loaded.connect(self._on_image_loaded)
        self.loader_thread.start()

    def _on_image_loaded(self, img_bytes: bytes):
        img = QImage.fromData(img_bytes)
        if not img.isNull():
            pix = QPixmap.fromImage(img).scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(pix)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def set_selected(self, selected: bool):
        self.checkbox.setChecked(selected)
