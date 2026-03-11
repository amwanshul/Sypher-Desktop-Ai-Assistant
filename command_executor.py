"""
command_executor.py  v5
All commands audited and fixed for Windows.
New in v5:
- search_web        : parameterised Google search (opens browser with query)
- search_youtube    : parameterised YouTube search (opens browser with query)
- get_time          : returns current time string
- get_date          : returns current date string
- get_battery       : returns battery percentage
- get_ip_address    : returns local IP address
- open_settings     : opens Windows Settings
- lock_screen       : locks the workstation
- empty_recycle_bin : empties the Recycle Bin
- open_cmd          : opens Command Prompt / terminal
- open_folder_path  : opens a specific named folder
- execute() now accepts optional params dict for slot-filled intents
"""

import os
import platform
import subprocess
import datetime
import time
import socket
import json
from urllib.parse import quote_plus

OS = platform.system()   # "Windows" | "Darwin" | "Linux"
_DYNAMIC_COMMANDS_PATH = os.path.join(os.path.dirname(__file__), "dynamic_commands.json")


# ─────────────────────────────────────────────────────────────
# Dynamic Commands (LLM Zero-Shot)
# ─────────────────────────────────────────────────────────────

def get_dynamic_commands() -> dict:
    if not os.path.exists(_DYNAMIC_COMMANDS_PATH):
        return {}
    try:
        with open(_DYNAMIC_COMMANDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Executor] Error loading dynamic commands: {e}")
        return {}

def save_dynamic_command(intent: str, os_command: str):
    cmds = get_dynamic_commands()
    cmds[intent] = os_command
    try:
        with open(_DYNAMIC_COMMANDS_PATH, "w", encoding="utf-8") as f:
            json.dump(cmds, f, indent=4)
        print(f"[Executor] Saved dynamic command: '{intent}' -> '{os_command}'")
    except Exception as e:
        print(f"[Executor] Error saving dynamic command: {e}")


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _open_url(url: str) -> bool:
    """Open a URL in the system default browser."""
    try:
        if OS == "Windows":
            subprocess.Popen(["cmd", "/c", "start", "", url])
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
            subprocess.Popen(["explorer", path])
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
    subprocess.Popen(["cmd", "/c", "start", fallback_cmd])
    return True


# ─────────────────────────────────────────────────────────────
# Windows volume / mute
# ─────────────────────────────────────────────────────────────
def _win_send_vk(code: int):
    subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"$wsh = New-Object -ComObject WScript.Shell; "
         f"$wsh.SendKeys([char]{code})"],
        capture_output=True, timeout=10
    )


def _win_volume_up():
    for _ in range(5):
        _win_send_vk(175)
        time.sleep(0.04)


def _win_volume_down():
    for _ in range(5):
        _win_send_vk(174)
        time.sleep(0.04)


def _win_mute():
    _win_send_vk(173)


# ─────────────────────────────────────────────────────────────
# Windows screenshot
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
# ─────────────────────────────────────────────────────────────
_WIN_CLOSE_PRIORITY = [
    "chrome.exe",
    "firefox.exe",
    "msedge.exe",
    "notepad.exe",
    "notepad++.exe",
    "Code.exe",
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
    "ApplicationFrameHost.exe",
]

# Map user-friendly app names to process names
_APP_NAME_MAP = {
    "chrome":      "chrome.exe",
    "firefox":     "firefox.exe",
    "edge":        "msedge.exe",
    "browser":     "msedge.exe",
    "notepad":     "notepad.exe",
    "vs code":     "Code.exe",
    "vscode":      "Code.exe",
    "code":        "Code.exe",
    "excel":       "EXCEL.EXE",
    "word":        "WINWORD.EXE",
    "powerpoint":  "POWERPNT.EXE",
    "spotify":     "Spotify.exe",
    "whatsapp":    "WhatsApp.exe",
    "telegram":    "Telegram.exe",
    "discord":     "Discord.exe",
    "zoom":        "Zoom.exe",
    "teams":       "Teams.exe",
    "vlc":         "vlc.exe",
    "paint":       "mspaint.exe",
    "calculator":  "calculator.exe",
}


def _get_running_procs_windows() -> set:
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


