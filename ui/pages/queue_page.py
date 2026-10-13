import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any
from ..widgets.queue_item import QueueItemWidget
from core.config import AppConfig


class QueuePage(QWidget):
    cancel_job_requested = pyqtSignal(str) # job_id
    cancel_all_requested = pyqtSignal()
    play_requested = pyqtSignal(str, str, str) # file_path, title, artist

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_widgets: Dict[str, QueueItemWidget] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(18)

        # Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title_label = QLabel("Download Queue", self)
        title_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        title_layout.addWidget(title_label)

        self.subtitle_label = QLabel("0 active jobs", self)
        self.subtitle_label.setStyleSheet("font-size: 13px; color: #8C8C9E;")
        title_layout.addWidget(self.subtitle_label)

        header_row.addLayout(title_layout, stretch=1)

        # Action Buttons
        self.open_folder_btn = QPushButton("📁 Open Folder", self)
        self.open_folder_btn.setProperty("class", "SecondaryButton")
        self.open_folder_btn.clicked.connect(self._open_download_folder)
        header_row.addWidget(self.open_folder_btn)

        self.cancel_all_btn = QPushButton("✕ Cancel All", self)
        self.cancel_all_btn.setProperty("class", "DangerButton")
        self.cancel_all_btn.clicked.connect(self.cancel_all_requested.emit)
        header_row.addWidget(self.cancel_all_btn)

        layout.addLayout(header_row)

        # Scrollable items area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(10)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area, stretch=1)

        self._show_empty_state()

    def _show_empty_state(self):
        empty_box = QFrame(self.container)
        empty_box.setProperty("class", "CardWidget")
        empty_layout = QVBoxLayout(empty_box)
        empty_layout.setContentsMargins(40, 50, 40, 50)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(12)

        icon_lbl = QLabel("📥", empty_box)
        icon_lbl.setStyleSheet("font-size: 40px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_lbl)

        title_lbl = QLabel("Queue is Empty", empty_box)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFFFFF;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title_lbl)

        desc_lbl = QLabel("Search and add tracks to begin downloading.", empty_box)
        desc_lbl.setStyleSheet("font-size: 12px; color: #8C8C9E;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_lbl)

        self.items_layout.addWidget(empty_box)

    def add_job(self, job_id: str, meta: Dict[str, Any]):
        # Clear empty state if present
        if len(self.item_widgets) == 0:
            while self.items_layout.count():
                item = self.items_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        widget = QueueItemWidget(job_id, meta, self.container)
        widget.cancel_requested.connect(self.cancel_job_requested.emit)
        widget.play_requested.connect(self.play_requested.emit)
        self.item_widgets[job_id] = widget
        self.items_layout.insertWidget(0, widget)

        self._update_counter()

    def update_job_progress(self, job_id: str, percent: float, speed: str, eta: str, status: str):
        if job_id in self.item_widgets:
            self.item_widgets[job_id].update_progress(percent, speed, eta, status)

    def mark_job_completed(self, job_id: str, file_path: str):
        if job_id in self.item_widgets:
            self.item_widgets[job_id].mark_completed(file_path)
        self._update_counter()

    def mark_job_error(self, job_id: str, err_msg: str):
        if job_id in self.item_widgets:
            self.item_widgets[job_id].mark_error(err_msg)
        self._update_counter()

    def _update_counter(self):
        count = len(self.item_widgets)
        self.subtitle_label.setText(f"{count} job{'s' if count != 1 else ''} tracked")

    def _open_download_folder(self):
        download_dir = AppConfig.get_instance().get("download_dir", "")
        if download_dir and os.path.exists(download_dir):
            if os.name == 'nt':
                os.startfile(download_dir)
            else:
                subprocess.Popen(['xdg-open', download_dir])
