import os
import sys
import ctypes
from ctypes import wintypes

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', ctypes.c_char_p),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('hProcess', wintypes.HANDLE),
        ('hThread', wintypes.HANDLE),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD),
    ]

def launch_on_interactive_desktop():
    cwd = os.path.dirname(os.path.abspath(__file__))
    songrip_exe = os.path.join(cwd, "SongRip.exe")
    if os.path.exists(songrip_exe):
        cmd = f'"{songrip_exe}"'
    else:
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        cmd = f'"{python_exe}" "{os.path.join(cwd, "app.py")}"'
    
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    si.lpDesktop = "WinSta0\\Default"
    pi = PROCESS_INFORMATION()

    # 0x08000000 = CREATE_NO_WINDOW
    flags = 0x08000000
    
    success = ctypes.windll.kernel32.CreateProcessW(
        None,
        cmd,
        None,
        None,
        False,
        flags,
        None,
        cwd,
        ctypes.byref(si),
        ctypes.byref(pi)
    )
    if success:
        print(f"Successfully launched CassetteCat on user interactive desktop! PID: {pi.dwProcessId}")
        ctypes.windll.kernel32.CloseHandle(pi.hProcess)
        ctypes.windll.kernel32.CloseHandle(pi.hThread)
        return True
    else:
        err = ctypes.windll.kernel32.GetLastError()
        print(f"Fallback direct start, error code: {err}")
        # Fallback to normal subprocess
        import subprocess
        subprocess.Popen([python_exe, os.path.join(cwd, "app.py")], cwd=cwd)
        return True

if __name__ == "__main__":
    launch_on_interactive_desktop()
