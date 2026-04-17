from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPoint, Signal, QThread
from PySide6.QtGui import QColor, QFont, QIcon, QCursor
from .styles import Colors, GLOBAL_STYLE

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None

    def create_title_bar(self, layout, title):
        title_bar = QWidget()
        title_bar.setObjectName("TitleBar")
        title_bar.setFixedHeight(40)
        
        # Enable dragging from title bar
        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(event):
            if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()

        def mouseReleaseEvent(event):
            self._drag_pos = None

        title_bar.mousePressEvent = mousePressEvent
        title_bar.mouseMoveEvent = mouseMoveEvent
        title_bar.mouseReleaseEvent = mouseReleaseEvent

        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        tb_layout.addWidget(title_label)
        tb_layout.addStretch()
        
        min_btn = QPushButton("—")
        min_btn.setFixedSize(30, 30)
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; color: {Colors.TEXT_PRIMARY}; font-weight: bold; }}
            QPushButton:hover {{ background: {Colors.DISABLED}; }}
        """)
        min_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; color: {Colors.TEXT_PRIMARY}; font-weight: bold; }}
            QPushButton:hover {{ background: {Colors.ERROR}; }}
        """)
        close_btn.clicked.connect(self.close)
        
        tb_layout.addWidget(min_btn)
        tb_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)

class LoginWorker(QThread):
    finished = Signal(bool, str, str) # success, message, username

    def __init__(self, username, password, core_manager):
        super().__init__()
        self.username = username
        self.password = password
        self.core = core_manager

    def run(self):
        try:
            # Login to hotspot via background
            if not self.core.hotspot.is_logged_in():
                # Attempt background silent login
                h_success, h_msg = self.core.hotspot.login(self.username, self.password)
                # If hotspot login fails, we still try SSH verification because Router might have different policies
            
            # Verify credentials via SSH
            is_valid = self.core.ssh.verify_user_credentials(self.username, self.password)
            if is_valid:
                self.finished.emit(True, "Login successful", self.username)
            else:
                self.finished.emit(False, "Invalid username or password, or router unreachable", self.username)
        except Exception as e:
            self.finished.emit(False, f"Error: {e}", self.username)

class LoginWindow(FramelessWindow):
    login_successful = Signal(str, str) # username, password

    def __init__(self, core_manager):
        super().__init__()
        self.core = core_manager
        self.setFixedSize(400, 500)
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_title_bar(layout, "MikroTik Manager")
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 20, 40, 40)
        
        # Logo/Title
        title = QLabel("Login")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("border: none; background: transparent;")
        content_layout.addWidget(title)
        
        content_layout.addSpacing(40)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.returnPressed.connect(self.handle_login)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        
        content_layout.addWidget(self.username_input)
        content_layout.addSpacing(15)
        content_layout.addWidget(self.password_input)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {Colors.ERROR}; border: none; background: transparent;")
        self.error_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.error_label)
        
        content_layout.addSpacing(20)
        
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.ACCENT}, stop:1 {Colors.ACCENT_HOVER});
                color: white;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.ACCENT_HOVER}, stop:1 #33e5ff);
            }}
            QPushButton:disabled {{
                background-color: {Colors.DISABLED};
                color: {Colors.TEXT_SECONDARY};
            }}
        """)
        self.login_btn.clicked.connect(self.handle_login)
        content_layout.addWidget(self.login_btn)
        
        content_layout.addStretch()
        layout.addLayout(content_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Please enter username and password")
            return
            
        self.login_btn.setEnabled(False)
        self.login_btn.setText("AUTHENTICATING...")
        self.error_label.setText("")
        
        self.worker = LoginWorker(username, password, self.core)
        self.worker.finished.connect(self.on_login_result)
        self.worker.start()

    def on_login_result(self, success, message, username):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("LOGIN")
        
        if success:
            self.error_label.setStyleSheet(f"color: {Colors.SUCCESS}; border: none; background: transparent;")
            self.error_label.setText("Success")
            self.login_successful.emit(self.username_input.text(), self.password_input.text())
        else:
            self.error_label.setStyleSheet(f"color: {Colors.ERROR}; border: none; background: transparent;")
            self.error_label.setText(message)
