import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt
from core.config import AppConfig

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AppConfig.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(18)

        # Header Title
        title_label = QLabel("Settings & Preferences", self)
        title_label.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #F5F0EC;
            letter-spacing: -0.3px;
        """)
        layout.addWidget(title_label)

        sub_label = QLabel("Configure audio format, download folder, lyrics, and metadata behavior.", self)
        sub_label.setStyleSheet("""
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 13px;
            color: #A8A49E;
            margin-bottom: 2px;
        """)
        layout.addWidget(sub_label)

        # Settings Card
        card = QFrame(self)
        card.setProperty("class", "CardWidget")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(16)

        # 1. Download Folder
        folder_layout = QVBoxLayout()
        folder_layout.setSpacing(6)
        folder_lbl = QLabel("Download Location", card)
        folder_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        folder_layout.addWidget(folder_lbl)

        folder_input_row = QHBoxLayout()
        folder_input_row.setSpacing(10)
        self.folder_input = QLineEdit(self.config.get("download_dir", ""), card)
        self.folder_input.textChanged.connect(lambda t: self.config.set("download_dir", t))
        folder_input_row.addWidget(self.folder_input, stretch=1)

        browse_btn = QPushButton("Browse...", card)
        browse_btn.setProperty("class", "SecondaryButton")
        browse_btn.clicked.connect(self._browse_folder)
        folder_input_row.addWidget(browse_btn)

        folder_layout.addLayout(folder_input_row)
        card_layout.addLayout(folder_layout)

        # 2. Audio Format & Quality
        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(18)

        # Format
        fmt_col = QVBoxLayout()
        fmt_col.setSpacing(6)
        fmt_lbl = QLabel("Output Audio Format", card)
        fmt_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        fmt_col.addWidget(fmt_lbl)

        self.fmt_combo = QComboBox(card)
        self.fmt_combo.addItems(["MP3", "M4A", "FLAC", "OPUS"])
        current_fmt = self.config.get("audio_format", "mp3").upper()
        idx = self.fmt_combo.findText(current_fmt)
        if idx >= 0:
            self.fmt_combo.setCurrentIndex(idx)
        self.fmt_combo.currentTextChanged.connect(lambda val: self.config.set("audio_format", val.lower()))
        fmt_col.addWidget(self.fmt_combo)
        fmt_row.addLayout(fmt_col)

        # Quality
        qual_col = QVBoxLayout()
        qual_col.setSpacing(6)
        qual_lbl = QLabel("Bitrate / Quality", card)
        qual_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        qual_col.addWidget(qual_lbl)

        self.qual_combo = QComboBox(card)
        self.qual_combo.addItems(["320 kbps (High)", "256 kbps (Standard)", "192 kbps (Medium)", "Lossless"])
        curr_qual = self.config.get("audio_quality", "320")
        if curr_qual == "320":
            self.qual_combo.setCurrentIndex(0)
        elif curr_qual == "256":
            self.qual_combo.setCurrentIndex(1)
        elif curr_qual == "192":
            self.qual_combo.setCurrentIndex(2)
        elif curr_qual == "lossless":
            self.qual_combo.setCurrentIndex(3)

        self.qual_combo.currentIndexChanged.connect(self._on_quality_changed)
        qual_col.addWidget(self.qual_combo)
        fmt_row.addLayout(qual_col)

        # Concurrency
        conc_col = QVBoxLayout()
        conc_col.setSpacing(6)
        conc_lbl = QLabel("Concurrent Downloads", card)
        conc_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        conc_col.addWidget(conc_lbl)

        self.conc_spin = QSpinBox(card)
        self.conc_spin.setRange(1, 5)
        self.conc_spin.setValue(int(self.config.get("max_concurrent_downloads", 2)))
        self.conc_spin.valueChanged.connect(lambda v: self.config.set("max_concurrent_downloads", v))
        conc_col.addWidget(self.conc_spin)
        fmt_row.addLayout(conc_col)

        card_layout.addLayout(fmt_row)

        # 3. Metadata & Lyrics Checkboxes
        toggles_layout = QVBoxLayout()
        toggles_layout.setSpacing(10)

        self.chk_art = QCheckBox("Embed High-Resolution Album Artwork (ID3/MP4/FLAC)", card)
        self.chk_art.setChecked(bool(self.config.get("embed_artwork", True)))
        self.chk_art.toggled.connect(lambda v: self.config.set("embed_artwork", v))
        toggles_layout.addWidget(self.chk_art)

        self.chk_lyrics = QCheckBox("Embed Synced & Plain Lyrics from LRCLIB", card)
        self.chk_lyrics.setChecked(bool(self.config.get("embed_lyrics", True)))
        self.chk_lyrics.toggled.connect(lambda v: self.config.set("embed_lyrics", v))
        toggles_layout.addWidget(self.chk_lyrics)

        self.chk_lrc = QCheckBox("Save Separate .lrc File Alongside Song", card)
        self.chk_lrc.setChecked(bool(self.config.get("save_lrc_file", False)))
        self.chk_lrc.toggled.connect(lambda v: self.config.set("save_lrc_file", v))
        toggles_layout.addWidget(self.chk_lrc)

        card_layout.addLayout(toggles_layout)

        # 4. Naming Pattern
        pattern_layout = QVBoxLayout()
        pattern_layout.setSpacing(6)

        pattern_lbl = QLabel("File Naming Pattern", card)
        pattern_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        pattern_layout.addWidget(pattern_lbl)

        self.pattern_input = QLineEdit(self.config.get("naming_pattern", "{artist} - {title}"), card)
        self.pattern_input.textChanged.connect(lambda t: self.config.set("naming_pattern", t))
        pattern_layout.addWidget(self.pattern_input)

        help_lbl = QLabel("Tokens: {artist}, {title}, {album}, {track}", card)
        help_lbl.setStyleSheet("""
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            color: #918E88;
        """)
        pattern_layout.addWidget(help_lbl)

        card_layout.addLayout(pattern_layout)

        # 5. FFmpeg Status Check
        ffmpeg_box = QFrame(card)
        ffmpeg_box.setStyleSheet("background-color: #131211; border-radius: 6px; padding: 10px; border: 1px solid rgba(245, 240, 236, 0.05);")
        ff_layout = QHBoxLayout(ffmpeg_box)
        ff_layout.setContentsMargins(10, 8, 10, 8)

        ff_path = self.config.get("ffmpeg_path", "")
        ff_ok = bool(ff_path and os.path.exists(ff_path))

        status_icon = "●"
        status_text = f"Audio Transcoder: {'Ready (FFmpeg bundled)' if ff_ok else 'Missing'}\n{ff_path}"

        ff_lbl = QLabel(f"{status_icon} {status_text}", ffmpeg_box)
        ff_lbl.setStyleSheet(f"""
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            color: {'#34D399' if ff_ok else '#FF6B6B'};
        """)
        ff_layout.addWidget(ff_lbl)

        card_layout.addWidget(ffmpeg_box)

        layout.addWidget(card)
        layout.addStretch(1)

    def _browse_folder(self):
        curr = self.folder_input.text()
        chosen = QFileDialog.getExistingDirectory(self, "Select Download Directory", curr)
        if chosen:
            self.folder_input.setText(chosen)
            self.config.set("download_dir", chosen)

    def _on_quality_changed(self, idx: int):
        val_map = {0: "320", 1: "256", 2: "192", 3: "lossless"}
        self.config.set("audio_quality", val_map.get(idx, "320"))
