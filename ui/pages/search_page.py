from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QScrollArea, QFrame,
    QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from typing import List, Dict, Any
from ..widgets.badge import ServiceBadge
from ..widgets.track_card import TrackCard
from core.metadata import MetadataResolver
from core.metadata.detector import ServiceDetector

class MetadataFetchWorker(QThread):
    finished_signal = pyqtSignal(dict) # result dict

    def __init__(self, query: str, parent=None):
        super().__init__(parent)
        self.query = query

    def run(self):
        result = MetadataResolver.resolve(self.query)
        self.finished_signal.emit(result)

class SearchPage(QWidget):
    download_requested = pyqtSignal(list) # list of track metadata dicts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tracks: List[Dict[str, Any]] = []
        self.cards: List[TrackCard] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(18)

        # Header Title (Space Grotesk)
        title_label = QLabel("Explore & Download", self)
        title_label.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #F5F0EC;
            letter-spacing: -0.3px;
        """)
        layout.addWidget(title_label)

        sub_label = QLabel("Paste any link from Spotify, Apple Music, Deezer, YouTube, or search across music catalogs.", self)
        sub_label.setStyleSheet("""
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 13px;
            color: #A8A49E;
            margin-bottom: 2px;
        """)
        layout.addWidget(sub_label)

        # Search Bar Row
        search_card = QFrame(self)
        search_card.setProperty("class", "CardWidget")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(10)

        # Service Detector Badge
        self.badge = ServiceBadge("empty", search_card)
        search_layout.addWidget(self.badge)

        # Search LineEdit
        self.search_input = QLineEdit(search_card)
        self.search_input.setPlaceholderText("Paste URL or enter song name (e.g. 'Daft Punk - Instant Crush')...")
        self.search_input.textChanged.connect(self._on_query_changed)
        self.search_input.returnPressed.connect(self._start_search)
        search_layout.addWidget(self.search_input, stretch=1)

        # Paste Button
        paste_btn = QPushButton("📋 Paste", search_card)
        paste_btn.setProperty("class", "SecondaryButton")
        paste_btn.clicked.connect(self._on_paste_clicked)
        search_layout.addWidget(paste_btn)

        # Search / Fetch Button
        self.fetch_btn = QPushButton("Explore", search_card)
        self.fetch_btn.setProperty("class", "PrimaryButton")
        self.fetch_btn.setFixedWidth(100)
        self.fetch_btn.clicked.connect(self._start_search)
        search_layout.addWidget(self.fetch_btn)

        layout.addWidget(search_card)

        # Results Summary & Selection Toolbar
        self.toolbar_frame = QFrame(self)
        toolbar_layout = QHBoxLayout(self.toolbar_frame)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        self.summary_label = QLabel("", self.toolbar_frame)
        self.summary_label.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: #F5F0EC;
        """)
        toolbar_layout.addWidget(self.summary_label, stretch=1)

        self.select_all_btn = QPushButton("Select All", self.toolbar_frame)
        self.select_all_btn.setProperty("class", "SecondaryButton")
        self.select_all_btn.clicked.connect(lambda: self._set_all_selected(True))
        toolbar_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All", self.toolbar_frame)
        self.deselect_all_btn.setProperty("class", "SecondaryButton")
        self.deselect_all_btn.clicked.connect(lambda: self._set_all_selected(False))
        toolbar_layout.addWidget(self.deselect_all_btn)

        self.download_selected_btn = QPushButton("⬇ Download Selected", self.toolbar_frame)
        self.download_selected_btn.setProperty("class", "PrimaryButton")
        self.download_selected_btn.clicked.connect(self._on_download_selected)
        toolbar_layout.addWidget(self.download_selected_btn)

        self.toolbar_frame.setVisible(False)
        layout.addWidget(self.toolbar_frame)

        # Scroll Area for Track Cards
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area, stretch=1)

        # Empty State Placeholder
        self._show_empty_state()

    def _show_empty_state(self):
        self._clear_cards()
        self.toolbar_frame.setVisible(False)

        empty_box = QFrame(self.cards_container)
        empty_box.setProperty("class", "CardWidget")
        empty_layout = QVBoxLayout(empty_box)
        empty_layout.setContentsMargins(40, 50, 40, 50)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(12)

        icon_lbl = QLabel("📼", empty_box)
        icon_lbl.setStyleSheet("font-size: 38px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_lbl)

        title_lbl = QLabel("CassetteCat Downloader Engine", empty_box)
        title_lbl.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #F5F0EC;
        """)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            "Paste URLs from Spotify, Apple Music, Deezer, YouTube, or type track titles.\n"
            "High-resolution album art and synchronized lyrics are embedded automatically.",
            empty_box
        )
        desc_lbl.setStyleSheet("""
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 12px;
            color: #A8A49E;
            text-align: center;
            line-height: 1.5;
        """)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_lbl)

        self.cards_layout.addWidget(empty_box)

    def _clear_cards(self):
        self.cards.clear()
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _on_query_changed(self, text: str):
        detected = ServiceDetector.detect(text)
        service = detected.get("service", "empty")
        self.badge.set_service(service)

    def _on_paste_clicked(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.search_input.setText(text)
            self._start_search()

    def _start_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")

        self.worker = MetadataFetchWorker(query, self)
        self.worker.finished_signal.connect(self._on_search_completed)
        self.worker.start()

    def _on_search_completed(self, result: Dict[str, Any]):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Explore")

        if not result.get("success"):
            QMessageBox.warning(self, "No Results", result.get("error", "Unable to resolve query."))
            return

        tracks = result.get("tracks", [])
        if not tracks:
            QMessageBox.information(self, "No Results", "No matching songs found.")
            return

        self._clear_cards()
        self.current_tracks = tracks

        res_type = result.get("type", "results")
        service_name = result.get("service", "").capitalize()
        summary_title = f"{service_name} • {len(tracks)} track{'s' if len(tracks) != 1 else ''} found"
        if res_type in ("album", "playlist") and result.get("item"):
            item = result["item"]
            summary_title = f"{item.get('title')} by {item.get('artist')} ({len(tracks)} tracks)"

        self.summary_label.setText(summary_title)
        self.toolbar_frame.setVisible(True)

        for track in tracks:
            card = TrackCard(track, self.cards_container)
            card.download_requested.connect(lambda t: self.download_requested.emit([t]))
            card.selection_changed.connect(self._update_download_button_count)
            self.cards.append(card)
            self.cards_layout.addWidget(card)

        self._update_download_button_count()

    def _set_all_selected(self, selected: bool):
        for card in self.cards:
            card.set_selected(selected)
        self._update_download_button_count()

    def _update_download_button_count(self):
        count = sum(1 for c in self.cards if c.is_selected())
        self.download_selected_btn.setText(f"⬇ Download Selected ({count})")
        self.download_selected_btn.setEnabled(count > 0)

    def _on_download_selected(self):
        selected_tracks = [c.meta for c in self.cards if c.is_selected()]
        if selected_tracks:
            self.download_requested.emit(selected_tracks)
