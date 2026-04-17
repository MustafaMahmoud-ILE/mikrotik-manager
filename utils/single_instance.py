import ctypes
import sys

def check_single_instance(mutex_name="MikrotikManagerSingleInstanceMutex"):
    # On Windows, we can use a named mutex to ensure only one instance runs.
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        return False, mutex
    return True, mutex
