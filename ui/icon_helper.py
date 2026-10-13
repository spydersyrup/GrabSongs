import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QSize, Qt

ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")

def get_svg_pixmap(icon_name: str, size: int = 20, color_hex: str = "#F5F0EC") -> QPixmap:
    svg_path = os.path.join(ICONS_DIR, f"{icon_name}.svg")
    if not os.path.exists(svg_path):
        # Fallback empty pixmap
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        return pix

    renderer = QSvgRenderer(svg_path)
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()

    # Apply color overlay
    if color_hex:
        tint_pix = QPixmap(size, size)
        tint_pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(tint_pix)
        p.drawPixmap(0, 0, pix)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.fillRect(tint_pix.rect(), QColor(color_hex))
        p.end()
        return tint_pix

    return pix

def get_svg_icon(icon_name: str, size: int = 20, color_hex: str = "#F5F0EC") -> QIcon:
    pix = get_svg_pixmap(icon_name, size, color_hex)
    return QIcon(pix)
