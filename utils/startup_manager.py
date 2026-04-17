import winreg
import sys
import os

def add_to_startup(app_name="MikroTik Manager", exe_path=None):
    if exe_path is None:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to add to startup: {e}")
        return False

def remove_from_startup(app_name="MikroTik Manager"):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Failed to remove from startup: {e}")
        return False
