import os
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QProgressBar, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any

class QueueItemWidget(QFrame):
    cancel_requested = pyqtSignal(str) # job_id
    play_requested = pyqtSignal(str, str, str) # path, title, artist
    reveal_requested = pyqtSignal(str) # path

    def __init__(self, job_id: str, meta: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.job_id = job_id
        self.meta = dict(meta)
        self.file_path = None

        self.setProperty("class", "CardWidget")
        self.setFixedHeight(82)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(6)

        # Top row: Title, Artist, Status, Actions
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Title & Artist
        title_artist_layout = QVBoxLayout()
        title_artist_layout.setSpacing(2)

        self.title_label = QLabel(self.meta.get("title", "Unknown Title"), self)
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 700;")
        title_artist_layout.addWidget(self.title_label)

        self.artist_label = QLabel(self.meta.get("artist", "Unknown Artist"), self)
        self.artist_label.setStyleSheet("color: #8C8C9E; font-size: 11px;")
        title_artist_layout.addWidget(self.artist_label)

        top_row.addLayout(title_artist_layout, stretch=1)

        # Status text & Metrics (speed, eta)
        self.metrics_label = QLabel("", self)
        self.metrics_label.setStyleSheet("color: #8C8C9E; font-size: 11px;")
        top_row.addWidget(self.metrics_label)

        # Status Badge
        self.status_badge = QLabel("Queued", self)
        self.status_badge.setStyleSheet("""
            background-color: rgba(99, 102, 241, 0.15);
            color: #818CF8;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 700;
        """)
        top_row.addWidget(self.status_badge)

        # Action Button (Cancel / Play / Reveal)
        self.action_btn = QPushButton("✕ Cancel", self)
        self.action_btn.setProperty("class", "DangerButton")
        self.action_btn.setFixedSize(85, 28)
        self.action_btn.clicked.connect(self._on_action_clicked)
        top_row.addWidget(self.action_btn)

        main_layout.addLayout(top_row)

        # Bottom row: Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        main_layout.addWidget(self.progress_bar)

    def update_progress(self, percent: float, speed: str, eta: str, status: str):
        self.progress_bar.setValue(int(percent))
        self.status_badge.setText(status)

        metrics = []
        if speed:
            metrics.append(speed)
        if eta:
            metrics.append(f"ETA: {eta}")
        self.metrics_label.setText(" • ".join(metrics))

        if status == "Downloading...":
            self.status_badge.setStyleSheet("""
                background-color: rgba(14, 165, 233, 0.15);
                color: #38BDF8;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            """)
        elif "Converting" in status or "Embedding" in status:
            self.status_badge.setStyleSheet("""
                background-color: rgba(234, 179, 8, 0.15);
                color: #FACC15;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 700;
            """)

    def mark_completed(self, file_path: str):
        self.file_path = file_path
        self.progress_bar.setValue(100)
        self.metrics_label.setText("")
        self.status_badge.setText("Completed")
        self.status_badge.setStyleSheet("""
            background-color: rgba(34, 197, 94, 0.15);
            color: #4ADE80;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 700;
        """)
        self.action_btn.setText("▶ Play")
        self.action_btn.setProperty("class", "PrimaryButton")
        self.action_btn.setStyleSheet("")

    def mark_error(self, error_msg: str):
        self.status_badge.setText("Failed")
        self.status_badge.setStyleSheet("""
            background-color: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 700;
        """)
        self.metrics_label.setText(error_msg[:30] + ("..." if len(error_msg) > 30 else ""))
        self.action_btn.setEnabled(False)

    def _on_action_clicked(self):
        if self.file_path and os.path.exists(self.file_path):
            self.play_requested.emit(
                self.file_path,
                self.meta.get("title", ""),
                self.meta.get("artist", "")
            )
        else:
            self.cancel_requested.emit(self.job_id)
