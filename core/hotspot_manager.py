import requests
import json
import logging

logger = logging.getLogger("MikroTikManager.Hotspot")

class HotspotManager:
    def __init__(self, base_url="http://10.0.0.1"):
        self.base_url = base_url.rstrip("/")

    def is_logged_in(self):
        # Hotspot typically redirects traffic to login page if not authenticated
        # MikroTik's /status page reveals if logged in
        try:
            response = requests.get(f"{self.base_url}/status", timeout=3)
            # Standard routerOS status page will have "logged in" or similar context
            if "logged in" in response.text.lower() or "logout" in response.text.lower():
                return True
            return False
        except requests.RequestException:
            return False

    def login(self, username, password):
        try:
            payload = {
                "username": username,
                "password": password
            }
            # MikroTik typically uses form URL encoded payload
            response = requests.post(f"{self.base_url}/login", data=payload, timeout=5)
            if "invalid username" in response.text.lower() or "invalid password" in response.text.lower() or "not found" in response.text.lower():
                return False, "Invalid credentials"
            return True, "Login successful"
        except requests.RequestException as e:
            msg = f"Connection error: {e}"
            logger.error(msg, exc_info=True)
            return False, msg
    def logout(self):
        try:
            response = requests.post(f"{self.base_url}/logout", timeout=3)
            return True
        except requests.RequestException as e:
            logger.error(f"Hotspot logout error: {e}", exc_info=True)
            return False