def _close_app_windows(params: dict = None) -> bool:
    # If a specific app was named, try that first
    if params and params.get("app_name"):
        app = params["app_name"].lower()
        exe = _APP_NAME_MAP.get(app)
        if exe:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
            print(f"[Executor] Closed {exe}")
            return True
    # Fallback: close the highest-priority running app
    running = _get_running_procs_windows()
    for exe in _WIN_CLOSE_PRIORITY:
        if exe.lower() in running:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
            print(f"[Executor] Closed {exe}")
            return True
    print("[Executor] No recognised closeable app found running.")
    return False


# ═════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═════════════════════════════════════════════════════════════

def open_browser(**kw):
    return _open_url("https://www.google.com")


def open_calculator(**kw):
    if OS == "Windows":
        subprocess.Popen(["calc"])
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Calculator"])
    else:
        subprocess.Popen(["gnome-calculator"])
    return True


def open_file_explorer(**kw):
    if OS == "Windows":
        subprocess.Popen(["explorer"])
    elif OS == "Darwin":
        subprocess.Popen(["open", os.path.expanduser("~")])
    else:
        subprocess.Popen(["xdg-open", os.path.expanduser("~")])
    return True


def open_notepad(**kw):
    if OS == "Windows":
        subprocess.Popen(["notepad"])
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


def open_task_manager(**kw):
    if OS == "Windows":
        subprocess.Popen(["taskmgr"])
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


def close_app(params=None, **kw):
    if OS == "Windows":
        return _close_app_windows(params)
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


def shutdown(**kw):
    if OS == "Windows":
        subprocess.Popen(["shutdown", "/s", "/t", "5"])
    else:
        subprocess.call(["sudo", "shutdown", "-h", "now"])
    return True


def restart(**kw):
    if OS == "Windows":
        subprocess.Popen(["shutdown", "/r", "/t", "5"])
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-r", "now"])
    else:
        subprocess.call(["sudo", "reboot"])
    return True


def volume_up(**kw):
    if OS == "Windows":
        _win_volume_up()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e",
            "set volume output volume (output volume of (get volume settings) + 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    return True


def volume_down(**kw):
    if OS == "Windows":
        _win_volume_down()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e",
            "set volume output volume (output volume of (get volume settings) - 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    return True


def mute(**kw):
    if OS == "Windows":
        _win_mute()
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output muted true"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
    return True


def take_screenshot(**kw):
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


def greet(**kw):
    return True


# ── Web & Search (parameterised) ─────────────────────────────

def search_google(**kw):
    return _open_url("https://www.google.com")


def search_web(params=None, **kw):
    """Open Google search with an extracted query."""
    query = (params or {}).get("query", "")
    if query:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        _open_url(url)
        return True
    # Fallback: just open Google
    return _open_url("https://www.google.com")


def search_youtube(params=None, **kw):
    """Open YouTube search with an extracted query."""
    query = (params or {}).get("query", "")
    if query:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        _open_url(url)
        return True
    # Fallback: just open YouTube
    return _open_url("https://www.youtube.com")


def open_youtube(**kw):
    return _open_url("https://www.youtube.com")


def open_gmail(**kw):
    return _open_url("https://mail.google.com")


# ── File & Folder ─────────────────────────────────────────────

def open_downloads(**kw):
    path = os.path.join(os.path.expanduser("~"), "Downloads")
    return _open_folder(path)


def open_desktop(**kw):
    path = os.path.join(os.path.expanduser("~"), "Desktop")
    return _open_folder(path)


def create_folder(**kw):
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


def open_folder_path(params=None, **kw):
    """Open a specific folder by extracted path."""
    path = (params or {}).get("path", "")
    folder_name = (params or {}).get("folder_name", "")
    if path and os.path.isdir(path):
        _open_folder(path)
        return True
    if folder_name:
        # Try constructing path
        path = os.path.join(os.path.expanduser("~"), folder_name)
        if os.path.isdir(path):
            _open_folder(path)
            return True
    # Fallback: open home
    _open_folder(os.path.expanduser("~"))
    return True


# ── Apps ──────────────────────────────────────────────────────

def open_spotify(**kw):
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


def open_whatsapp(**kw):
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "WhatsApp", "WhatsApp.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Microsoft", "WindowsApps", "WhatsApp.exe"),
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


