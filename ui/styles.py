THEME_DARK = """
/* Harmonix Dark Theme */

QMainWindow, QWidget#CentralWidget {
    background-color: #111115;
    color: #F0F0F5;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

/* Sidebar */
QFrame#Sidebar {
    background-color: #16161C;
    border-right: 1px solid #23232C;
    min-width: 210px;
    max-width: 210px;
}

QLabel#AppTitle {
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

QLabel#AppSubtitle {
    font-size: 11px;
    color: #8C8C9E;
    font-weight: 500;
}

/* Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #9C9CAE;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #21212B;
    color: #FFFFFF;
}

QPushButton.NavButton:checked {
    background-color: #2A2A38;
    color: #FFFFFF;
    font-weight: 700;
    border-left: 3px solid #6366F1;
}

/* Search Bar & Inputs */
QLineEdit {
    background-color: #1C1C24;
    border: 1px solid #2E2E3C;
    border-radius: 10px;
    padding: 10px 14px;
    color: #FFFFFF;
    font-size: 13px;
    selection-background-color: #6366F1;
}

QLineEdit:focus {
    border: 1px solid #6366F1;
    background-color: #22222D;
}

/* Action Buttons */
QPushButton.PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton.PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #7C3AED);
}

QPushButton.PrimaryButton:pressed {
    background-color: #4338CA;
}

QPushButton.SecondaryButton {
    background-color: #242430;
    color: #E2E2EC;
    border: 1px solid #323242;
    border-radius: 10px;
    padding: 9px 15px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.SecondaryButton:hover {
    background-color: #2E2E3E;
    border-color: #424256;
}

QPushButton.DangerButton {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 10px;
    padding: 9px 15px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: rgba(239, 68, 68, 0.25);
    border-color: #EF4444;
}

/* Card Containers */
QFrame.CardWidget {
    background-color: #191922;
    border: 1px solid #262633;
    border-radius: 12px;
}

QFrame.CardWidget:hover {
    border-color: #38384A;
    background-color: #1D1D28;
}

/* Badges */
QLabel.Badge {
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

/* Progress Bars */
QProgressBar {
    background-color: #242432;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #EC4899);
    border-radius: 4px;
}

/* Scroll Area & Bars */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #141419;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2E2E3C;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4A4A5E;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ComboBox & SpinBox */
QComboBox, QSpinBox {
    background-color: #1C1C24;
    border: 1px solid #2E2E3C;
    border-radius: 8px;
    padding: 6px 12px;
    color: #FFFFFF;
    font-size: 13px;
}

QComboBox:focus, QSpinBox:focus {
    border-color: #6366F1;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1E1E28;
    color: #FFFFFF;
    border: 1px solid #2E2E3C;
    selection-background-color: #6366F1;
    border-radius: 6px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 5px;
    background: #262635;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #6366F1;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #818CF8;
}

/* Bottom Player Bar */
QFrame#PlayerBar {
    background-color: #15151B;
    border-top: 1px solid #22222C;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
    color: #D1D1E0;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #3E3E50;
    background-color: #1C1C26;
}

QCheckBox::indicator:checked {
    background-color: #6366F1;
    border-color: #6366F1;
    image: none;
}
"""
