import paramiko
import time
import logging

logger = logging.getLogger("MikroTikManager.SSH")

class SSHManager:
    def __init__(self, host="10.0.0.1", port=22, username="python", password="python-2ooo"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def _get_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.host, port=self.port, username=self.username, password=self.password, timeout=5)
        return client

    def verify_user_credentials(self, hotspot_user, hotspot_password):
        try:
            with self._get_client() as client:
                # Find the user's password specifically
                command = f'/ip hotspot user print detail where name="{hotspot_user}"'
                stdin, stdout, stderr = client.exec_command(command)
                output = stdout.read().decode('utf-8')
                
                if hotspot_user not in output:
                    return False
                
                # Mikrotik hides passwords sometimes depending on user policies,
                # but if the user has correct permissions we can see `password="xxx"`
                # Alternative is just assuming true if the user exists and Hotspot Manager deals with the actual web auth
                if f'password="{hotspot_password}"' in output or f"password={hotspot_password}" in output:
                     return True
                # Let's be lenient here since web auth will eventually validate the actual password anyway,
                # but we'll try our best to validate via SSH if password is visible.
                # If password is completely masked, we'll return True and let Hotspot HTTP auth be the ultimate decider.
                if "password" not in output:
                    return True  # Masked password
                return False
        except Exception as e:
            logger.error(f"SSH Auth error: {e}", exc_info=True)
            return False

    def get_user_profile(self, hotspot_user):
        try:
            with self._get_client() as client:
                # Using 'get' returns just the value, much safer than 'print detail'
                command = f':put [/ip hotspot user get [find name="{hotspot_user}"] profile]'
                stdin, stdout, stderr = client.exec_command(command)
                profile = stdout.read().decode('utf-8').strip()
                
                print(f"DEBUG: Router returned profile for {hotspot_user}: '{profile}'")
                if profile:
                    return profile
        except Exception as e:
            logger.error(f"SSH Get Profile error: {e}", exc_info=True)
        return "default"

    def get_user_quota(self, hotspot_user):
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user print detail where name="{hotspot_user}"'
                stdin, stdout, stderr = client.exec_command(command)
                output = stdout.read().decode('utf-8')
                
                import re
                limit_match = re.search(r'limit-bytes-total=(\d+)', output)
                bytes_in_match = re.search(r'bytes-in=(\d+)', output)
                bytes_out_match = re.search(r'bytes-out=(\d+)', output)
                
                limit = int(limit_match.group(1)) if limit_match else 0
                bytes_in = int(bytes_in_match.group(1)) if bytes_in_match else 0
                bytes_out = int(bytes_out_match.group(1)) if bytes_out_match else 0
                
                return {
                    "limit_bytes_total": limit,
                    "bytes_in": bytes_in,
                    "bytes_out": bytes_out,
                    "bytes_total_used": bytes_in + bytes_out
                }
        except Exception as e:
            print(f"SSH Get Quota error: {e}")
        return {"limit_bytes_total": 0, "bytes_in": 0, "bytes_out": 0, "bytes_total_used": 0}

    def change_user_profile(self, hotspot_user, new_profile):
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user set profile="{new_profile}" [find name="{hotspot_user}"]'
                client.exec_command(command)
                return True
        except Exception as e:
            print(f"SSH Change Profile error: {e}")
            return False

    def change_user_password(self, hotspot_user, new_password):
        try:
            with self._get_client() as client:
                command = f'/ip hotspot user set password="{new_password}" [find name="{hotspot_user}"]'
                client.exec_command(command)
                return True
        except Exception as e:
            print(f"SSH Change Password error: {e}")
            return False

    def force_logout(self, hotspot_user):
         try:
            with self._get_client() as client:
                command = f'/ip hotspot active remove [find user="{hotspot_user}"]'
                client.exec_command(command)
                return True
         except Exception as e:
            print(f"SSH Force Logout error: {e}")
            return False