def open_vscode(**kw):
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
        try:
            subprocess.Popen(["code"])
            return True
        except FileNotFoundError:
            pass
        subprocess.Popen(["code"], shell=True)
    elif OS == "Darwin":
        try:
            subprocess.Popen(["open", "-a", "Visual Studio Code"])
        except Exception:
            subprocess.Popen(["code"])
    else:
        subprocess.Popen(["code"])
    return True


def open_excel(**kw):
    if OS == "Windows":
        return _win_open_office("EXCEL.EXE", "excel")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft Excel"])
    else:
        subprocess.Popen(["libreoffice", "--calc"])
    return True


def open_word(**kw):
    if OS == "Windows":
        return _win_open_office("WINWORD.EXE", "winword")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft Word"])
    else:
        subprocess.Popen(["libreoffice", "--writer"])
    return True


def open_powerpoint(**kw):
    if OS == "Windows":
        return _win_open_office("POWERPNT.EXE", "powerpnt")
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft PowerPoint"])
    else:
        subprocess.Popen(["libreoffice", "--impress"])
    return True


# ═════════════════════════════════════════════════════════════
# NEW: System / Internal-task handlers
# ═════════════════════════════════════════════════════════════

def get_time(**kw):
    """Return the current time as a readable string (no side-effects)."""
    return True   # response is dynamic, see INTENT_HANDLERS


def get_date(**kw):
    return True


def get_battery(**kw):
    return True


def get_ip_address(**kw):
    return True


def open_settings(**kw):
    if OS == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "ms-settings:"])
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "System Preferences"])
    else:
        for app in ["gnome-control-center", "xfce4-settings-manager"]:
            try:
                subprocess.Popen([app])
                return True
            except FileNotFoundError:
                continue
    return True


def lock_screen(**kw):
    if OS == "Windows":
        subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif OS == "Darwin":
        subprocess.call(["/System/Library/CoreServices/Menu Extras"
                         "/User.menu/Contents/Resources/CGSession", "-suspend"])
    else:
        try:
            subprocess.call(["xdg-screensaver", "lock"])
        except FileNotFoundError:
            subprocess.call(["gnome-screensaver-command", "-l"])
    return True


def empty_recycle_bin(**kw):
    if OS == "Windows":
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                capture_output=True, timeout=15
            )
        except Exception as e:
            print(f"[Executor] empty_recycle_bin error: {e}")
            return False
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e",
            'tell application "Finder" to empty the trash'])
    else:
        import shutil
        trash = os.path.expanduser("~/.local/share/Trash")
        if os.path.exists(trash):
            shutil.rmtree(trash, ignore_errors=True)
    return True


def open_cmd(**kw):
    if OS == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "cmd"])
    elif OS == "Darwin":
        subprocess.Popen(["open", "-a", "Terminal"])
    else:
        for term in ["gnome-terminal", "xfce4-terminal", "konsole", "xterm"]:
            try:
                subprocess.Popen([term])
                return True
            except FileNotFoundError:
                continue
    return True


# ═════════════════════════════════════════════════════════════
# Dynamic response builders (for intents returning info)
# ═════════════════════════════════════════════════════════════

