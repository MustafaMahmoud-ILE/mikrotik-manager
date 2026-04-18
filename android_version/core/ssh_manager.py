import paramiko
import logging
import re

logger = logging.getLogger("MikroLink.SSH")

class SSHManager:
    def __init__(self, host="10.0.0.1", port=22, username="python", password="python-2ooo"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def update_config(self, host, username=None, password=None):
        self.host = host
        if username: self.username = username
        if password: self.password = password

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Use a more aggressive timeout for mobile networks
        client.connect(self.host, port=self.port, username=self.username, password=self.password, timeout=10)
        return client

    def get_user_quota(self, hotspot_user):
        """Fetch quota with robust regex and error handling for mobile latency"""
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user print detail where name="{hotspot_user}"'
                stdin, stdout, stderr = client.exec_command(command)
                output = stdout.read().decode('utf-8', errors='ignore')
                
                limit_match = re.search(r'limit-bytes-total=(\d+)', output)
                bytes_in_match = re.search(r'bytes-in=(\d+)', output)
                bytes_out_match = re.search(r'bytes-out=(\d+)', output)
                profile_match = re.search(r'profile=([^\s,]+)', output)
                
                limit = int(limit_match.group(1)) if limit_match else 0
                bytes_in = int(bytes_in_match.group(1)) if bytes_in_match else 0
                bytes_out = int(bytes_out_match.group(1)) if bytes_out_match else 0
                profile = profile_match.group(1) if profile_match else "default"
                
                return {
                    "limit_bytes_total": limit,
                    "bytes_in": bytes_in,
                    "bytes_out": bytes_out,
                    "bytes_total_used": bytes_in + bytes_out,
                    "profile": profile
                }
        except Exception as e:
            logger.error(f"SSH Quota error: {e}")
            return None

    def change_user_profile(self, hotspot_user, new_profile):
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user set profile="{new_profile}" [find name="{hotspot_user}"]'
                client.exec_command(command)
                
                # Also force logout to apply changes immediately
                command_logout = f'/ip hotspot active remove [find user="{hotspot_user}"]'
                client.exec_command(command_logout)
                return True
        except Exception as e:
            logger.error(f"SSH Profile change error: {e}")
            return False

    def change_user_password(self, hotspot_user, new_password):
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user set password="{new_password}" [find name="{hotspot_user}"]'
                client.exec_command(command)
                return True
        except Exception as e:
            logger.error(f"SSH Password change error: {e}")
            return False

    def check_is_mikrotik(self, host):
        """Verify if a host is likely a MikroTik router (for auto-detect)"""
        try:
            with self._get_client() as client:
                stdin, stdout, stderr = client.exec_command(":put [/system resource get board-name]")
                output = stdout.read().decode('utf-8').strip()
                return len(output) > 0
        except:
            return False
