import sys
import os

# إضافة المجلد الحالي للمسار ليتمكن من استيراد الـ core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))

from hotspot_manager import HotspotManager
from ssh_manager import SSHManager

def run_test():
    router_ip = "10.0.0.1"
    print(f"Starting Core Logic Test for MikroLink (Mobile Version)")
    print(f"Target Router: {router_ip}")
    print("-" * 40)

    # 1. Test Hotspot HTTP
    print("[1/2] Testing Hotspot HTTP connection...")
    hotspot = HotspotManager(base_url=f"http://{router_ip}")
    is_up = hotspot.is_logged_in() # This just checks if we can reach the status page
    print(f"      - Status: {'REACHABLE' if is_up else 'NOT LOGGED IN / REACHABLE'}")

    # 2. Test SSH Management
    print("[2/2] Testing SSH Management connection...")
    # Default credentials from desktop version
    ssh = SSHManager(host=router_ip, username="python", password="python-2ooo")
    
    # Try to fetch some dummy data or check credentials
    # Let's try to detect if it's a MikroTik
    is_mikro = ssh.check_is_mikrotik(router_ip)
    if is_mikro:
        print(f"      - Device: MikroTik Router detected via SSH! OK")
        
        # Try to fetch quota for 'tester' or similar (change manually if needed)
        print("      - Attempting to fetch test data...")
        test_user = "python" # change to a real hotspot user for full test
        quota = ssh.get_user_quota(test_user)
        if quota:
            print(f"      - SUCCESS: Fetched quota for user '{test_user}'")
            print(f"      - Profile: {quota.get('profile')}")
            print(f"      - Used: {quota.get('bytes_total_used')} bytes")
        else:
            print(f"      - WARNING: SSH connected but couldn't find user '{test_user}'")
    else:
        print(f"      - FAILED: Could not establish SSH connection to {router_ip}")
        print(f"      - Hint: Check if SSH is enabled on the router and credentials are correct.")

    print("-" * 40)
    print("Test complete.")

if __name__ == "__main__":
    run_test()
