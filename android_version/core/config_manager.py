import os
import json
from cryptography.fernet import Fernet

# Flexible imports to support both Android and Desktop IDE environments
try:
    from kivy.storage.jsonstore import JsonStore
    from kivy.utils import platform
except ImportError:
    # Development fallbacks for Desktop
    platform = 'desktop'
    class JsonStore:
        def __init__(self, path): pass
        def put(self, *args, **kwargs): pass
        def get(self, *args): return {}
        def exists(self, *args): return False
        def clear(self): pass

class ConfigManager:
    def __init__(self, app_name="MikroLink"):
        self.app_name = app_name
        
        # Determine the user data directory based on platform
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                self.data_dir = app_storage_path()
            except (ImportError, ModuleNotFoundError):
                self.data_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            # Fallback for development on desktop
            self.data_dir = os.path.join(os.path.expanduser("~"), f".{self.app_name.lower()}")
            
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.store = JsonStore(os.path.join(self.data_dir, "config.json"))
        self.key_path = os.path.join(self.data_dir, ".key")
        self.fernet = self._load_or_create_key()

    def _load_or_create_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
        return Fernet(key)

    def set_credentials(self, username, password):
        encrypted_pw = self.fernet.encrypt(password.encode()).decode()
        self.store.put('auth', username=username, password=encrypted_pw)

    def get_credentials(self):
        if not self.store.exists('auth'):
            return None, None
        
        auth = self.store.get('auth')
        username = auth['username']
        try:
            decrypted_pw = self.fernet.decrypt(auth['password'].encode()).decode()
            return username, decrypted_pw
        except:
            return username, None

    def set_auto_login(self, state: bool):
        self.store.put('settings', auto_login=state)

    def get_auto_login(self) -> bool:
        if self.store.exists('settings'):
            return self.store.get('settings').get('auto_login', False)
        return False

    def set_router_ip(self, ip: str):
        self.store.put('network', router_ip=ip)

    def get_router_ip(self) -> str:
        if self.store.exists('network'):
            return self.store.get('network').get('router_ip', "10.0.0.1")
        return "10.0.0.1"

    def clear_all(self):
        self.store.clear()
