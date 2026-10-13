import os
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from core.audio_player import PreviewPlayer
from ..icon_helper import get_svg_icon, get_svg_pixmap

class PlayerBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlayerBar")
        self.setFixedHeight(74)
        self.player = PreviewPlayer.get_instance()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(24)

        # -------------------------------------------------------------
        # Left Section: Artwork + Track Title + Artist + Heart
        # -------------------------------------------------------------
        left_box = QWidget(self)
        left_layout = QHBoxLayout(left_box)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.cover_label = QLabel(left_box)
        self.cover_label.setFixedSize(46, 46)
        self.cover_label.setStyleSheet("background-color: #22201D; border-radius: 6px;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("🎵")
        left_layout.addWidget(self.cover_label)

        title_artist_col = QVBoxLayout()
        title_artist_col.setSpacing(2)
        title_artist_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel("No track playing", left_box)
        self.title_label.setStyleSheet("""
            color: #F5F0EC;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
        """)
        title_artist_col.addWidget(self.title_label)

        self.artist_label = QLabel("CassetteCat Engine", left_box)
        self.artist_label.setStyleSheet("""
            color: #A8A49E;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 11px;
        """)
        title_artist_col.addWidget(self.artist_label)

        left_layout.addLayout(title_artist_col)

        # Heart button
        heart_btn = QPushButton(left_box)
        heart_btn.setFixedSize(28, 28)
        heart_btn.setIcon(get_svg_icon("heart", 16, "#A8A49E"))
        heart_btn.setIconSize(QSize(16, 16))
        heart_btn.setStyleSheet("background: transparent; border: none;")
        heart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(heart_btn)

        layout.addWidget(left_box, stretch=2)

        # -------------------------------------------------------------
        # Center Section: Transport Buttons + Timeline Bar
        # -------------------------------------------------------------
        center_col = QVBoxLayout()
        center_col.setSpacing(4)
        center_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctrl_row.setSpacing(14)

        # Shuffle
        self.btn_shuffle = QPushButton(self)
        self.btn_shuffle.setFixedSize(28, 28)
        self.btn_shuffle.setIcon(get_svg_icon("arrow-up-down", 15, "#918E88"))
        self.btn_shuffle.setStyleSheet("background: transparent; border: none;")
        ctrl_row.addWidget(self.btn_shuffle)

        # Previous
        self.btn_prev = QPushButton(self)
        self.btn_prev.setFixedSize(30, 30)
        self.btn_prev.setIcon(get_svg_icon("chevron-left", 18, "#F5F0EC"))
        self.btn_prev.setStyleSheet("background: transparent; border: none;")
        self.btn_prev.clicked.connect(lambda: self.player.seek(0))
        ctrl_row.addWidget(self.btn_prev)

        # Play / Pause Circle (Record Red)
        self.play_btn = QPushButton(self)
        self.play_btn.setFixedSize(38, 38)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #C23B30;
                border: none;
                border-radius: 19px;
            }
            QPushButton:hover {
                background-color: #D64337;
            }
            QPushButton:pressed {
                background-color: #AA332A;
            }
        """)
        self.play_btn.setIcon(get_svg_icon("play", 18, "#FFFFFF"))
        self.play_btn.setIconSize(QSize(18, 18))
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.player.toggle_play)
        ctrl_row.addWidget(self.play_btn)

        # Next
        self.btn_next = QPushButton(self)
        self.btn_next.setFixedSize(30, 30)
        self.btn_next.setIcon(get_svg_icon("chevron-right", 18, "#F5F0EC"))
        self.btn_next.setStyleSheet("background: transparent; border: none;")
        ctrl_row.addWidget(self.btn_next)

        # Repeat
        self.btn_repeat = QPushButton(self)
        self.btn_repeat.setFixedSize(28, 28)
        self.btn_repeat.setIcon(get_svg_icon("arrow-up", 15, "#918E88"))
        self.btn_repeat.setStyleSheet("background: transparent; border: none;")
        ctrl_row.addWidget(self.btn_repeat)

        center_col.addLayout(ctrl_row)

        # Timeline row (Timestamps in IBM Plex Mono)
        time_row = QHBoxLayout()
        time_row.setSpacing(8)

        self.time_curr = QLabel("0:00", self)
        self.time_curr.setStyleSheet("""
            color: #918E88;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        """)
        time_row.addWidget(self.time_curr)

        self.pos_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.pos_slider.setRange(0, 1000)
        self.pos_slider.setValue(0)
        self.pos_slider.sliderMoved.connect(self._on_seek)
        time_row.addWidget(self.pos_slider)

        self.time_total = QLabel("-0:00", self)
        self.time_total.setStyleSheet("""
            color: #918E88;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        """)
        time_row.addWidget(self.time_total)

        center_col.addLayout(time_row)
        layout.addLayout(center_col, stretch=4)

        # -------------------------------------------------------------
        # Right Section: Volume Control + Mono Percentage
        # -------------------------------------------------------------
        right_box = QWidget(self)
        right_layout = QHBoxLayout(right_box)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        vol_btn = QPushButton(right_box)
        vol_btn.setFixedSize(24, 24)
        vol_btn.setIcon(get_svg_icon("headphones", 16, "#918E88"))
        vol_btn.setStyleSheet("background: transparent; border: none;")
        right_layout.addWidget(vol_btn)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal, right_box)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(85)
        self.vol_slider.setFixedWidth(85)
        self.vol_slider.valueChanged.connect(self._on_volume_changed)
        right_layout.addWidget(self.vol_slider)

        self.vol_label = QLabel("85%", right_box)
        self.vol_label.setFixedWidth(32)
        self.vol_label.setStyleSheet("""
            color: #918E88;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        """)
        right_layout.addWidget(self.vol_label)

        layout.addWidget(right_box, stretch=2)

    def _connect_signals(self):
        self.player.track_loaded.connect(self._on_track_loaded)
        self.player.state_changed.connect(self._on_state_changed)
        self.player.position_changed.connect(self._on_position_changed)

    def _on_track_loaded(self, title: str, artist: str, file_path: str):
        self.title_label.setText(title)
        self.artist_label.setText(artist or "Unknown Artist")
        self.play_btn.setIcon(get_svg_icon("pause", 18, "#FFFFFF"))

    def _on_state_changed(self, is_playing: bool):
        icon_name = "pause" if is_playing else "play"
        self.play_btn.setIcon(get_svg_icon(icon_name, 18, "#FFFFFF"))

    def _on_position_changed(self, current_ms: int, total_ms: int):
        if total_ms > 0:
            val = int(current_ms / total_ms * 1000)
            self.pos_slider.blockSignals(True)
            self.pos_slider.setValue(val)
            self.pos_slider.blockSignals(False)

            cur_sec = current_ms // 1000
            rem_sec = (total_ms - current_ms) // 1000
            self.time_curr.setText(f"{int(cur_sec // 60)}:{int(cur_sec % 60):02d}")
            self.time_total.setText(f"-{int(rem_sec // 60)}:{int(rem_sec % 60):02d}")

    def _on_seek(self, value: int):
        total_ms = self.player.player.duration()
        if total_ms > 0:
            target_ms = int(value / 1000 * total_ms)
            self.player.seek(target_ms)

    def _on_volume_changed(self, value: int):
        self.player.set_volume(value / 100.0)
        self.vol_label.setText(f"{value}%")
