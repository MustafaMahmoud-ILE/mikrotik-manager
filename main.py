import sys
import os
import shutil
import ctypes
import logging
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

from core.ssh_manager import SSHManager
from core.hotspot_manager import HotspotManager
from core.config_manager import ConfigManager
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow
from utils.single_instance import check_single_instance
from utils.startup_manager import add_to_startup
from utils.shortcut_manager import create_shortcuts
from utils.tray_manager import TrayManager
# Configure Logging
if getattr(sys, 'frozen', False):
    # If running as an EXE
    app_base_path = os.path.dirname(sys.executable)
else:
    # If running as a script
    app_base_path = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(app_base_path, "mikro.log")
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MikroTikManager")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # Prefer _MEIPASS (onefile), fallback to executable dir (onedir)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class CoreManager:
    def __init__(self):
        self.ssh = SSHManager()
        self.hotspot = HotspotManager()
        self.config = ConfigManager()

class MikroTikApp:
    def __init__(self):
        # Set Windows AppUserModelID to ensure taskbar icon shows correctly
        try:
            myappid = u'mycompany.mikrotikmanager.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        self.app = QApplication(sys.argv)
        
        # Set Global Window Icon
        icon_path = resource_path(os.path.join('ui', 'assets', 'mikrotik-light.png'))
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
            
        self.core = CoreManager()
        self.login_win = None
        self.dashboard_win = None
        
        # Initialize Tray (but keep hidden until logged in)
        self.tray = TrayManager(icon_path, self.app)
        self.tray.show_requested.connect(self.restore_window)
        self.tray.exit_requested.connect(self.app.quit)

    def run(self):
        # Single Instance Check
        is_first, mutex = check_single_instance()
        if not is_first:
            # We don't show a warning here to keep it subtle
            sys.exit(0)
            
        # Create Login Window first to establish GUI context
        self.login_win = LoginWindow(self.core)
        self.login_win.login_successful.connect(self.show_dashboard)

        # Check for saved credentials
        saved_user, saved_pw = self.core.config.get_credentials()
        if saved_user and saved_pw:
            self.login_win.username_input.setText(saved_user)
            self.login_win.password_input.setText(saved_pw)
            self.login_win.show()
            self.login_win.handle_login()
        else:
            self.login_win.show()
            
        # Now that a window is ACTIVE, perform installation checks safely
        QTimer.singleShot(1500, self.first_run_checks)
            
        sys.exit(self.app.exec())

    def first_run_checks(self):
        # Only perform install checks when frozen (EXE)
        if not getattr(sys, 'frozen', False):
            return
            
        apdata = os.getenv('APPDATA')
        if not apdata:
            return
            
        app_data_path = os.path.normcase(os.path.normpath(os.path.join(apdata, 'MikroTik Manager')))
        exe_path = os.path.normcase(os.path.normpath(sys.executable))
        
        # If we are not running from the install dir
        if not exe_path.startswith(app_data_path):
            try:
                reply = QMessageBox.question(self.login_win, 'Installation', 
                                             'Do you want to install this application to your system?',
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if not os.path.exists(app_data_path):
                        os.makedirs(app_data_path)
                    
                    source_dir = os.path.dirname(exe_path)
                    target_exe = os.path.join(app_data_path, os.path.basename(exe_path))
                    
                    # Copy all files and directories (especially _internal) to the install location
                    # We use a loop to avoid issues with copying the folder into itself if someone 
                    # ran it from AppData parent.
                    for item in os.listdir(source_dir):
                        src_item = os.path.join(source_dir, item)
                        dst_item = os.path.join(app_data_path, item)
                        
                        if os.path.isdir(src_item):
                            if os.path.exists(dst_item):
                                shutil.rmtree(dst_item)
                            shutil.copytree(src_item, dst_item)
                        else:
                            shutil.copy2(src_item, dst_item)
                    
                    # Create shortcuts on Desktop and Start Menu
                    create_shortcuts(target_exe)
                    
                    startup_reply = QMessageBox.question(self.login_win, 'Startup', 
                                         'Do you want this application to start automatically with Windows?',
                                         QMessageBox.Yes | QMessageBox.No)
                    if startup_reply == QMessageBox.Yes:
                        add_to_startup(exe_path=target_exe)
                        
                    QMessageBox.information(self.login_win, 'Success', 'Installation complete. Please run the application from the Start Menu.')
                    sys.exit(0)
            except Exception as e:
                logger.error(f"Installation check failed: {e}")

    def show_dashboard(self, username, password):
        # Save credentials 
        self.core.config.set_credentials(username, password)
        
        # Fetch initial data before showing dashboard
        initial_profile = self.core.ssh.get_user_profile(username)
        initial_quota = self.core.ssh.get_user_quota(username)
        
        self.dashboard_win = DashboardWindow(self.core, username, password, initial_profile, initial_quota)
        self.dashboard_win.logout_requested.connect(self.handle_logout)
        
        if self.login_win:
            self.login_win.close()
        
        # Show tray when dashboard is active
        self.tray.show()
        self.dashboard_win.show()

    def restore_window(self):
        if self.dashboard_win:
            self.dashboard_win.showNormal()
            self.dashboard_win.activateWindow()
        elif self.login_win:
            self.login_win.showNormal()
            self.login_win.activateWindow()

    def handle_logout(self):
        if self.dashboard_win:
            self.dashboard_win.close()
        # Hide tray on logout
        self.tray.hide()
        self.login_win = LoginWindow(self.core)
        self.login_win.login_successful.connect(self.show_dashboard)
        self.login_win.show()

if __name__ == "__main__":
    try:
        app = MikroTikApp()
        app.run()
    except Exception as e:
        logger.exception("Application crashed on startup")
        # Ensure the user sees the error before closure
        try:
            QMessageBox.critical(None, "Fatal Error", f"The application encountered a fatal error and must close.\nDetails saved to mikro.log\n\nError: {e}")
        except:
            pass
        sys.exit(1)
