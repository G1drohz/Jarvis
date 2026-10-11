"""Luxify-inspired dark theme for JARVIS."""

# Accent can be overridden from settings later
ACCENT = "#3b82f6"  # blue
ACCENT_HOVER = "#2563eb"
ACCENT_SOFT = "rgba(59, 130, 246, 0.15)"

DARK_QSS = f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background-color: #0b0f14;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
    font-size: 13px;
}}

/* ── Sidebar ── */
#sidebar {{
    background-color: #111827;
    border-right: 1px solid #1f2937;
}}
#sidebar QPushButton {{
    background: transparent;
    border: none;
    border-radius: 10px;
    text-align: left;
    padding: 12px 16px;
    color: #9ca3af;
    font-size: 13px;
    font-weight: 500;
}}
#sidebar QPushButton:hover {{
    background-color: #1f2937;
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
    padding: 8px 4px;
}}
#sidebarSub {{
    color: #6b7280;
    font-size: 11px;
}}

/* ── Content area ── */
#content {{
    background-color: #0b0f14;
}}
#pageTitle {{
    font-size: 22px;
    font-weight: 700;
    color: #f3f4f6;
}}
#pageSub {{
    color: #6b7280;
    font-size: 12px;
}}

/* ── Cards / panels ── */
#card {{
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
}}

/* ── Chat ── */
QTextEdit, QPlainTextEdit {{
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 12px;
    color: #e5e7eb;
    selection-background-color: {ACCENT};
}}
QLineEdit {{
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 12px 16px;
    color: #e5e7eb;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: #1d4ed8;
}}
QPushButton#secondary {{
    background-color: #1f2937;
    border: 1px solid #374151;
    color: #e5e7eb;
}}
QPushButton#secondary:hover {{
    background-color: #374151;
}}
QPushButton#ghost {{
    background: transparent;
    border: 1px solid #374151;
    color: #9ca3af;
}}
QPushButton#ghost:hover {{
    background-color: #1f2937;
    color: #e5e7eb;
}}
QPushButton#danger {{
    background-color: #dc2626;
}}
QPushButton#danger:hover {{
    background-color: #b91c1c;
}}
QPushButton#mic {{
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 22px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    font-size: 18px;
}}
QPushButton#mic[listening="true"] {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}

/* ── Toggle / checkbox style ── */
QCheckBox {{
    spacing: 10px;
    color: #d1d5db;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 1px solid #4b5563;
    background: #1f2937;
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #374151;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}

/* ── List ── */
QListWidget {{
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 10px 12px;
    border-radius: 8px;
    color: #d1d5db;
}}
QListWidget::item:selected {{
    background-color: {ACCENT_SOFT};
    color: {ACCENT};
}}
QListWidget::item:hover {{
    background-color: #1f2937;
}}

/* ── Combo / spin ── */
QComboBox {{
    background-color: #0f172a;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 8px 12px;
    color: #e5e7eb;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: #111827;
    border: 1px solid #1f2937;
    selection-background-color: {ACCENT_SOFT};
    color: #e5e7eb;
}}

/* ── Slider ── */
QSlider::groove:horizontal {{
    height: 6px;
    background: #1f2937;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 3px;
}}

/* ── Status bar ── */
#statusDot {{
    font-size: 10px;
    color: #22c55e;
}}
#statusText {{
    color: #6b7280;
    font-size: 12px;
}}
"""
