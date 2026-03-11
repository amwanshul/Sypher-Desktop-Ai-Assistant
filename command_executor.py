"""
command_executor.py  v4
All commands audited and fixed for Windows.
- open_browser     : opens default browser (not hardcoded to Chrome)
- close_app        : smart — detects what's running, closes the top app
- open_desktop     : fixed broken PowerShell escape — uses simple explorer path
- open_downloads   : creates folder if it doesn't exist
- open_whatsapp    : added Microsoft Store (WindowsApps) path
- open_vscode      : added PROGRAMFILES(X86) and PATH fallback
- open_excel/word/ppt : added Office 365 Click-to-Run registry lookup
"""

import os
import platform
import subprocess
import datetime
import time

OS = platform.system()   # "Windows" | "Darwin" | "Linux"


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _open_url(url: str) -> bool:
    """Open a URL in the system default browser."""
    try:
        if OS == "Windows":
            os.system(f'start "" "{url}"')
        elif OS == "Darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
        return True
    except Exception as e:
        print(f"[Executor] _open_url error: {e}")
        return False


def _open_folder(path: str) -> bool:
    """Open a folder in the system file manager."""
    try:
        os.makedirs(path, exist_ok=True)   # create if missing (e.g. Downloads)
        if OS == "Windows":
            os.system(f'explorer "{path}"')
        elif OS == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        print(f"[Executor] _open_folder error: {e}")
        return False