def _build_dynamic_response(intent: str, params: dict) -> str | None:
    """Build a text response for informational intents."""
    if intent == "get_time":
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."

    if intent == "get_date":
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    if intent == "get_battery":
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                pct = battery.percent
                plug = "plugged in" if battery.power_plugged else "on battery"
                return f"Battery is at {pct:.0f}% ({plug})."
            return "Could not read battery info."
        except ImportError:
            # Fallback: PowerShell
            if OS == "Windows":
                try:
                    r = subprocess.run(
                        ["powershell", "-NoProfile", "-Command",
                         "(Get-WmiObject Win32_Battery).EstimatedChargeRemaining"],
                        capture_output=True, text=True, timeout=10
                    )
                    pct = r.stdout.strip()
                    if pct.isdigit():
                        return f"Battery is at {pct}%."
                except Exception:
                    pass
            return "Could not read battery (install psutil for best results)."

    if intent == "get_ip_address":
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"Your local IP address is {ip}."
        except Exception:
            return "Could not determine your IP address."

    if intent == "search_web":
        query = (params or {}).get("query", "")
        if query:
            return f"Searching the web for '{query}'."
        return "Opening Google."

    if intent == "search_youtube":
        query = (params or {}).get("query", "")
        if query:
            return f"Searching YouTube for '{query}'."
        return "Opening YouTube."

    if intent == "open_folder_path":
        folder = (params or {}).get("folder_name", "")
        if folder:
            return f"Opening your {folder} folder."
        return "Opening your home folder."

    if intent == "close_app":
        app = (params or {}).get("app_name", "")
        if app:
            return f"Closing {app}."
        return "Closing the active application."

    return None


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
    "mute":               (mute,              "Toggling mute."),
    "take_screenshot":    (take_screenshot,    "Taking a screenshot."),
    "greet":              (greet,              "Hello! I'm your voice assistant. "
                                               "I can open apps, search the web, "
                                               "tell you the time, check your battery, "
                                               "and much more. Just ask!"),
    # Web & Search
    "search_google":      (search_google,      "Opening Google."),
    "search_web":         (search_web,         "Searching the web."),
    "search_youtube":     (search_youtube,     "Searching YouTube."),
    "open_youtube":       (open_youtube,       "Opening YouTube."),
    "open_gmail":         (open_gmail,         "Opening Gmail."),
    # File & Folder
    "open_downloads":     (open_downloads,     "Opening your Downloads folder."),
    "open_desktop":       (open_desktop,       "Opening Desktop."),
    "create_folder":      (create_folder,      "Creating a new folder on your Desktop."),
    "open_folder_path":   (open_folder_path,   "Opening folder."),
    # Apps
    "open_spotify":       (open_spotify,       "Opening Spotify."),
    "open_whatsapp":      (open_whatsapp,      "Opening WhatsApp."),
    "open_vscode":        (open_vscode,        "Opening Visual Studio Code."),
    "open_excel":         (open_excel,         "Opening Microsoft Excel."),
    "open_word":          (open_word,          "Opening Microsoft Word."),
    "open_powerpoint":    (open_powerpoint,    "Opening Microsoft PowerPoint."),
    # System / Internal
    "get_time":           (get_time,           "Checking the time."),
    "get_date":           (get_date,           "Checking the date."),
    "get_battery":        (get_battery,        "Checking battery status."),
    "get_ip_address":     (get_ip_address,     "Checking your IP address."),
    "open_settings":      (open_settings,      "Opening Settings."),
    "lock_screen":        (lock_screen,        "Locking the screen."),
    "empty_recycle_bin":   (empty_recycle_bin,  "Emptying the Recycle Bin."),
    "open_cmd":           (open_cmd,           "Opening Command Prompt."),
}


# Intents that accept params from slot extraction
_PARAMETERISED_INTENTS = {
    "search_web", "search_youtube", "open_folder_path", "close_app",
}

# Intents that produce dynamic text responses
_DYNAMIC_INTENTS = {
    "get_time", "get_date", "get_battery", "get_ip_address",
    "search_web", "search_youtube", "open_folder_path", "close_app",
}


def execute(intent: str, params: dict = None) -> str:
    """
    Dispatch an intent to its handler and return a response string.
    Supports parameterised intents via the optional `params` dict.
    If the intent is a known dynamic command, runs it zero-shot.
    """
    if intent not in INTENT_HANDLERS:
        # Check dynamic commands (LLM-synthesised zero-shot intents)
        dyn_cmds = get_dynamic_commands()
        if intent in dyn_cmds:
            os_cmd = dyn_cmds[intent]
            try:
                subprocess.Popen(os_cmd, shell=True)
                return f"Executing dynamic command: {intent.replace('_', ' ')}"
            except Exception as e:
                return f"Failed to execute dynamic command: {e}"
                
        return f"I don't know how to handle '{intent}' yet."

    handler, default_response = INTENT_HANDLERS[intent]

    # Call handler (pass params if it's a parameterised intent)
    if intent in _PARAMETERISED_INTENTS:
        success = handler(params=params)
    else:
        success = handler()

    if not success:
        return f"Sorry, I could not complete '{intent}'."

    # Use dynamic response if available
    if intent in _DYNAMIC_INTENTS:
        dynamic = _build_dynamic_response(intent, params)
        if dynamic:
            return dynamic

    return default_response