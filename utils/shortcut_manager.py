import os
import subprocess
import sys

def create_shortcuts(exe_path, app_name="MikroTik Manager"):
    """
    Creates Windows shortcuts on the Desktop and in the Start Menu using PowerShell.
    """
    if not getattr(sys, 'frozen', False):
        return # Don't create shortcuts during development
        
    # Get standard Windows paths
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
    
    # Ensure paths exist
    targets = [desktop, start_menu]
    
    for folder in targets:
        if not os.path.exists(folder):
            continue
            
        shortcut_path = os.path.join(folder, f"{app_name}.lnk")
        work_dir = os.path.dirname(exe_path)
        
        # PowerShell command to create a COM shortcut object
        ps_command = f"""
        $s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}');
        $s.TargetPath = '{exe_path}';
        $s.WorkingDirectory = '{work_dir}';
        $s.IconLocation = '{exe_path},0';
        $s.Save();
        """
        
        try:
            subprocess.run(["powershell", "-Command", ps_command], 
                           capture_output=True, 
                           check=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            print(f"Failed to create shortcut in {folder}: {e}")
