"""
command_executor.py
Maps predicted intents to OS-level actions.
Supports Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
import datetime


OS = platform.system()   # "Windows" | "Darwin" | "Linux"


# ──────────────────────────────────────────────
# Helper: open apps cross-platform
# ──────────────────────────────────────────────
def _open(win_cmd: list, mac_cmd: list, lin_cmd: list):
    try:
        if OS == "Windows":
            subprocess.Popen(win_cmd, shell=True)
        elif OS == "Darwin":
            subprocess.Popen(mac_cmd)
        else:
            subprocess.Popen(lin_cmd)
        return True
    except Exception as e:
        print(f"[Executor] Error: {e}")
        return False


# ──────────────────────────────────────────────
# Individual command handlers
# ──────────────────────────────────────────────
def open_browser():
    return _open(
        win_cmd=["start", "chrome"],
        mac_cmd=["open", "-a", "Google Chrome"],
        lin_cmd=["xdg-open", "https://www.google.com"],
    )


def open_calculator():
    return _open(
        win_cmd=["calc"],
        mac_cmd=["open", "-a", "Calculator"],
        lin_cmd=["gnome-calculator"],
    )


def open_file_explorer():
    return _open(
        win_cmd=["explorer"],
        mac_cmd=["open", os.path.expanduser("~")],
        lin_cmd=["nautilus", os.path.expanduser("~")],
    )


def open_notepad():
    return _open(
        win_cmd=["notepad"],
        mac_cmd=["open", "-a", "TextEdit"],
        lin_cmd=["gedit"],
    )


def open_task_manager():
    return _open(
        win_cmd=["taskmgr"],
        mac_cmd=["open", "-a", "Activity Monitor"],
        lin_cmd=["gnome-system-monitor"],
    )


def close_app():
    if OS == "Windows":
        subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"], shell=True)
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", 'quit app "Google Chrome"'])
    else:
        subprocess.call(["pkill", "-f", "chrome"])
    return True


def shutdown():
    if OS == "Windows":
        subprocess.call(["shutdown", "/s", "/t", "5"], shell=True)
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-h", "now"])
    else:
        subprocess.call(["sudo", "shutdown", "-h", "now"])
    return True


def restart():
    if OS == "Windows":
        subprocess.call(["shutdown", "/r", "/t", "5"], shell=True)
    elif OS == "Darwin":
        subprocess.call(["sudo", "shutdown", "-r", "now"])
    else:
        subprocess.call(["sudo", "reboot"])
    return True


def volume_up():
    if OS == "Windows":
        # Uses nircmd if available; otherwise uses PowerShell
        try:
            subprocess.call(["nircmd", "changesysvolume", "5000"])
        except FileNotFoundError:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.10), None)
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
    return True


def volume_down():
    if OS == "Windows":
        try:
            subprocess.call(["nircmd", "changesysvolume", "-5000"])
        except FileNotFoundError:
            pass
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
    return True


def mute():
    if OS == "Windows":
        try:
            subprocess.call(["nircmd", "mutesysvolume", "2"])
        except FileNotFoundError:
            pass
    elif OS == "Darwin":
        subprocess.call(["osascript", "-e", "set volume output muted true"])
    else:
        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
    return True


def take_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(os.path.expanduser("~"), f"screenshot_{timestamp}.png")
    try:
        import pyautogui
        pyautogui.screenshot(filename)
        print(f"[Executor] Screenshot saved → {filename}")
        return True
    except ImportError:
        if OS == "Darwin":
            subprocess.call(["screencapture", filename])
            return True
        elif OS == "Linux":
            subprocess.call(["scrot", filename])
            return True
    return False


def greet():
    # No system action; voice feedback handled by assistant
    return True


# ──────────────────────────────────────────────
# Intent → handler dispatch table
# ──────────────────────────────────────────────
INTENT_HANDLERS = {
    "open_browser":      (open_browser,      "Opening the browser for you."),
    "open_calculator":   (open_calculator,   "Opening Calculator."),
    "open_file_explorer":(open_file_explorer,"Opening File Explorer."),
    "open_notepad":      (open_notepad,      "Opening Notepad."),
    "open_task_manager": (open_task_manager, "Opening Task Manager."),
    "close_app":         (close_app,         "Closing the application."),
    "shutdown":          (shutdown,          "Shutting down the system in 5 seconds."),
    "restart":           (restart,           "Restarting the system in 5 seconds."),
    "volume_up":         (volume_up,         "Increasing the volume."),
    "volume_down":       (volume_down,       "Decreasing the volume."),
    "mute":              (mute,              "Muting the sound."),
    "take_screenshot":   (take_screenshot,   "Taking a screenshot."),
    "greet":             (greet,             "Hello! I am your voice assistant. How can I help you?"),
}


def execute(intent: str) -> str:
    """Run the handler for *intent* and return the speech response string."""
    if intent in INTENT_HANDLERS:
        handler, response = INTENT_HANDLERS[intent]
        success = handler()
        return response if success else f"Sorry, I could not complete the action for '{intent}'."
    return f"I don't know how to handle the intent '{intent}' yet."
