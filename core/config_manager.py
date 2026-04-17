import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    def __init__(self, app_name="MikroTik Manager"):
        self.app_name = app_name
        self.app_dir = os.path.join(os.getenv('APPDATA'), self.app_name)
        self.config_path = os.path.join(self.app_dir, "config.json")
        self.key_path = os.path.join(self.app_dir, ".key")
        
        self.ensure_dirs()
        self.fernet = self._load_or_create_key()
        self.config = self._load_config()

    def ensure_dirs(self):
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)

    def _load_or_create_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            # Generate a key derived from DPAPI or just a stable local file since it's local storage
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
        return Fernet(key)

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                return self._default_config()
        return self._default_config()

    def _default_config(self):
        return {
            "auto_login": False
        }

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def set_credentials(self, username, password):
        pass # Feature disabled

    def get_credentials(self):
        return None, None

    def set_auto_login(self, state: bool):
        self.config["auto_login"] = state
        self.save()

    def get_auto_login(self) -> bool:
        return self.config.get("auto_login", False)
