"""
plugins/applications.py
Handles launching and closing applications (e.g., Office, VS Code, Calculator).
"""
import os
import subprocess
from . import register_intent
from .utils import OS, open_url, launch

# ─────────────────────────────────────────────────────────────
# Office helpers
# ─────────────────────────────────────────────────────────────
def _win_find_office_exe(exe_name: str) -> str | None:
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
        return launch(path)
    subprocess.Popen(["cmd", "/c", "start", fallback_cmd])
    return True

# ─────────────────────────────────────────────────────────────
# Close app helpers
# ─────────────────────────────────────────────────────────────
_WIN_CLOSE_PRIORITY = [
    "chrome.exe", "firefox.exe", "msedge.exe", "notepad.exe", "notepad++.exe",
    "Code.exe", "EXCEL.EXE", "WINWORD.EXE", "POWERPNT.EXE", "Spotify.exe",
    "WhatsApp.exe", "Telegram.exe", "Discord.exe", "Zoom.exe", "Teams.exe",
    "vlc.exe", "mspaint.exe", "calculator.exe", "ApplicationFrameHost.exe",
]

_APP_NAME_MAP = {
    "chrome": "chrome.exe", "firefox": "firefox.exe", "edge": "msedge.exe", "browser": "msedge.exe",
    "notepad": "notepad.exe", "vs code": "Code.exe", "vscode": "Code.exe", "code": "Code.exe",
    "excel": "EXCEL.EXE", "word": "WINWORD.EXE", "powerpoint": "POWERPNT.EXE",
    "spotify": "Spotify.exe", "whatsapp": "WhatsApp.exe", "telegram": "Telegram.exe",
    "discord": "Discord.exe", "zoom": "Zoom.exe", "teams": "Teams.exe",
    "vlc": "vlc.exe", "paint": "mspaint.exe", "calculator": "calculator.exe",
}

def _get_running_procs_windows() -> set:
    try:
        result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=5)
        procs = set()
        for line in result.stdout.strip().splitlines():
            parts = line.strip('"').split('","')
            if parts: procs.add(parts[0].lower())
        return procs
    except Exception:
        return set()

def _close_app_windows(params: dict = None) -> bool:
    if params and params.get("app_name"):
        app = params["app_name"].lower()
        exe = _APP_NAME_MAP.get(app)
        if exe:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
            return True
    running = _get_running_procs_windows()
    for exe in _WIN_CLOSE_PRIORITY:
        if exe.lower() in running:
            subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True)
            return True
    return False

# ─────────────────────────────────────────────────────────────
# Application Intents
# ─────────────────────────────────────────────────────────────

@register_intent("open_calculator", "Opening Calculator.")
def open_calculator(**kw):
    if OS == "Windows": subprocess.Popen(["calc"])
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Calculator"])
    else: subprocess.Popen(["gnome-calculator"])
    return True

@register_intent("open_task_manager", "Opening Task Manager.")
def open_task_manager(**kw):
    if OS == "Windows": subprocess.Popen(["taskmgr"])
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Activity Monitor"])
    else:
        for app in ["gnome-system-monitor", "xfce4-taskmanager", "ksysguard"]:
            try:
                subprocess.Popen([app])
                return True
            except FileNotFoundError: continue
    return True

@register_intent("open_notepad", "Opening Notepad.")
def open_notepad(**kw):
    if OS == "Windows": subprocess.Popen(["notepad"])
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "TextEdit"])
    else:
        for editor in ["gedit", "mousepad", "xed", "kate", "nano"]:
            try:
                subprocess.Popen([editor])
                return True
            except FileNotFoundError: continue
    return True

@register_intent("open_spotify", "Opening Spotify.")
def open_spotify(**kw):
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("APPDATA", ""), "Spotify", "Spotify.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "Spotify.exe"),
        ]
        for p in paths:
            if os.path.exists(p): return launch(p)
        return open_url("https://open.spotify.com")
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Spotify"])
    else:
        try: subprocess.Popen(["spotify"])
        except FileNotFoundError: return open_url("https://open.spotify.com")
    return True

@register_intent("open_whatsapp", "Opening WhatsApp.")
def open_whatsapp(**kw):
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "WhatsApp", "WhatsApp.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "WhatsApp.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "WindowsApps", "WhatsApp.exe"),
        ]
        for p in paths:
            if os.path.exists(p): return launch(p)
        return open_url("https://web.whatsapp.com")
    elif OS == "Darwin":
        try: subprocess.Popen(["open", "-a", "WhatsApp"])
        except Exception: return open_url("https://web.whatsapp.com")
    else: return open_url("https://web.whatsapp.com")
    return True

@register_intent("open_vscode", "Opening Visual Studio Code.")
def open_vscode(**kw):
    if OS == "Windows":
        paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "") or os.environ.get("PROGRAMFILES", ""), "Microsoft VS Code", "Code.exe"),
        ]
        for p in paths:
            if os.path.exists(p): return launch(p)
        try:
            subprocess.Popen(["code"])
            return True
        except FileNotFoundError: pass
        subprocess.Popen(["code"], shell=True)
    elif OS == "Darwin":
        try: subprocess.Popen(["open", "-a", "Visual Studio Code"])
        except Exception: subprocess.Popen(["code"])
    else: subprocess.Popen(["code"])
    return True

@register_intent("open_excel", "Opening Microsoft Excel.")
def open_excel(**kw):
    if OS == "Windows": return _win_open_office("EXCEL.EXE", "excel")
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Microsoft Excel"])
    else: subprocess.Popen(["libreoffice", "--calc"])
    return True

@register_intent("open_word", "Opening Microsoft Word.")
def open_word(**kw):
    if OS == "Windows": return _win_open_office("WINWORD.EXE", "winword")
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Microsoft Word"])
    else: subprocess.Popen(["libreoffice", "--writer"])
    return True

@register_intent("open_powerpoint", "Opening Microsoft PowerPoint.")
def open_powerpoint(**kw):
    if OS == "Windows": return _win_open_office("POWERPNT.EXE", "powerpnt")
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Microsoft PowerPoint"])
    else: subprocess.Popen(["libreoffice", "--impress"])
    return True

@register_intent("close_app", "Closing the active application.", is_parameterised=True, is_dynamic=True)
def close_app(params=None, **kw):
    app = (params or {}).get("app_name", "")
    
    if OS == "Windows": 
        success = _close_app_windows(params)
    elif OS == "Darwin":
        try:
            script = 'tell application "System Events" to set frontApp to name of first application process whose frontmost is true; tell application frontApp to quit'
            subprocess.call(["osascript", "-e", script])
            success = True
        except Exception as e: success = False
    else:
        try:
            subprocess.call(["xdotool", "getactivewindow", "windowclose"])
            success = True
        except FileNotFoundError:
            subprocess.call(["pkill", "-f", "chrome"])
            success = True
            
    if success:
        return f"Closing {app}." if app else "Closing the active application."
    return False