def _launch(exe_path: str) -> bool:
    """Launch an executable by full path."""
    try:
        subprocess.Popen([exe_path])
        return True
    except Exception as e:
        print(f"[Executor] _launch error: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# Windows: find Office via registry (handles 365 / Click-to-Run)
# ─────────────────────────────────────────────────────────────
def _win_find_office_exe(exe_name: str) -> str | None:
    """
    Look up the Office install root in the Windows registry.
    Works for Office 2013 / 2016 / 2019 / 365 (Click-to-Run).
    Returns full path to exe or None.
    """
    # Registry keys tried in order
    reg_paths = [
        r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration",
        r"SOFTWARE\WOW6432Node\Microsoft\Office\ClickToRun\Configuration",
    ]
    try:
        import winreg
        for reg_path in reg_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                install_path, _ = winreg.QueryValueEx(key, "InstallationPath")
                winreg.CloseKey(key)
                if install_path:
                    candidate = os.path.join(install_path, "root", "Office16", exe_name)
                    if os.path.exists(candidate):
                        return candidate
            except (FileNotFoundError, OSError):
                continue
    except ImportError:
        pass

    # Fallback: hardcoded common paths (Office 2013–2021)
    roots = [
        r"C:\Program Files\Microsoft Office\root\Office16",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16",
        r"C:\Program Files\Microsoft Office\Office16",
        r"C:\Program Files (x86)\Microsoft Office\Office16",
        r"C:\Program Files\Microsoft Office\Office15",
        r"C:\Program Files (x86)\Microsoft Office\Office15",
    ]
    for root in roots:
        full = os.path.join(root, exe_name)
        if os.path.exists(full):
            return full
    return None


def _win_open_office(exe_name: str, fallback_cmd: str) -> bool:
    path = _win_find_office_exe(exe_name)
    if path:
        return _launch(path)
    # Last resort: shell association (works if Office registered in PATH/shell)
    os.system(f"start {fallback_cmd}")
    return True


# ─────────────────────────────────────────────────────────────
# Windows volume / mute  (WScript SendKeys — zero dependencies)
# VK codes:  173 = mute toggle   174 = vol down   175 = vol up
# ─────────────────────────────────────────────────────────────
def _win_send_vk(code: int):
    os.system(
        f'powershell -NoProfile -Command '
        f'"$wsh = New-Object -ComObject WScript.Shell; '
        f'$wsh.SendKeys([char]{code})"'
    )


def _win_volume_up():
    for _ in range(5):        # 5 presses ≈ +10%
        _win_send_vk(175)
        time.sleep(0.04)


def _win_volume_down():
    for _ in range(5):        # 5 presses ≈ -10%
        _win_send_vk(174)
        time.sleep(0.04)


def _win_mute():
    _win_send_vk(173)


# ─────────────────────────────────────────────────────────────
# Windows screenshot
# Method 1: PowerShell System.Windows.Forms  (always available)
# Method 2: Pillow ImageGrab
# Method 3: pyautogui
# ─────────────────────────────────────────────────────────────
def _win_screenshot(filepath: str) -> bool:
    ps_path = filepath.replace("\\", "/")
    ps_cmd = "; ".join([
        "Add-Type -AssemblyName System.Windows.Forms",
        "Add-Type -AssemblyName System.Drawing",
        "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds",
        "$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)",
        "$g = [System.Drawing.Graphics]::FromImage($bmp)",
        "$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size, [System.Drawing.CopyPixelOperation]::SourceCopy)",
        f"$bmp.Save('{ps_path}', [System.Drawing.Imaging.ImageFormat]::Png)",
        "$g.Dispose()",
        "$bmp.Dispose()",
    ])
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive",
             "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and os.path.exists(filepath):
            print(f"[Executor] Screenshot saved -> {filepath}")
            return True
        if result.stderr:
            print(f"[Executor] PowerShell error: {result.stderr.strip()}")
    except Exception as e:
        print(f"[Executor] PowerShell screenshot failed: {e}")

    try:
        from PIL import ImageGrab
        ImageGrab.grab(all_screens=True).save(filepath)
        print(f"[Executor] Screenshot saved (Pillow) -> {filepath}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"[Executor] Pillow failed: {e}")

    try:
        import pyautogui
        pyautogui.screenshot(filepath)
        print(f"[Executor] Screenshot saved (pyautogui) -> {filepath}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"[Executor] pyautogui failed: {e}")

    print("[Executor] All screenshot methods failed.")
    return False


# ─────────────────────────────────────────────────────────────
# Windows close_app — smart process detection
# Checks what is actually running, closes the highest-priority app
# ─────────────────────────────────────────────────────────────

# Ordered by how commonly apps are open — topmost gets closed first
_WIN_CLOSE_PRIORITY = [
    "chrome.exe",
    "firefox.exe",
    "msedge.exe",
    "notepad.exe",
    "notepad++.exe",
    "Code.exe",             # VS Code
    "EXCEL.EXE",
    "WINWORD.EXE",
    "POWERPNT.EXE",
    "Spotify.exe",
    "WhatsApp.exe",
    "Telegram.exe",
    "Discord.exe",
    "Zoom.exe",
    "Teams.exe",
    "vlc.exe",
    "mspaint.exe",
    "calculator.exe",
    "ApplicationFrameHost.exe",  # UWP Calculator on Win10/11
]


def _get_running_procs_windows() -> set:
    """Return lowercase set of running process names."""
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        procs = set()
        for line in result.stdout.strip().splitlines():
            parts = line.strip('"').split('","')
            if parts:
                procs.add(parts[0].lower())
        return procs
    except Exception:
        return set()


def _close_app_windows() -> bool:
    running = _get_running_procs_windows()
    for exe in _WIN_CLOSE_PRIORITY:
        if exe.lower() in running:
            os.system(f'taskkill /F /IM "{exe}"')
            print(f"[Executor] Closed {exe}")
            return True
    print("[Executor] No recognised closeable app found running.")
    return False


# ═════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═════════════════════════════════════════════════════════════

def open_browser():
    """Open the system default browser."""
    # Use a URL so Windows opens whatever the user's DEFAULT browser is
    # (not hardcoded to Chrome which may not be installed)
    return _open_url("https://www.google.com")


def open_calculator():
    if OS == "Windows":
        os.system("calc")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Calculator"])
    else:
        subprocess.Popen(["gnome-calculator"])
    return True


def open_file_explorer():
    if OS == "Windows":
        os.system("explorer")
    elif OS == "Darwin":
        subprocess.Popen(["open", os.path.expanduser("~")])
    else:
        subprocess.Popen(["xdg-open", os.path.expanduser("~")])
    return True


def open_notepad():
    if OS == "Windows":
        os.system("notepad")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "TextEdit"])
    else:
        for editor in ["gedit", "mousepad", "xed", "kate", "nano"]:
            try:
                subprocess.Popen([editor])
                return True
            except FileNotFoundError:
                continue
    return True


def open_task_manager():
    if OS == "Windows":
        os.system("taskmgr")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Activity Monitor"])
    else:
        for app in ["gnome-system-monitor", "xfce4-taskmanager", "ksysguard"]:
            try:
                subprocess.Popen([app])
                return True
            except FileNotFoundError:
                continue
    return True


def close_app():
    """
    Closes the most relevant currently-open application.
    Windows: checks running processes against priority list.
    macOS: closes the frontmost window via AppleScript.
    Linux: closes the focused window via xdotool.
    """
    if OS == "Windows":
        return _close_app_windows()
    elif OS == "Darwin":
        try:
            script = (
                'tell application "System Events" to set frontApp to '
                'name of first application process whose frontmost is true; '
                'tell application frontApp to quit'
            )
            subprocess.call(["osascript", "-e", script])
            return True
        except Exception as e:
            print(f"[Executor] macOS close error: {e}")
            return False
    else:
        try:
            subprocess.call(["xdotool", "getactivewindow", "windowclose"])
            return True
        except FileNotFoundError:
            subprocess.call(["pkill", "-f", "chrome"])
            return True


def shutdown():
    if OS == "Windows":
        os.system("shutdown /s /t 5")
    else:
        subprocess.call(["sudo", "shutdown", "-h", "now"])
    return True


def restart():
    if OS == "Windows":
        os.system("shutdown /r /t 5")
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-r", "now"])
    else:
        subprocess.call(["sudo", "reboot"])
    return True


def volume_up():
    if OS == "Windows":
        _win_volume_up()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e",
            "set volume output volume (output volume of (get volume settings) + 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    return True


def volume_down():
    if OS == "Windows":
        _win_volume_down()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e",
            "set volume output volume (output volume of (get volume settings) - 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    return True


def mute():
    if OS == "Windows":
        _win_mute()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output muted true"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
    return True


def take_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(os.path.expanduser("~"), f"screenshot_{timestamp}.png")
    if OS == "Windows":
        return _win_screenshot(filepath)
    elif OS == "Darwin":
        subprocess.call(["screencapture", filepath])
        return True
    else:
        try:
            subprocess.call(["scrot", filepath])
            return True
        except FileNotFoundError:
            try:
                from PIL import ImageGrab
                ImageGrab.grab().save(filepath)
                return True
            except Exception:
                return False


def greet():
    return True


# ── Web & Search ──────────────────────────────────────────────

def search_google():
    return _open_url("https://www.google.com")


def open_youtube():
    return _open_url("https://www.youtube.com")


def open_gmail():
    return _open_url("https://mail.google.com")


# ── File & Folder ─────────────────────────────────────────────

def open_downloads():
    path = os.path.join(os.path.expanduser("~"), "Downloads")
    return _open_folder(path)


def open_desktop():
    """Opens the Desktop folder in a file manager window."""
    path = os.path.join(os.path.expanduser("~"), "Desktop")
    return _open_folder(path)


def create_folder():
    """Creates a new timestamped folder on the Desktop and opens it."""
    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop     = os.path.join(os.path.expanduser("~"), "Desktop")
    new_folder  = os.path.join(desktop, f"New_Folder_{timestamp}")
    try:
        os.makedirs(new_folder, exist_ok=True)
        print(f"[Executor] Folder created -> {new_folder}")
        return _open_folder(desktop)
    except Exception as e:
        print(f"[Executor] create_folder error: {e}")
        return False


# ── Apps ──────────────────────────────────────────────────────

def open_spotify():
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("APPDATA", ""),
                         "Spotify", "Spotify.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Microsoft", "WindowsApps", "Spotify.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                return _launch(p)
        return _open_url("https://open.spotify.com")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Spotify"])
    else:
        try:
            subprocess.Popen(["spotify"])
        except FileNotFoundError:
            return _open_url("https://open.spotify.com")
    return True


def open_whatsapp():
    if OS == "Windows":
        paths = [
            # Classic desktop installer
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "WhatsApp", "WhatsApp.exe"),
            # Microsoft Store version (WindowsApps)
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Microsoft", "WindowsApps", "WhatsApp.exe"),
            # Older Microsoft Store path
            os.path.join(os.environ.get("PROGRAMFILES", ""),
                         "WindowsApps", "WhatsApp.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                return _launch(p)
        return _open_url("https://web.whatsapp.com")
    elif OS == "Darwin":
        try:
            subprocess.Popen(["open", "-a", "WhatsApp"])
        except Exception:
            return _open_url("https://web.whatsapp.com")
    else:
        return _open_url("https://web.whatsapp.com")
    return True


def open_vscode():
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""),
                         "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "") or
                         os.environ.get("PROGRAMFILES", ""),
                         "Microsoft VS Code", "Code.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                return _launch(p)
        # Fallback: 'code' command (works if VS Code added to PATH)
        try:
            subprocess.Popen(["code"])
            return True
        except FileNotFoundError:
            pass
        os.system("code")
    elif OS == "Darwin":
        try:
            subprocess.Popen(["open", "-a", "Visual Studio Code"])
        except Exception:
            subprocess.Popen(["code"])
    else:
        subprocess.Popen(["code"])
    return True


def open_excel():
    if OS == "Windows":
        return _win_open_office("EXCEL.EXE", "excel")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft Excel"])
    else:
        subprocess.Popen(["libreoffice", "--calc"])
    return True


def open_word():
    if OS == "Windows":
        return _win_open_office("WINWORD.EXE", "winword")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft Word"])
    else:
        subprocess.Popen(["libreoffice", "--writer"])
    return True


def open_powerpoint():
    if OS == "Windows":
        return _win_open_office("POWERPNT.EXE", "powerpnt")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft PowerPoint"])
    else:
        subprocess.Popen(["libreoffice", "--impress"])
    return True


# ═════════════════════════════════════════════════════════════
# Intent → handler dispatch table
# ═════════════════════════════════════════════════════════════

INTENT_HANDLERS = {
    # Core
    "open_browser":       (open_browser,       "Opening your browser."),
    "open_calculator":    (open_calculator,    "Opening Calculator."),
    "open_file_explorer": (open_file_explorer, "Opening File Explorer."),
    "open_notepad":       (open_notepad,       "Opening Notepad."),
    "open_task_manager":  (open_task_manager,  "Opening Task Manager."),
    "close_app":          (close_app,          "Closing the active application."),
    "shutdown":           (shutdown,           "Shutting down in 5 seconds."),
    "restart":            (restart,            "Restarting in 5 seconds."),
    "volume_up":          (volume_up,          "Increasing the volume."),
    "volume_down":        (volume_down,        "Decreasing the volume."),
    "mute":               (mute,               "Toggling mute."),
    "take_screenshot":    (take_screenshot,    "Taking a screenshot."),
    "greet":              (greet,              "Hello! I am your voice assistant. Say a command or ask what I can do."),
    # Web & Search
    "search_google":      (search_google,      "Opening Google."),
    "open_youtube":       (open_youtube,       "Opening YouTube."),
    "open_gmail":         (open_gmail,         "Opening Gmail."),
    # File & Folder
    "open_downloads":     (open_downloads,     "Opening your Downloads folder."),
    "open_desktop":       (open_desktop,       "Opening Desktop."),
    "create_folder":      (create_folder,      "Creating a new folder on your Desktop."),
    # Apps
    "open_spotify":       (open_spotify,       "Opening Spotify."),
    "open_whatsapp":      (open_whatsapp,      "Opening WhatsApp."),
    "open_vscode":        (open_vscode,        "Opening Visual Studio Code."),
    "open_excel":         (open_excel,         "Opening Microsoft Excel."),
    "open_word":          (open_word,          "Opening Microsoft Word."),
    "open_powerpoint":    (open_powerpoint,    "Opening Microsoft PowerPoint."),
}


def execute(intent: str) -> str:
    if intent in INTENT_HANDLERS:
        handler, response = INTENT_HANDLERS[intent]
        success = handler()
        return response if success else f"Sorry, I could not complete '{intent}'."
    return f"I don't know how to handle '{intent}' yet."