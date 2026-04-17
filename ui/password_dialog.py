from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QFont
from .styles import Colors, GLOBAL_STYLE

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 400)
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.old_password = None
        self.new_password = None
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QDialog()
        self.container.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.PRIMARY_BG};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 127))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        # Title
        title_label = QLabel("Change Password")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Inputs
        self.old_pw_input = QLineEdit()
        self.old_pw_input.setPlaceholderText("Old Password")
        self.old_pw_input.setEchoMode(QLineEdit.Password)
        self.old_pw_input.setMinimumHeight(45)
        
        self.new_pw_input = QLineEdit()
        self.new_pw_input.setPlaceholderText("New Password")
        self.new_pw_input.setEchoMode(QLineEdit.Password)
        self.new_pw_input.setMinimumHeight(45)

        self.confirm_pw_input = QLineEdit()
        self.confirm_pw_input.setPlaceholderText("Confirm Password")
        self.confirm_pw_input.setEchoMode(QLineEdit.Password)
        self.confirm_pw_input.setMinimumHeight(45)

        container_layout.addWidget(self.old_pw_input)
        container_layout.addWidget(self.new_pw_input)
        container_layout.addWidget(self.confirm_pw_input)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.status_label)
        
        container_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Colors.TEXT_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.SECONDARY_BG};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        change_btn = QPushButton("Change")
        change_btn.setMinimumHeight(45)
        change_btn.setCursor(Qt.PointingHandCursor)
        change_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.ACCENT}, stop:1 {Colors.SUCCESS});
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.ACCENT_HOVER}, stop:1 #33ff99);
            }}
        """)
        change_btn.clicked.connect(self.accept_change)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(change_btn)
        container_layout.addLayout(btn_layout)

        main_layout.addWidget(self.container)

    def accept_change(self):
        old_i = self.old_pw_input.text()
        new_i = self.new_pw_input.text()
        con_i = self.confirm_pw_input.text()
        
        if not old_i or not new_i or not con_i:
            self.set_error("Please fill all fields")
            return
            
        if new_i != con_i:
            self.set_error("Passwords don't match")
            return
            
        if len(new_i) < 8:
            self.set_error("Password must be at least 8 characters")
            return
            
        self.old_password = old_i
        self.new_password = new_i
        self.accept()
        
    def set_error(self, message):
        self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-size: 12px;")
        self.status_label.setText(message)
