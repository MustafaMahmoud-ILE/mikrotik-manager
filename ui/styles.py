class Colors:
    PRIMARY_BG = "#1a1a1a"
    SECONDARY_BG = "#252525"
    ACCENT = "#00adb5"
    ACCENT_HOVER = "#00c9d2"
    TEXT_PRIMARY = "#eeeeee"
    TEXT_SECONDARY = "#a0a0a0"
    BORDER = "#252525"  # Darker border color
    SUCCESS = "#00e676"
    WARNING = "#ff9800"
    ERROR = "#ff5252"
    DISABLED = "#404040"

GLOBAL_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {Colors.PRIMARY_BG};
    color: {Colors.TEXT_PRIMARY};
    border-radius: 12px;
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QLineEdit {{
    background-color: {Colors.SECONDARY_BG};
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    padding: 0 15px;
    height: 45px;
    font-size: 14px;
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QLineEdit:focus {{
    border: 1px solid {Colors.ACCENT};
}}

QPushButton {{
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QProgressBar {{
    background-color: {Colors.PRIMARY_BG};
    border-radius: 12px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.ACCENT}, stop:1 {Colors.SUCCESS});
    border-radius: 12px;
}}

/* Main container for frameless windows */
#MainWidget {{
    background-color: {Colors.PRIMARY_BG};
    border: 1px solid {Colors.BORDER};
    border-radius: 12px;
}}

/* Custom Title Bar specific generic styles */
#TitleBar {{
    background-color: {Colors.SECONDARY_BG};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border: none;
}}
"""
