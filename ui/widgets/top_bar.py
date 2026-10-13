from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..icon_helper import get_svg_pixmap, get_svg_icon

class TopBar(QFrame):
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QFrame {
                background-color: #0E0D0C; /* surfaceBase */
                border-bottom: 1px solid rgba(245, 240, 236, 0.04);
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 16, 0)
        layout.setSpacing(12)

        # Title Label in Space Grotesk
        self.title_label = QLabel("Explore", self)
        self.title_label.setStyleSheet("""
            font-family: 'Space Grotesk', sans-serif;
            font-size: 17px;
            font-weight: 700;
            color: #F5F0EC;
            letter-spacing: -0.2px;
        """)
        layout.addWidget(self.title_label)

        layout.addStretch(1)

        # Window Controls: Minimize, Maximize, Close
        btn_style = """
            QPushButton {
                background-color: transparent;
                color: #A8A49E;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-family: 'IBM Plex Mono', monospace;
            }
            QPushButton:hover {
                background-color: #22201D;
                color: #F5F0EC;
            }
        """

        close_style = """
            QPushButton {
                background-color: transparent;
                color: #A8A49E;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-family: 'IBM Plex Mono', monospace;
            }
            QPushButton:hover {
                background-color: #C23B30;
                color: #FFFFFF;
            }
        """

        self.btn_min = QPushButton("─", self)
        self.btn_min.setFixedSize(32, 28)
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.btn_min)

        self.btn_max = QPushButton("□", self)
        self.btn_max.setFixedSize(32, 28)
        self.btn_max.setStyleSheet(btn_style)
        self.btn_max.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕", self)
        self.btn_close.setFixedSize(32, 28)
        self.btn_close.setStyleSheet(close_style)
        self.btn_close.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.btn_close)

    def set_title(self, title: str):
        self.title_label.setText(title)
