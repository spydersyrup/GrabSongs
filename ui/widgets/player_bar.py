from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider
)
from PyQt6.QtCore import Qt
from core.audio_player import PreviewPlayer

class PlayerBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlayerBar")
        self.setFixedHeight(68)
        self.player = PreviewPlayer.get_instance()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(16)

        # Left: Current Track Info
        track_info_layout = QVBoxLayout()
        track_info_layout.setSpacing(2)
        track_info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title_label = QLabel("No track playing", self)
        self.title_label.setStyleSheet("""
            color: #F5F0EC;
            font-family: 'Space Grotesk', 'IBM Plex Sans', sans-serif;
            font-size: 13px;
            font-weight: 600;
        """)
        track_info_layout.addWidget(self.title_label)

        self.artist_label = QLabel("CassetteCat Audio Engine", self)
        self.artist_label.setStyleSheet("""
            color: #A8A49E;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 11px;
        """)
        track_info_layout.addWidget(self.artist_label)

        layout.addLayout(track_info_layout, stretch=2)

        # Center: Play Controls & Timeline
        center_layout = QVBoxLayout()
        center_layout.setSpacing(4)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctrl_row.setSpacing(10)

        self.play_btn = QPushButton("▶", self)
        self.play_btn.setFixedSize(34, 34)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #C23B30;
                color: #FFFFFF;
                border: none;
                border-radius: 17px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #D64337;
            }
            QPushButton:pressed {
                background-color: #AA332A;
            }
        """)
        self.play_btn.clicked.connect(self.player.toggle_play)
        ctrl_row.addWidget(self.play_btn)

        center_layout.addLayout(ctrl_row)

        # Slider & Timers row (Timers in IBM Plex Mono)
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

        self.time_total = QLabel("0:00", self)
        self.time_total.setStyleSheet("""
            color: #918E88;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        """)
        time_row.addWidget(self.time_total)

        center_layout.addLayout(time_row)
        layout.addLayout(center_layout, stretch=4)

        # Right: Volume Control
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(8)
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        vol_icon = QLabel("🔊", self)
        vol_icon.setStyleSheet("color: #918E88; font-size: 12px;")
        vol_layout.addWidget(vol_icon)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(85)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.valueChanged.connect(lambda v: self.player.set_volume(v / 100.0))
        vol_layout.addWidget(self.vol_slider)

        layout.addLayout(vol_layout, stretch=1)

    def _connect_signals(self):
        self.player.track_loaded.connect(self._on_track_loaded)
        self.player.state_changed.connect(self._on_state_changed)
        self.player.position_changed.connect(self._on_position_changed)

    def _on_track_loaded(self, title: str, artist: str, file_path: str):
        self.title_label.setText(title)
        self.artist_label.setText(artist or "Unknown Artist")
        self.play_btn.setText("⏸")

    def _on_state_changed(self, is_playing: bool):
        self.play_btn.setText("⏸" if is_playing else "▶")

    def _on_position_changed(self, current_ms: int, total_ms: int):
        if total_ms > 0:
            val = int(current_ms / total_ms * 1000)
            self.pos_slider.blockSignals(True)
            self.pos_slider.setValue(val)
            self.pos_slider.blockSignals(False)

            cur_sec = current_ms // 1000
            tot_sec = total_ms // 1000
            self.time_curr.setText(f"{int(cur_sec // 60)}:{int(cur_sec % 60):02d}")
            self.time_total.setText(f"{int(tot_sec // 60)}:{int(tot_sec % 60):02d}")

    def _on_seek(self, value: int):
        total_ms = self.player.player.duration()
        if total_ms > 0:
            target_ms = int(value / 1000 * total_ms)
            self.player.seek(target_ms)
