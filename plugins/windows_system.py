"""
plugins/windows_system.py
Windows/OS controls and settings functionality.
"""
import os
import datetime
import subprocess
from . import register_intent
from .utils import OS, open_folder

@register_intent("take_screenshot", "Taking a screenshot.", is_dynamic=True)
def take_screenshot(**kw):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(os.path.expanduser("~"), "Pictures", f"screenshot_{timestamp}.png")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    success = False

    if OS == "Windows":
        try:
            import pyautogui
            pyautogui.screenshot(filepath)
            success = True
        except Exception: pass
            
        if not success:
            try:
                from PIL import ImageGrab
                ImageGrab.grab().save(filepath)
                success = True
            except Exception: pass
            
    elif OS == "Darwin":
        try:
            subprocess.call(["screencapture", "-x", filepath])
            success = True
        except Exception: pass
        
    else:
        try:
            subprocess.call(["scrot", "-m", filepath])
            success = True
        except FileNotFoundError:
            try:
                from PIL import ImageGrab
                ImageGrab.grab(all_screens=True).save(filepath)
                success = True
            except Exception: pass

    if success:
        return f"Screenshot saved to {filepath}"
    return False

@register_intent("open_file_explorer", "Opening File Explorer.")
def open_file_explorer(**kw):
    if OS == "Windows": subprocess.Popen(["explorer"])
    elif OS == "Darwin": subprocess.Popen(["open", os.path.expanduser("~")])
    else: subprocess.Popen(["xdg-open", os.path.expanduser("~")])
    return True

@register_intent("open_downloads", "Opening your Downloads folder.")
def open_downloads(**kw):
    return open_folder(os.path.join(os.path.expanduser("~"), "Downloads"))

@register_intent("open_desktop", "Opening Desktop.")
def open_desktop(**kw):
    return open_folder(os.path.join(os.path.expanduser("~"), "Desktop"))

@register_intent("create_folder", "Creating a new folder on your Desktop.")
def create_folder(**kw):
    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop     = os.path.join(os.path.expanduser("~"), "Desktop")
    new_folder  = os.path.join(desktop, f"New_Folder_{timestamp}")
    try:
        os.makedirs(new_folder, exist_ok=True)
        return open_folder(desktop)
    except Exception: return False

@register_intent("open_folder_path", "Opening folder.", is_parameterised=True, is_dynamic=True)
def open_folder_path(params=None, **kw):
    path = (params or {}).get("path", "")
    folder_name = (params or {}).get("folder_name", "")
    if path and os.path.isdir(path):
        open_folder(path)
        return f"Opening your {folder_name or 'requested'} folder."
    if folder_name:
        path = os.path.join(os.path.expanduser("~"), folder_name)
        if os.path.isdir(path):
            open_folder(path)
            return f"Opening your {folder_name} folder."
    open_folder(os.path.expanduser("~"))
    return "Opening your home folder."

@register_intent("shutdown", "Shutting down in 5 seconds.")
def shutdown(**kw):
    if OS == "Windows": subprocess.Popen(["shutdown", "/s", "/t", "5"])
    else: subprocess.call(["sudo", "shutdown", "-h", "now"])
    return True

@register_intent("restart", "Restarting in 5 seconds.")
def restart(**kw):
    if OS == "Windows": subprocess.Popen(["shutdown", "/r", "/t", "5"])
    elif OS == "Darwin": subprocess.call(["sudo", "shutdown", "-r", "now"])
    else: subprocess.call(["sudo", "reboot"])
    return True

@register_intent("open_settings", "Opening Settings.")
def open_settings(**kw):
    if OS == "Windows": subprocess.Popen(["cmd", "/c", "start", "ms-settings:"])
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "System Preferences"])
    else:
        for app in ["gnome-control-center", "xfce4-settings-manager"]:
            try:
                subprocess.Popen([app])
                return True
            except FileNotFoundError: continue
    return True

@register_intent("lock_screen", "Locking the screen.")
def lock_screen(**kw):
    if OS == "Windows": subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif OS == "Darwin": subprocess.call(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
    else:
        try: subprocess.call(["xdg-screensaver", "lock"])
        except FileNotFoundError: subprocess.call(["gnome-screensaver-command", "-l"])
    return True

@register_intent("empty_recycle_bin", "Emptying the Recycle Bin.")
def empty_recycle_bin(**kw):
    if OS == "Windows":
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], capture_output=True, timeout=15)
        except Exception: return False
    elif OS == "Darwin": subprocess.call(["osascript", "-e", 'tell application "Finder" to empty the trash'])
    else:
        import shutil
        trash = os.path.expanduser("~/.local/share/Trash")
        if os.path.exists(trash): shutil.rmtree(trash, ignore_errors=True)
    return True

@register_intent("open_cmd", "Opening Command Prompt.")
def open_cmd(**kw):
    if OS == "Windows": subprocess.Popen(["cmd", "/c", "start", "cmd"])
    elif OS == "Darwin": subprocess.Popen(["open", "-a", "Terminal"])
    else:
        for term in ["gnome-terminal", "xfce4-terminal", "konsole", "xterm"]:
            try:
                subprocess.Popen([term])
                return True
            except FileNotFoundError: continue
    return True

@register_intent("greet", "Hello! I'm your voice assistant. I can open apps, search the web, tell you the time, check your battery, and much more. Just ask!")
def greet(**kw):
    return True
