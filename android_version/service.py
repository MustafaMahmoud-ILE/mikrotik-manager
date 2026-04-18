import time
import os
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import logging

# Logic adaptation for mobile
from core.ssh_manager import SSHManager
from core.hotspot_manager import HotspotManager
from core.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MikroLink.Service")

CLIENT = OSCClient('localhost', 3002)
SERVER = OSCThreadServer()

class MikroLinkService:
    def __init__(self):
        self.config = ConfigManager()
        self.host = self.config.get_router_ip()
        self.ssh = SSHManager(host=self.host)
        self.hotspot = HotspotManager(base_url=f"http://{self.host}")
        
        self.running = True
        self.last_quota_sync = 0
        self.sync_interval = 60  # seconds
        self.check_interval = 5   # connectivity check
        
        SERVER.listen('localhost', port=3000, default=True)
        SERVER.bind(b'/stop', self.stop)
        SERVER.bind(b'/sync_now', self.sync_data)

    def stop(self, *args):
        self.running = False

    def sync_data(self, *args):
        username, password = self.config.get_credentials()
        if not username: return
        
        quota = self.ssh.get_user_quota(username)
        if quota:
            # Send to UI
            CLIENT.send_message(b'/quota_update', [
                quota['limit_bytes_total'],
                quota['bytes_total_used'],
                quota['profile'].encode()
            ])
            self.last_quota_sync = time.time()
            self.update_notification(f"Connected • {quota['profile']}")

    def update_notification(self, text):
        # On Android, we'd use jnius to update the foreground service notification.
        # For now, we log it. The buildozer/p4a recipe handles the entry point.
        logger.info(f"NOTIFICATION UPDATE: {text}")
        try:
            from android.runnable import run_on_ui_thread
            # Placeholder for Android-specific notification update logic
            pass
        except ImportError:
            pass

    def run(self):
        logger.info("Service started")
        while self.running:
            try:
                username, password = self.config.get_credentials()
                auto_login = self.config.get_auto_login()
                
                if username and auto_login:
                    # Check connection
                    logged_in = self.hotspot.is_logged_in()
                    
                    if not logged_in:
                        logger.info("Session dropped. Re-authenticating...")
                        success, msg = self.hotspot.login(username, password)
                        if success:
                            self.update_notification("Connected (Auto-relogin)")
                            self.sync_data()
                        else:
                            self.update_notification("Disconnected • Retrying...")
                    
                    # Periodic sync
                    if time.time() - self.last_quota_sync > self.sync_interval:
                        self.sync_data()
                        
            except Exception as e:
                logger.error(f"Service loop error: {e}")
                
            time.sleep(self.check_interval)

if __name__ == '__main__':
    service = MikroLinkService()
    service.run()
