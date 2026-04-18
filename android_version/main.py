import os
import sys
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

# Ported core components
from core.config_manager import ConfigManager
from core.hotspot_manager import HotspotManager
from core.ssh_manager import SSHManager

class LoginScreen(MDScreen):
    pass

class DashboardScreen(MDScreen):
    pass

class SettingsScreen(MDScreen):
    pass

class MikroLinkApp(MDApp):
    connection_status = StringProperty("Disconnected")
    quota_percent = NumericProperty(0)
    quota_text = StringProperty("Fetching...")
    current_profile = StringProperty("default")
    is_auto_login = BooleanProperty(False)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        # Using the colors suggested by the user
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.primary_hue = "500"
        
        self.config = ConfigManager()
        self.is_auto_login = self.config.get_auto_login()
        self.host = self.config.get_router_ip()
        
        self.hotspot = HotspotManager(base_url=f"http://{self.host}")
        self.ssh = SSHManager(host=self.host)
        
        # OSC Server for Background Service communication
        self.server = OSCThreadServer()
        self.server.listen('localhost', port=3002, default=True)
        self.server.bind(b'/quota_update', self.on_quota_update)
        
        self.client = OSCClient('localhost', 3000)

        # Start background service on Android
        self.start_service()
        
        return Builder.load_file('ui/screens.kv')

    def start_service(self):
        if platform == 'android':
            from android import PythonService
            # In buildozer.spec, the service name is usually 'myservice'
            service_path = os.path.join(self.user_data_dir, 'service.py')
            # Actual implementation depends on buildozer version/setup
            # For now, this is a conceptual placeholder for P4A services
            pass

    def on_quota_update(self, limit, used, profile):
        self.connection_status = "Connected"
        if limit > 0:
            remain = limit - used
            self.quota_percent = int((remain / limit) * 100)
            self.quota_text = f"{(remain / 1024**3):.2f} GB left"
        else:
            self.quota_percent = 100
            self.quota_text = "Unlimited"
        self.current_profile = profile.decode()

    def handle_login(self, username, password, router_ip):
        # Update config
        self.config.set_router_ip(router_ip)
        self.host = router_ip
        self.hotspot.set_base_url(router_ip)
        self.ssh.update_config(host=router_ip)
        
        # Perform Login
        success, msg = self.hotspot.login(username, password)
        if success:
            self.config.set_credentials(username, password)
            self.root.current = "dashboard"
            self.connection_status = "Authenticating..."
            # Trigger initial sync via OSC
            self.client.send_message(b'/sync_now', [])
        else:
            MDSnackbar(text=msg).open()

    def toggle_auto_login(self, active):
        self.is_auto_login = active
        self.config.set_auto_login(active)

    def logout(self):
        self.hotspot.logout()
        self.root.current = "login"

if __name__ == '__main__':
    MikroLinkApp().run()
