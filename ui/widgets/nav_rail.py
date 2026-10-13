from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap
from ..icon_helper import get_svg_pixmap, get_svg_icon
import os

class NavRailButton(QPushButton):
    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setToolTip(tooltip)
        self.setFixedSize(42, 42)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_appearance(False)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._update_appearance(checked)

    def _update_appearance(self, active: bool):
        color = "#F5F0EC" if active else "#A8A49E"
        pix = get_svg_pixmap(self.icon_name, 20, color)
        self.setIcon(QIcon(pix))
        self.setIconSize(QSize(20, 20))

        if active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #282623; /* surfaceElevated */
                    border: none;
                    border-radius: 8px;
                    border-left: 3px solid #C23B30; /* recordRed indicator */
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #22201D; /* surfaceCardHover */
                }
            """)

class NavRail(QFrame):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(60)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 14, 9, 14)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # 1. Top Logo (CassetteCat red icon)
        logo_label = QLabel(self)
        logo_label.setFixedSize(32, 32)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "cassettecat_icon.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        layout.addWidget(logo_label)

        layout.addSpacing(12)

        # 2. Main Nav Items (Explore, Library, Queue)
        self.btn_explore = NavRailButton("house", "Explore & Download", self)
        self.btn_explore.setChecked(True)
        self.btn_explore.clicked.connect(lambda: self.set_active_index(0))
        layout.addWidget(self.btn_explore)

        self.btn_queue = NavRailButton("clock", "Download Queue", self)
        self.btn_queue.clicked.connect(lambda: self.set_active_index(1))
        layout.addWidget(self.btn_queue)

        self.btn_library = NavRailButton("disc", "Library", self)
        self.btn_library.clicked.connect(lambda: self.set_active_index(2))
        layout.addWidget(self.btn_library)

        layout.addStretch(1)

        # 3. Bottom Settings Button
        self.btn_settings = NavRailButton("settings", "Settings", self)
        self.btn_settings.clicked.connect(lambda: self.set_active_index(3))
        layout.addWidget(self.btn_settings)

    def set_active_index(self, index: int):
        self.btn_explore.setChecked(index == 0)
        self.btn_queue.setChecked(index == 1)
        self.btn_library.setChecked(index == 2)
        self.btn_settings.setChecked(index == 3)
        self.page_changed.emit(index)
