from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

SERVICE_COLORS = {
    "spotify": {"bg": "rgba(29, 185, 84, 0.18)", "text": "#1DB954", "border": "#1DB954"},
    "apple_music": {"bg": "rgba(250, 45, 72, 0.18)", "text": "#FA2D48", "border": "#FA2D48"},
    "deezer": {"bg": "rgba(162, 56, 255, 0.18)", "text": "#A238FF", "border": "#A238FF"},
    "youtube": {"bg": "rgba(255, 0, 0, 0.18)", "text": "#FF3333", "border": "#FF0000"},
    "search": {"bg": "rgba(99, 102, 241, 0.18)", "text": "#818CF8", "border": "#6366F1"},
    "empty": {"bg": "rgba(140, 140, 158, 0.15)", "text": "#8C8C9E", "border": "#4A4A58"},
}

SERVICE_LABELS = {
    "spotify": "SPOTIFY",
    "apple_music": "APPLE MUSIC",
    "deezer": "DEEZER",
    "youtube": "YOUTUBE",
    "search": "SEARCH",
    "empty": "INPUT",
}

class ServiceBadge(QLabel):
    def __init__(self, service="empty", parent=None):
        super().__init__(parent)
        self.set_service(service)

    def set_service(self, service: str):
        colors = SERVICE_COLORS.get(service, SERVICE_COLORS["empty"])
        label = SERVICE_LABELS.get(service, service.upper())

        self.setText(label)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
