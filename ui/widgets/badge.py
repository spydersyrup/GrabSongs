from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

SERVICE_COLORS = {
    "spotify": {"bg": "rgba(29, 185, 84, 0.12)", "text": "#1DB954", "border": "rgba(29, 185, 84, 0.35)"},
    "apple_music": {"bg": "rgba(250, 45, 72, 0.12)", "text": "#FA2D48", "border": "rgba(250, 45, 72, 0.35)"},
    "deezer": {"bg": "rgba(162, 56, 255, 0.12)", "text": "#A238FF", "border": "rgba(162, 56, 255, 0.35)"},
    "youtube": {"bg": "rgba(194, 59, 48, 0.15)", "text": "#FF6B6B", "border": "rgba(194, 59, 48, 0.4)"},
    "search": {"bg": "rgba(194, 59, 48, 0.12)", "text": "#D8584E", "border": "rgba(194, 59, 48, 0.3)"},
    "empty": {"bg": "rgba(168, 164, 158, 0.08)", "text": "#918E88", "border": "rgba(245, 240, 236, 0.08)"},
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
                border-radius: 4px;
                padding: 3px 8px;
                font-family: "IBM Plex Mono", monospace;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 0.6px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
