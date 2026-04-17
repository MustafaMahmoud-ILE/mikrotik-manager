from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QLabel, QPushButton, QProgressBar, QGridLayout, QFrame)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QColor, QFont
import time

from .styles import Colors, GLOBAL_STYLE
from .login_window import FramelessWindow
from .password_dialog import PasswordDialog

class ProfileSwitchWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, username, new_profile, password, core):
        super().__init__()
        self.username = username
        self.new_profile = new_profile
        self.password = password
        self.core = core

    def run(self):
        try:
            # Change profile out of band
            self.core.ssh.change_user_profile(self.username, self.new_profile)
            
            # Force hotspot logout
            self.core.ssh.force_logout(self.username)
            self.core.hotspot.logout()
            
            # Wait to ensure router registers disconnection
            time.sleep(2)
            
            # Relogin to apply new profile settings
            self.core.hotspot.login(self.username, self.password)
            
            self.finished.emit(True, self.new_profile)
        except Exception as e:
            self.finished.emit(False, str(e))

class DashboardWindow(FramelessWindow):
    logout_requested = Signal()

    def __init__(self, core_manager, username, password, initial_profile, initial_quota):
        super().__init__()
        self.core = core_manager
        self.username = username
        self.password = password
        self.current_profile = initial_profile
        self.current_quota = initial_quota
        
        self.setFixedSize(900, 650)
        self.setStyleSheet(GLOBAL_STYLE)
        
        # UI Elements
        self.profile_buttons = {}
        
        self.init_ui()
        self.update_quota_ui()
        self.update_profile_buttons()
        
        # Setup auto-login monitor thread and timer for quota refresh
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.check_auto_login)
        self.monitor_timer.start(30000) # every 30 seconds

        self.quota_timer = QTimer(self)
        self.quota_timer.timeout.connect(self.refresh_data)
        self.quota_timer.start(60000) # every 60 seconds

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized():
                # Use a tiny delay to ensure Windows finishes the minimize animation 
                # before we hide the window from the taskbar completely.
                QTimer.singleShot(0, self.hide)
        super().changeEvent(event)

    def init_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.create_title_bar(layout, f"MikroTik Manager - {self.username}")
        
        content = QWidget()
        content.setStyleSheet("border: none;")
        clayout = QVBoxLayout(content)
        clayout.setContentsMargins(20, 20, 20, 20)
        clayout.setSpacing(20)

        # TOP: Quota Display
        quota_frame = QFrame()
        quota_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border-radius: 8px;
            }}
        """)
        quota_frame.setFixedHeight(150)
        qlayout = QVBoxLayout(quota_frame)
        qlayout.setContentsMargins(25, 25, 25, 25)
        
        qheader_layout = QHBoxLayout()
        qtitle = QLabel("Data Quota")
        qtitle.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.qtext = QLabel("Calculating...")
        self.qtext.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;")
        
        qheader_layout.addWidget(qtitle)
        qheader_layout.addStretch()
        qheader_layout.addWidget(self.qtext)
        
        qlayout.addLayout(qheader_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 32px; font-weight: bold;")
        
        prog_layout = QHBoxLayout()
        prog_layout.addWidget(self.progress_bar)
        prog_layout.addSpacing(20)
        prog_layout.addWidget(self.percentage_label)
        
        qlayout.addLayout(prog_layout)
        clayout.addWidget(quota_frame)
        
        # MIDDLE: Profile Cards
        profiles_frame = QWidget()
        grid = QGridLayout(profiles_frame)
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0)
        
        profiles = [
            ("Balanced", "⚖️", "General purpose usage", "Balanced-Mode", 0, 0),
            ("Default", "⚙️", "Standard configuration", "Default Speed", 0, 1),
            ("Gaming", "🎮", "Optimized for gaming", "Gaming-Nitro", 1, 0),
            ("Upload", "⬆️", "Optimized for upload-heavy tasks", "Upload-King", 1, 1)
        ]
        
        for name, icon, desc, pid, row, col in profiles:
            btn = self.create_profile_btn(name, icon, desc, pid)
            self.profile_buttons[pid] = btn
            grid.addWidget(btn, row, col)
            
        clayout.addWidget(profiles_frame)
        clayout.addStretch()
        
        # BOTTOM: Controls
        controls = QFrame()
        controls.setFixedHeight(80)
        controls.setStyleSheet(f"background-color: {Colors.SECONDARY_BG}; border-radius: 8px;")
        ctl_layout = QHBoxLayout(controls)
        ctl_layout.setContentsMargins(20, 0, 20, 0)
        
        al_label = QLabel("Auto Login")
        al_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.al_btn = QPushButton()
        self.al_btn.setFixedSize(60, 30)
        self.al_btn.setCursor(Qt.PointingHandCursor)
        
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setFixedSize(80, 30)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.ERROR};
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid {Colors.ERROR};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 82, 82, 0.1);
            }}
        """)
        self.logout_btn.clicked.connect(self.perform_logout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {Colors.ACCENT};")
        
        self.update_auto_login_ui()
        self.al_btn.clicked.connect(self.toggle_auto_login)
        
        ctl_layout.addWidget(al_label)
        ctl_layout.addSpacing(10)
        ctl_layout.addWidget(self.al_btn)
        
        ctl_layout.addSpacing(20)
        ctl_layout.addWidget(self.logout_btn)
        
        ctl_layout.addStretch()
        
        ctl_layout.addWidget(self.status_label)
        ctl_layout.addStretch()
        
        pw_btn = QPushButton("🔑 Change Password")
        pw_btn.setFixedSize(200, 45)
        pw_btn.setCursor(Qt.PointingHandCursor)
        pw_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 2px solid {Colors.ACCENT};
                border-radius: 8px;
                color: {Colors.ACCENT};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(0, 173, 181, 0.1);
            }}
        """)
        pw_btn.clicked.connect(self.change_password)
        ctl_layout.addWidget(pw_btn)
        
        clayout.addWidget(controls)
        layout.addWidget(content)

    def create_profile_btn(self, name, icon, desc, pid):
        btn = QPushButton()
        btn.setFixedSize(400, 120)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Default style for non-active
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.BORDER};
                border-radius: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT};
            }}
        """)
        
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(20, 20, 20, 20)
        
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; border: none; background: transparent;")
        
        self.badge_lbls = getattr(self, 'badge_lbls', {})
        badge = QLabel("CURRENT")
        badge.setStyleSheet(f"""
            background-color: {Colors.ACCENT};
            color: white;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: bold;
        """)
        badge.hide()
        self.badge_lbls[pid] = badge
        
        top.addWidget(icon_lbl)
        top.addSpacing(10)
        top.addWidget(name_lbl)
        top.addStretch()
        top.addWidget(badge)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; border: none; background: transparent;")
        
        layout.addLayout(top)
        layout.addWidget(desc_lbl)
        
        btn.clicked.connect(lambda: self.switch_profile(pid))
        
        return btn

    def update_profile_buttons(self):
        # If current profile is not in our 4 presets, enable all buttons
        preset_ids = self.profile_buttons.keys()
        
        for pid, btn in self.profile_buttons.items():
            if pid == self.current_profile:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.BORDER};
                        border: 2px solid {Colors.DISABLED};
                        border-radius: 12px;
                    }}
                """)
                btn.setCursor(Qt.ForbiddenCursor)
                self.badge_lbls[pid].show()
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.SECONDARY_BG};
                        border: 2px solid {Colors.BORDER};
                        border-radius: 12px;
                    }}
                    QPushButton:hover {{
                        border-color: {Colors.ACCENT};
                    }}
                """)
                btn.setCursor(Qt.PointingHandCursor)
                self.badge_lbls[pid].hide()

    def update_quota_ui(self):
        from core.quota_manager import QuotaManager
        data = QuotaManager.calculate_quota(self.current_quota)
        
        if data["is_unlimited"]:
            self.qtext.setText(f"{data['left_str']} left")
            self.progress_bar.setValue(100)
            self.percentage_label.setText("∞")
        else:
            self.qtext.setText(f"{data['left_str']} of {data['limit_str']} left")
            self.progress_bar.setValue(data["percentage"])
            self.percentage_label.setText(f"{data['percentage']}%")

    def toggle_auto_login(self):
        current = self.core.config.get_auto_login()
        self.core.config.set_auto_login(not current)
        self.update_auto_login_ui()

    def update_auto_login_ui(self):
        enabled = self.core.config.get_auto_login()
        if enabled:
            self.al_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.SUCCESS};
                    border-radius: 15px;
                    border: 2px solid #555555;
                }}
            """)
            self.status_label.setText("Auto-login active")
        else:
            self.al_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border-radius: 15px;
                    border: 2px solid #555555;
                }}
            """)
            self.status_label.setText("")

    def switch_profile(self, pid):
        if pid == self.current_profile:
            return
            
        # Disable GUI and show loading state
        for btn in self.profile_buttons.values():
            btn.setEnabled(False)
        self.status_label.setText(f"Switching to {pid}...")
        
        self.switch_worker = ProfileSwitchWorker(self.username, pid, self.password, self.core)
        self.switch_worker.finished.connect(self.on_switch_complete)
        self.switch_worker.start()

    def on_switch_complete(self, success, new_pid_or_err):
        for btn in self.profile_buttons.values():
            btn.setEnabled(True)
            
        if success:
            self.current_profile = new_pid_or_err
            self.update_profile_buttons()
            self.status_label.setText(f"Profile updated to {new_pid_or_err}")
        else:
            self.status_label.setStyleSheet(f"color: {Colors.ERROR};")
            self.status_label.setText(f"Error: {new_pid_or_err}")

    def refresh_data(self):
        """Periodically sync profile and quota from the router"""
        try:
            # Sync Quota
            self.current_quota = self.core.ssh.get_user_quota(self.username)
            self.update_quota_ui()
            
            # Sync Profile (in case changed by admin elsewhere)
            new_profile = self.core.ssh.get_user_profile(self.username)
            if new_profile and new_profile != self.current_profile:
                self.current_profile = new_profile
                self.update_profile_buttons()
                self.status_label.setText("Profile synced from router")
        except Exception as e:
            print(f"Data refresh error: {e}")

    def check_auto_login(self):
        if self.core.config.get_auto_login():
            if not self.core.hotspot.is_logged_in():
                self.status_label.setText("Re-authenticating session...")
                # Best effort headless login
                self.core.hotspot.login(self.username, self.password)
                self.status_label.setText("Session restored via Auto Login")

    def change_password(self):
        dlg = PasswordDialog(self)
        if dlg.exec():
            # Old pw must match router
            if not self.core.ssh.verify_user_credentials(self.username, dlg.old_password):
                self.status_label.setStyleSheet(f"color: {Colors.ERROR};")
                self.status_label.setText("Invalid old password.")
                return
                
            if self.core.ssh.change_user_password(self.username, dlg.new_password):
                self.password = dlg.new_password
                self.core.config.set_credentials(self.username, dlg.new_password)
                self.status_label.setStyleSheet(f"color: {Colors.SUCCESS};")
                self.status_label.setText("Password changed successfully.")
            else:
                self.status_label.setStyleSheet(f"color: {Colors.ERROR};")
                self.status_label.setText("Failed to change password on router.")

    def perform_logout(self):
        self.status_label.setText("Logging out...")
        
        # Stop background polling timers to prevent hanging
        self.monitor_timer.stop()
        self.quota_timer.stop()
        
        # Drop SSH session first while the firewall still permits communication
        self.core.ssh.force_logout(self.username)
        
        # Drop Hotspot HTTP authentication last
        self.core.hotspot.logout()
        
        self.logout_requested.emit()
