import requests
import logging

logger = logging.getLogger("MikroLink.Hotspot")

class HotspotManager:
    def __init__(self, base_url="http://10.0.0.1"):
        self.base_url = base_url.rstrip("/")

    def set_base_url(self, ip):
        self.base_url = f"http://{ip}"

    def is_logged_in(self):
        try:
            # MikroTik status page check
            response = requests.get(f"{self.base_url}/status", timeout=5)
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
            response = requests.post(f"{self.base_url}/login", data=payload, timeout=7)
            
            # Simplified check for mobile
            if "invalid" in response.text.lower() or "not found" in response.text.lower():
                return False, "Invalid credentials"
                
            if "logged in" in response.text.lower() or "login successful" in response.text.lower() or response.status_code == 200:
                 return True, "Login successful"
                 
            return False, "Login failed (check network)"
        except requests.RequestException as e:
            return False, f"Network error: {str(e)}"

    def logout(self):
        try:
            requests.post(f"{self.base_url}/logout", timeout=5)
            return True
        except:
            return False
