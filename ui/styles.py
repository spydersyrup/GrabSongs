# CassetteCat Design System Stylesheet
# Colors and typography strictly derived from C:\Users\ladsa\Desktop\CassetteCat_Desktop\DESIGN.md

THEME_CASSETTECAT = """
/* =========================================================================
   CassetteCat Visual Design System
   Base Surface: #0E0D0C
   Brand Accent: Record Red (#C23B30, Hover: #D64337, Active: #AA332A)
   Typography: Space Grotesk (Headings), IBM Plex Sans (Body), IBM Plex Mono (Labels)
========================================================================= */

QMainWindow, QWidget#CentralWidget {
    background-color: #0E0D0C; /* surfaceBase */
    color: #F5F0EC;            /* textPrimary */
    font-family: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
}

/* Sidebar */
QFrame#Sidebar {
    background-color: #131211; /* surfaceSidebar */
    border-right: 1px solid rgba(245, 240, 236, 0.05); /* borderSubtle */
    min-width: 220px;
    max-width: 220px;
}

QLabel#AppTitle {
    font-family: "Space Grotesk", sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #F5F0EC; /* textPrimary */
    letter-spacing: 0.5px;
}

QLabel#AppSubtitle {
    font-family: "IBM Plex Mono", monospace;
    font-size: 11px;
    color: #A8A49E; /* textSecondary */
    font-weight: 500;
    letter-spacing: 0.3px;
}

/* Nav Item Button (Matches NavItem.qml) */
QPushButton.NavButton {
    background-color: transparent;
    color: #A8A49E; /* textSecondary */
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #22201D; /* surfaceCardHover */
    color: #F5F0EC;            /* textPrimary */
}

QPushButton.NavButton:checked {
    background-color: #282623; /* surfaceElevated */
    color: #F5F0EC;            /* textPrimary */
    font-weight: 600;
    border-left: 3px solid #C23B30; /* recordRed */
    padding-left: 11px;
}

/* Input Fields (Matches surfaceInput) */
QLineEdit {
    background-color: #1A1917; /* surfaceInput */
    border: 1px solid rgba(245, 240, 236, 0.08); /* borderVariant */
    border-radius: 8px;
    padding: 10px 14px;
    color: #F5F0EC; /* textPrimary */
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
    selection-background-color: #C23B30;
}

QLineEdit:focus {
    border: 1px solid #C23B30; /* recordRed focus */
    background-color: #1F1E1B;
}

QLineEdit::placeholder {
    color: #918E88; /* silverDim */
}

/* Action Buttons */
QPushButton.PrimaryButton {
    background-color: #C23B30; /* recordRed */
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #D64337; /* recordRedHover */
}

QPushButton.PrimaryButton:pressed {
    background-color: #AA332A;
}

QPushButton.PrimaryButton:disabled {
    background-color: #282623;
    color: #918E88;
}

QPushButton.SecondaryButton {
    background-color: #282623; /* surfaceElevated */
    color: #F5F0EC;            /* textPrimary */
    border: 1px solid rgba(245, 240, 236, 0.08);
    border-radius: 8px;
    padding: 8px 14px;
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #22201D; /* surfaceCardHover */
    border-color: rgba(245, 240, 236, 0.15);
}

QPushButton.SecondaryButton:pressed {
    background-color: #181715;
}

QPushButton.DangerButton {
    background-color: rgba(255, 107, 107, 0.12); /* danger tint */
    color: #FF6B6B;                              /* danger */
    border: 1px solid rgba(255, 107, 107, 0.25);
    border-radius: 8px;
    padding: 8px 14px;
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: rgba(255, 107, 107, 0.22);
    border-color: #FF6B6B;
}

/* Cards & Containers (Matches surfaceCard) */
QFrame.CardWidget {
    background-color: #181715; /* surfaceCard */
    border: 1px solid rgba(245, 240, 236, 0.06); /* borderCard */
    border-radius: 10px;
}

QFrame.CardWidget:hover {
    background-color: #22201D; /* surfaceCardHover */
    border-color: rgba(245, 240, 236, 0.12);
}

/* Headings */
QLabel.Heading1 {
    font-family: "Space Grotesk", sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #F5F0EC;
    letter-spacing: -0.2px;
}

QLabel.Heading2 {
    font-family: "Space Grotesk", sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: #F5F0EC;
}

/* Progress Bars */
QProgressBar {
    background-color: #22201D; /* surfaceCardHover */
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #C23B30; /* recordRed */
    border-radius: 3px;
}

/* Scroll Area & Minimalist Warm Dark Bars */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #0E0D0C; /* surfaceBase */
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #282623; /* surfaceElevated */
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #383530;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ComboBox & SpinBox */
QComboBox, QSpinBox {
    background-color: #1A1917; /* surfaceInput */
    border: 1px solid rgba(245, 240, 236, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #F5F0EC; /* textPrimary */
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
}

QComboBox:focus, QSpinBox:focus {
    border-color: #C23B30;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #282623; /* surfaceElevated */
    color: #F5F0EC;
    border: 1px solid rgba(245, 240, 236, 0.1);
    selection-background-color: #C23B30;
    border-radius: 6px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #22201D; /* surfaceCardHover */
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #C23B30; /* recordRed */
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #F5F0EC; /* textPrimary */
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::handle:horizontal:hover {
    background: #FFFFFF;
    transform: scale(1.15);
}

/* Player Dock / Bottom Bar (Matches surfaceDock) */
QFrame#PlayerBar {
    background-color: #151412; /* surfaceDock */
    border-top: 1px solid rgba(245, 240, 236, 0.05); /* borderSubtle */
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #F5F0EC;
    font-family: "IBM Plex Sans", sans-serif;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid rgba(245, 240, 236, 0.2);
    background-color: #1A1917;
}

QCheckBox::indicator:checked {
    background-color: #C23B30;
    border-color: #C23B30;
    image: none;
}
"""
