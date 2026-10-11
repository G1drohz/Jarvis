"""Luxify-inspired dark theme for JARVIS desktop app."""

ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
ACCENT_SOFT = "rgba(59, 130, 246, 0.18)"

DARK_QSS = f"""
QMainWindow, QWidget {{
    background-color: #0a0e14;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}

/* Sidebar */
#sidebar {{
    background-color: #0f141c;
    border-right: 1px solid #1a2332;
}}
#sidebar QPushButton {{
    background: transparent;
    border: none;
    border-radius: 10px;
    text-align: left;
    padding: 11px 14px;
    color: #8b9bb4;
    font-size: 13px;
    font-weight: 500;
}}
#sidebar QPushButton:hover {{
    background-color: #1a2332;
    color: #e5e7eb;
}}
#sidebar QPushButton[active="true"] {{
    background-color: {ACCENT_SOFT};
    color: {ACCENT};
    font-weight: 600;
}}
#sidebarTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {ACCENT};
    padding: 4px 2px;
}}
#sidebarSub {{
    color: #5b6b82;
    font-size: 11px;
}}
#collapseBtn {{
    background: transparent;
    border: 1px solid #1a2332;
    border-radius: 8px;
    color: #8b9bb4;
    padding: 6px;
    min-width: 32px;
    max-width: 36px;
}}
#collapseBtn:hover {{
    background: #1a2332;
    color: #e5e7eb;
}}

#content {{
    background-color: #0a0e14;
}}
#pageTitle {{
    font-size: 22px;
    font-weight: 700;
    color: #f3f4f6;
}}
#pageSub {{
    color: #5b6b82;
    font-size: 12px;
}}

#card {{
    background-color: #0f141c;
    border: 1px solid #1a2332;
    border-radius: 14px;
}}

QTextEdit, QPlainTextEdit {{
    background-color: #0c1219;
    border: 1px solid #1a2332;
    border-radius: 12px;
    padding: 12px;
    color: #e5e7eb;
    selection-background-color: {ACCENT};
}}
QLineEdit {{
    background-color: #0c1219;
    border: 1px solid #1a2332;
    border-radius: 12px;
    padding: 11px 14px;
    color: #e5e7eb;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}}
QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
QPushButton:pressed {{ background-color: #1d4ed8; }}
QPushButton#secondary {{
    background-color: #1a2332;
    border: 1px solid #243044;
    color: #e5e7eb;
}}
QPushButton#secondary:hover {{ background-color: #243044; }}
QPushButton#ghost {{
    background: transparent;
    border: 1px solid #243044;
    color: #8b9bb4;
}}
QPushButton#ghost:hover {{
    background-color: #1a2332;
    color: #e5e7eb;
}}
QPushButton#mic {{
    background-color: #1a2332;
    border: 1px solid #243044;
    border-radius: 22px;
    min-width: 44px; max-width: 44px;
    min-height: 44px; max-height: 44px;
    font-size: 18px;
}}
QPushButton#mic[listening="true"] {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}

QCheckBox {{ spacing: 10px; color: #c5d0e0; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 6px;
    border: 1px solid #3a4a63; background: #1a2332;
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT}; border-color: {ACCENT};
}}

QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: #2a3a52; border-radius: 4px; min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

QListWidget {{
    background-color: #0c1219;
    border: 1px solid #1a2332;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 10px 12px; border-radius: 8px; color: #c5d0e0;
}}
QListWidget::item:selected {{
    background-color: {ACCENT_SOFT}; color: {ACCENT};
}}
QListWidget::item:hover {{ background-color: #1a2332; }}

QComboBox {{
    background-color: #0c1219;
    border: 1px solid #1a2332;
    border-radius: 10px;
    padding: 8px 12px;
    color: #e5e7eb;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: #0f141c;
    border: 1px solid #1a2332;
    selection-background-color: {ACCENT_SOFT};
    color: #e5e7eb;
}}

QSlider::groove:horizontal {{
    height: 6px; background: #1a2332; border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT}; width: 16px; height: 16px;
    margin: -5px 0; border-radius: 8px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 3px; }}

#statusDot {{ font-size: 10px; color: #22c55e; }}
#statusText {{ color: #5b6b82; font-size: 12px; }}
"""
